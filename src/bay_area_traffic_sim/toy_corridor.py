"""Build and run the first intentionally small freeway experiment."""

from __future__ import annotations

import subprocess
from dataclasses import asdict
from pathlib import Path

from bay_area_traffic_sim.metrics import RunMetrics, read_tripinfo
from bay_area_traffic_sim.sumo_install import binary


def repository_root(start_directory: Path | None = None) -> Path:
    """Find this checkout from the current directory or one of its parents."""

    start = (start_directory or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "network").is_dir():
            return candidate
    raise RuntimeError(
        "Run this command from the repository or one of its subdirectories so its scenario files "
        "can be found."
    )


REPOSITORY_ROOT = repository_root()
TOY_NETWORK_SOURCE = REPOSITORY_ROOT / "network" / "toy_corridor"
TOY_ROUTE_FILE = REPOSITORY_ROOT / "routes" / "toy_corridor.rou.xml"
TOY_COOPERATIVE_ROUTE_FILE = REPOSITORY_ROOT / "routes" / "toy_corridor_cooperative.rou.xml"
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
        stdout=subprocess.DEVNULL,
    )
    return network_file


def _run_route(route_file: Path, report_name: str, seed: int) -> RunMetrics:
    network_file = build_network()
    tripinfo_file = TOY_OUTPUT_DIRECTORY / f"{report_name}_seed_{seed}.tripinfo.xml"
    subprocess.run(
        [
            str(binary("sumo")),
            "--net-file",
            str(network_file),
            "--route-files",
            str(route_file),
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
        stdout=subprocess.DEVNULL,
    )
    return read_tripinfo(tripinfo_file)


def run_human_baseline(seed: int = 42) -> RunMetrics:
    """Run the uncalibrated human-like toy baseline and summarize finished trips."""

    return _run_route(TOY_ROUTE_FILE, "human_baseline", seed)


def run_cacc_sensitivity(seed: int = 42) -> RunMetrics:
    """Run a deterministic CACC sensitivity scenario without a V2V controller.

    This experiment changes only the vehicle-following model; it makes no claim
    to simulate radio communications, cooperative routing, or learned control.
    """

    return _run_route(TOY_COOPERATIVE_ROUTE_FILE, "cacc_sensitivity", seed)


def metrics_as_dict(metrics: RunMetrics) -> dict[str, float | int | None]:
    """Return JSON-friendly metrics for the command-line interface."""

    return asdict(metrics)
