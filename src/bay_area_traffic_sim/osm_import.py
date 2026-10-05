"""Import a checked-in OSM extract into a SUMO network for manual audit."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bay_area_traffic_sim.sumo_install import binary
from bay_area_traffic_sim.toy_corridor import repository_root

OVERPASS_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)


@dataclass(frozen=True)
class CorridorConfig:
    """The saved boundary and source location for one real-road import."""

    name: str
    bounding_box: dict[str, float]
    osm_source_path: Path
    edge_patch_path: Path | None = None
    connection_patch_path: Path | None = None


def load_corridor_config(config_path: Path) -> CorridorConfig:
    """Load import metadata without silently downloading map data."""

    raw = json.loads(config_path.read_text())
    root = repository_root()
    source_path = root / raw["osm_source_path"]
    edge_patch = raw.get("edge_patch_path")
    connection_patch = raw.get("connection_patch_path")
    if bool(edge_patch) != bool(connection_patch):
        raise ValueError("Both edge_patch_path and connection_patch_path are required together.")
    return CorridorConfig(
        name=raw["name"],
        bounding_box=raw["bounding_box"],
        osm_source_path=source_path,
        edge_patch_path=root / edge_patch if edge_patch else None,
        connection_patch_path=root / connection_patch if connection_patch else None,
    )


def road_query(bounding_box: dict[str, float]) -> str:
    """Build a deliberately narrow Overpass query for road geometry."""

    south, west = bounding_box["south"], bounding_box["west"]
    north, east = bounding_box["north"], bounding_box["east"]
    return f"""[out:xml][timeout:60];
way["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link"]({south},{west},{north},{east});
(._;>;);
out body;"""


def download_osm(config_path: Path) -> tuple[Path, Path]:
    """Download a timestamped public road extract and write its provenance."""

    config = load_corridor_config(config_path)
    query = road_query(config.bounding_box)
    payload: bytes | None = None
    source_url: str | None = None
    errors: list[str] = []
    for endpoint in OVERPASS_ENDPOINTS:
        request = Request(
            endpoint,
            data=urlencode({"data": query}).encode(),
            headers={"User-Agent": "bay-area-traffic-sim-local-research/0.1"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read()
                source_url = endpoint
                break
        except (HTTPError, URLError, TimeoutError) as error:
            errors.append(f"{endpoint}: {error}")
    if payload is None or source_url is None:
        raise RuntimeError("OSM download failed: " + "; ".join(errors))
    if not payload.startswith(b"<?xml"):
        raise RuntimeError("Overpass did not return OSM XML; the source file was not written.")

    config.osm_source_path.parent.mkdir(parents=True, exist_ok=True)
    config.osm_source_path.write_bytes(payload)
    provenance_path = config.osm_source_path.with_suffix(".provenance.json")
    provenance_path.write_text(
        json.dumps(
            {
                "scenario": config.name,
                "source": source_url,
                "downloaded_at_utc": datetime.now(UTC).isoformat(),
                "query": query,
            },
            indent=2,
        )
        + "\n"
    )
    return config.osm_source_path, provenance_path


def import_osm(config_path: Path, output_directory: Path) -> Path:
    """Convert a pre-downloaded OSM extract to a SUMO network.

    The heuristics are a starting point only. The generated network is not
    calibrated or approved until its freeway lanes and every ramp are audited.
    """

    config = load_corridor_config(config_path)
    if not config.osm_source_path.is_file():
        raise FileNotFoundError(
            f"OSM source not found: {config.osm_source_path}. Download a timestamped extract "
            "there before importing."
        )

    apply_patch = config.edge_patch_path is not None
    if apply_patch:
        assert config.edge_patch_path is not None
        assert config.connection_patch_path is not None
        for patch_path in (config.edge_patch_path, config.connection_patch_path):
            if not patch_path.is_file():
                raise FileNotFoundError(f"Network patch not found: {patch_path}")

    output_directory.mkdir(parents=True, exist_ok=True)
    network_file = output_directory / "us101_corridor.net.xml"
    raw_network_file = (
        output_directory / "us101_corridor_osm_raw.net.xml"
        if apply_patch
        else network_file
    )
    subprocess.run(
        [
            str(binary("netconvert")),
            "--osm-files",
            str(config.osm_source_path),
            "--output-file",
            str(raw_network_file),
            "--geometry.remove",
            "--ramps.guess",
            "--junctions.join",
            "--tls.discard-simple",
        ],
        check=True,
    )
    if apply_patch:
        assert config.edge_patch_path is not None
        assert config.connection_patch_path is not None
        subprocess.run(
            [
                str(binary("netconvert")),
                "--sumo-net-file",
                str(raw_network_file),
                "--edge-files",
                str(config.edge_patch_path),
                "--connection-files",
                str(config.connection_patch_path),
                "--output-file",
                str(network_file),
            ],
            check=True,
        )
    return network_file
