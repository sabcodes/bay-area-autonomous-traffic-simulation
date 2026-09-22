"""Build and run the first intentionally small freeway experiment."""

from __future__ import annotations

import subprocess
from dataclasses import asdict
from pathlib import Path

from bay_area_traffic_sim.metrics import RunMetrics, read_tripinfo
from bay_area_traffic_sim.sumo_install import binary

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TOY_NETWORK_SOURCE = REPOSITORY_ROOT / "network" / "toy_corridor"
TOY_ROUTE_FILE = REPOSITORY_ROOT / "routes" / "toy_corridor.rou.xml"
TOY_OUTPUT_DIRECTORY = REPOSITORY_ROOT / "outputs" / "toy_corridor"


def build_network(output_directory: Path = TOY_OUTPUT_DIRECTORY) -> Path:
    """Create a runnable network from the checked-in node and edge files."""

    output_directory.mkdir(parents=True, exist_ok=True)
    network_file = output_directory / "toy_corridor.net.xml"
    subprocess.run(
        [
            str(binary("netconvert")),
            "--node-files",
            str(TOY_NETWORK_SOURCE / "toy_corridor.nod.xml"),
            "--edge-files",
            str(TOY_NETWORK_SOURCE / "toy_corridor.edg.xml"),
            "--output-file",
            str(network_file),
            "--no-warnings",
        ],
        check=True,
    )
    return network_file


def run_human_baseline(seed: int = 42) -> RunMetrics:
    """Run the uncalibrated human-like toy baseline and summarize finished trips."""

    network_file = build_network()
    tripinfo_file = TOY_OUTPUT_DIRECTORY / f"human_baseline_seed_{seed}.tripinfo.xml"
    subprocess.run(
        [
            str(binary("sumo")),
            "--net-file",
            str(network_file),
            "--route-files",
            str(TOY_ROUTE_FILE),
            "--step-length",
            "0.5",
            "--end",
            "900",
            "--seed",
            str(seed),
            "--tripinfo-output",
            str(tripinfo_file),
            "--no-step-log",
            "true",
            "--duration-log.disable",
            "true",
            "--xml-validation",
            "never",
        ],
        check=True,
    )
    return read_tripinfo(tripinfo_file)


def metrics_as_dict(metrics: RunMetrics) -> dict[str, float | int | None]:
    """Return JSON-friendly metrics for the command-line interface."""

    return asdict(metrics)
