"""Import a checked-in OSM extract into a SUMO network for manual audit."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from bay_area_traffic_sim.sumo_install import binary
from bay_area_traffic_sim.toy_corridor import repository_root


@dataclass(frozen=True)
class CorridorConfig:
    """The saved boundary and source location for one real-road import."""

    name: str
    osm_source_path: Path


def load_corridor_config(config_path: Path) -> CorridorConfig:
    """Load import metadata without silently downloading map data."""

    raw = json.loads(config_path.read_text())
    source_path = repository_root() / raw["osm_source_path"]
    return CorridorConfig(name=raw["name"], osm_source_path=source_path)


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

    output_directory.mkdir(parents=True, exist_ok=True)
    network_file = output_directory / "us101_corridor.net.xml"
    subprocess.run(
        [
            str(binary("netconvert")),
            "--osm-files",
            str(config.osm_source_path),
            "--output-file",
            str(network_file),
            "--geometry.remove",
            "--ramps.guess",
            "--junctions.join",
            "--tls.discard-simple",
        ],
        check=True,
    )
    return network_file
