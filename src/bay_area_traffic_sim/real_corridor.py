"""Prepare and run the first PeMS-driven human baseline on the real corridor."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import sumolib

from bay_area_traffic_sim.metrics import RunMetrics, read_tripinfo
from bay_area_traffic_sim.sumo_install import binary
from bay_area_traffic_sim.toy_corridor import repository_root

SECONDS_PER_PROFILE_INTERVAL = 300
FIVE_MINUTE_INTERVALS_PER_HOUR = 12


@dataclass(frozen=True)
class DemandPoint:
    """One five-minute mainline demand target derived from PeMS."""

    observed_time: str
    begin_seconds: int
    end_seconds: int
    vehicles_per_hour: float
    observed_speed_mph: float | None


@dataclass(frozen=True)
class PreparedBaseline:
    """Files and assumptions needed to reproduce one draft baseline."""

    scenario: str
    network_file: str
    route_file: str
    manifest_file: str
    route_edge_count: int
    route_length_meters: float
    minimum_lane_count: int
    expected_input_vehicles: float
    simulation_end_seconds: int
    demand_profile: list[DemandPoint]
    assumptions: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def demand_points_from_report(report: dict[str, Any], warmup_seconds: int) -> list[DemandPoint]:
    """Convert station flow per five minutes into a two-hour SUMO demand profile."""

    raw_profile = report.get("summary", {}).get("time_profile")
    if not isinstance(raw_profile, list) or not raw_profile:
        raise ValueError("The PeMS report does not contain a non-empty time profile.")

    points: list[DemandPoint] = []
    for index, raw_point in enumerate(raw_profile):
        flow = raw_point.get("mean_flow_vehicles_per_5_minutes_per_station")
        observed_time = raw_point.get("time")
        observed_speed = raw_point.get("mean_speed_mph")
        if not isinstance(flow, (int, float)) or not isinstance(observed_time, str):
            raise ValueError("Every PeMS time-profile point needs a time and numeric flow.")
        begin = warmup_seconds + index * SECONDS_PER_PROFILE_INTERVAL
        points.append(
            DemandPoint(
                observed_time=observed_time,
                begin_seconds=begin,
                end_seconds=begin + SECONDS_PER_PROFILE_INTERVAL,
                vehicles_per_hour=float(flow) * FIVE_MINUTE_INTERVALS_PER_HOUR,
                observed_speed_mph=(
                    float(observed_speed)
                    if isinstance(observed_speed, (int, float))
                    else None
                ),
            )
        )
    return points


def _route_edges(network_file: Path, checkpoint_edge_ids: list[str]) -> list[Any]:
    if len(checkpoint_edge_ids) < 2:
        raise ValueError("The corridor route needs at least two ordered checkpoints.")

    network = sumolib.net.readNet(str(network_file))
    try:
        checkpoints = [network.getEdge(edge_id) for edge_id in checkpoint_edge_ids]
    except KeyError as error:
        message = f"Configured corridor edge is missing from {network_file}: {error}"
        raise ValueError(message) from error

    route: list[Any] = []
    for start_edge, end_edge in zip(checkpoints[:-1], checkpoints[1:], strict=True):
        segment, _ = network.getShortestPath(start_edge, end_edge)
        if not segment:
            raise ValueError(f"No route connects {start_edge.getID()} to {end_edge.getID()}.")
        route.extend(segment if not route else segment[1:])
    return route


def write_route_file(
    destination: Path,
    route_edge_ids: list[str],
    demand_points: list[DemandPoint],
    warmup_seconds: int,
) -> None:
    """Write a transparent SUMO route file for human passenger traffic."""

    if not route_edge_ids:
        raise ValueError("The baseline route needs at least one edge.")
    if not demand_points:
        raise ValueError("The baseline route needs at least one demand point.")

    root = ElementTree.Element("routes")
    root.append(
        ElementTree.Comment(
            "Draft human baseline: mainline passenger demand only; not yet fully calibrated."
        )
    )
    ElementTree.SubElement(
        root,
        "vType",
        {
            "id": "human_passenger",
            "vClass": "passenger",
            "carFollowModel": "Krauss",
            "accel": "2.6",
            "decel": "4.5",
            "emergencyDecel": "9.0",
            "sigma": "0.5",
            "tau": "1.2",
            "length": "5.0",
            "minGap": "2.5",
            "speedFactor": "1.0",
            "speedDev": "0.1",
        },
    )
    ElementTree.SubElement(
        root,
        "route",
        {"id": "us101_northbound", "edges": " ".join(route_edge_ids)},
    )

    first_rate = demand_points[0].vehicles_per_hour
    if warmup_seconds:
        _add_flow(root, "warmup", 0, warmup_seconds, first_rate)
    for point in demand_points:
        _add_flow(
            root,
            f"observed_{point.observed_time.replace(':', '')}",
            point.begin_seconds,
            point.end_seconds,
            point.vehicles_per_hour,
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    tree = ElementTree.ElementTree(root)
    ElementTree.indent(tree, space="    ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def _add_flow(
    root: ElementTree.Element,
    flow_id: str,
    begin_seconds: int,
    end_seconds: int,
    vehicles_per_hour: float,
) -> None:
    ElementTree.SubElement(
        root,
        "flow",
        {
            "id": flow_id,
            "type": "human_passenger",
            "route": "us101_northbound",
            "begin": str(begin_seconds),
            "end": str(end_seconds),
            "vehsPerHour": f"{vehicles_per_hour:.2f}",
            "departLane": "best",
            "departSpeed": "max",
        },
    )


def prepare_human_baseline(config_path: Path) -> PreparedBaseline:
    """Build a route and provenance manifest from the corrected network and PeMS report."""

    root = repository_root()
    raw = json.loads(config_path.read_text())
    network_file = root / raw["network_file"]
    pems_report_file = root / raw["pems_report"]
    route_file = root / raw["route_file"]
    manifest_file = root / raw["manifest_file"]
    for required_file in (network_file, pems_report_file):
        if not required_file.is_file():
            raise FileNotFoundError(f"Required baseline input not found: {required_file}")

    warmup_seconds = int(raw["warmup_seconds"])
    clearance_seconds = int(raw["clearance_seconds"])
    report = json.loads(pems_report_file.read_text())
    demand_points = demand_points_from_report(report, warmup_seconds)
    route_edges = _route_edges(network_file, raw["checkpoint_edge_ids"])
    route_edge_ids = [edge.getID() for edge in route_edges]
    route_length = sum(edge.getLength() for edge in route_edges)
    write_route_file(route_file, route_edge_ids, demand_points, warmup_seconds)

    first_interval_input = demand_points[0].vehicles_per_hour * warmup_seconds / 3600
    expected_input = first_interval_input
    expected_input += sum(
        point.vehicles_per_hour * (point.end_seconds - point.begin_seconds) / 3600
        for point in demand_points
    )
    simulation_end = demand_points[-1].end_seconds + clearance_seconds
    prepared = PreparedBaseline(
        scenario=raw["scenario"],
        network_file=str(network_file),
        route_file=str(route_file),
        manifest_file=str(manifest_file),
        route_edge_count=len(route_edges),
        route_length_meters=route_length,
        minimum_lane_count=min(edge.getLaneNumber() for edge in route_edges),
        expected_input_vehicles=expected_input,
        simulation_end_seconds=simulation_end,
        demand_profile=demand_points,
        assumptions=[
            *raw["assumptions"],
            f"Warmup contributes approximately {first_interval_input:.1f} input vehicles.",
        ],
    )
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(prepared.as_dict(), indent=2) + "\n")
    return prepared


def run_human_baseline(config_path: Path, seed: int = 42) -> tuple[PreparedBaseline, RunMetrics]:
    """Run the draft real-corridor human baseline and read completed-trip metrics."""

    prepared = prepare_human_baseline(config_path)
    output_directory = Path(prepared.manifest_file).parent
    tripinfo_file = output_directory / f"h0_human_baseline_seed_{seed}.tripinfo.xml"
    log_file = output_directory / f"h0_human_baseline_seed_{seed}.log"
    subprocess.run(
        [
            str(binary("sumo")),
            "--net-file",
            prepared.network_file,
            "--route-files",
            prepared.route_file,
            "--step-length",
            "0.5",
            "--end",
            str(prepared.simulation_end_seconds),
            "--seed",
            str(seed),
            "--tripinfo-output",
            str(tripinfo_file),
            "--log",
            str(log_file),
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
    return prepared, read_tripinfo(tripinfo_file)
