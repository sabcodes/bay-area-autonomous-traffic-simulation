"""Prepare and run the first PeMS-driven human baseline on the real corridor."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import sumolib

from bay_area_traffic_sim.detectors import (
    VirtualDetectorSpec,
    build_virtual_detector_specs,
    detector_specs_as_dict,
    summarize_virtual_detector_output,
    write_virtual_detector_file,
)
from bay_area_traffic_sim.metrics import RunMetrics, read_tripinfo
from bay_area_traffic_sim.osm_import import load_corridor_config
from bay_area_traffic_sim.pems_metadata import load_station_ids
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
class RampDemand:
    """One visually audited ramp route and its observed demand profile."""

    station_id: int
    lane_type: str
    name: str
    route_id: str
    route_edge_ids: list[str]
    demand_profile: list[DemandPoint]


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
    ramp_demands: list[RampDemand]
    virtual_detectors: list[VirtualDetectorSpec]
    assumptions: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def demand_points_from_report(
    report: dict[str, Any], warmup_seconds: int, station_id: int | None = None
) -> list[DemandPoint]:
    """Convert station flow per five minutes into a two-hour SUMO demand profile."""

    summary = report.get("summary", {})
    if station_id is None:
        raw_profile = summary.get("time_profile")
    else:
        station_profile = next(
            (
                profile
                for profile in summary.get("profiles", [])
                if profile.get("station_id") == station_id
            ),
            None,
        )
        raw_profile = station_profile.get("time_profile") if station_profile else None
    if not isinstance(raw_profile, list) or not raw_profile:
        raise ValueError("The PeMS report does not contain a non-empty time profile.")

    points: list[DemandPoint] = []
    for index, raw_point in enumerate(raw_profile):
        flow = raw_point.get(
            "mean_flow_vehicles_per_5_minutes_per_station",
            raw_point.get("mean_flow_vehicles_per_5_minutes"),
        )
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
                    float(observed_speed) if isinstance(observed_speed, (int, float)) else None
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
    ramp_demands: list[RampDemand] | None = None,
) -> None:
    """Write a transparent SUMO route file for human passenger traffic."""

    if not route_edge_ids:
        raise ValueError("The baseline route needs at least one edge.")
    if not demand_points:
        raise ValueError("The baseline route needs at least one demand point.")

    root = ElementTree.Element("routes")
    root.append(
        ElementTree.Comment(
            "Draft human baseline: measured mainline and audited ramp passenger demand."
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
    for ramp in ramp_demands or []:
        ElementTree.SubElement(
            root,
            "route",
            {"id": ramp.route_id, "edges": " ".join(ramp.route_edge_ids)},
        )
    ElementTree.SubElement(
        root,
        "route",
        {"id": "us101_northbound", "edges": " ".join(route_edge_ids)},
    )

    _add_profile_flows(root, "mainline", "us101_northbound", demand_points, warmup_seconds)
    for ramp in ramp_demands or []:
        _add_profile_flows(
            root,
            f"ramp_{ramp.station_id}",
            ramp.route_id,
            ramp.demand_profile,
            warmup_seconds,
        )

    flows = root.findall("flow")
    for flow in flows:
        root.remove(flow)
    for flow in sorted(flows, key=lambda item: int(item.attrib["begin"])):
        root.append(flow)

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
    route_id: str = "us101_northbound",
) -> None:
    ElementTree.SubElement(
        root,
        "flow",
        {
            "id": flow_id,
            "type": "human_passenger",
            "route": route_id,
            "begin": str(begin_seconds),
            "end": str(end_seconds),
            "vehsPerHour": f"{vehicles_per_hour:.2f}",
            "departLane": "best",
            "departSpeed": "max",
        },
    )


def _add_profile_flows(
    root: ElementTree.Element,
    flow_prefix: str,
    route_id: str,
    demand_points: list[DemandPoint],
    warmup_seconds: int,
) -> None:
    if warmup_seconds:
        _add_flow(
            root,
            f"{flow_prefix}_warmup",
            0,
            warmup_seconds,
            demand_points[0].vehicles_per_hour,
            route_id,
        )
    for point in demand_points:
        _add_flow(
            root,
            f"{flow_prefix}_{point.observed_time.replace(':', '')}",
            point.begin_seconds,
            point.end_seconds,
            point.vehicles_per_hour,
            route_id,
        )


def _subtract_demand_profiles(
    minuend: list[DemandPoint], subtrahends: list[list[DemandPoint]]
) -> list[DemandPoint]:
    """Remove measured off-ramp flows from upstream mainline through demand."""

    by_time = [{point.observed_time: point for point in profile} for profile in subtrahends]
    result: list[DemandPoint] = []
    for point in minuend:
        removed = sum(
            profile[point.observed_time].vehicles_per_hour
            for profile in by_time
            if point.observed_time in profile
        )
        remaining = point.vehicles_per_hour - removed
        if remaining < 0:
            raise ValueError(f"Off-ramp demand exceeds mainline demand at {point.observed_time}.")
        result.append(
            DemandPoint(
                observed_time=point.observed_time,
                begin_seconds=point.begin_seconds,
                end_seconds=point.end_seconds,
                vehicles_per_hour=remaining,
                observed_speed_mph=point.observed_speed_mph,
            )
        )
    return result


def _shortest_route_edge_ids(network: Any, start_edge_id: str, end_edge_id: str) -> list[str]:
    """Return one connected SUMO route between two audited edge IDs."""

    try:
        start_edge = network.getEdge(start_edge_id)
        end_edge = network.getEdge(end_edge_id)
    except KeyError as error:
        raise ValueError(f"Configured ramp edge is missing: {error}") from error
    route, _ = network.getShortestPath(start_edge, end_edge)
    if not route:
        raise ValueError(f"No route connects {start_edge_id} to {end_edge_id}.")
    return [edge.getID() for edge in route]


def _build_ramp_demands(
    network_file: Path,
    mainline_edge_ids: list[str],
    mappings: list[dict[str, Any]],
    ramp_report: dict[str, Any],
    warmup_seconds: int,
) -> list[RampDemand]:
    """Join measured ramp profiles to their visually and topologically audited routes."""

    network = sumolib.net.readNet(str(network_file))
    demands: list[RampDemand] = []
    for mapping in mappings:
        station_id = int(mapping["station_id"])
        lane_type = str(mapping["lane_type"])
        ramp_edge_id = str(mapping["sumo_edge_id"])
        if lane_type == "FR":
            route_edge_ids = _shortest_route_edge_ids(network, mainline_edge_ids[0], ramp_edge_id)
        elif lane_type == "OR":
            merge_edge_id = str(mapping["merge_edge_id"])
            try:
                merge_index = mainline_edge_ids.index(merge_edge_id)
            except ValueError as error:
                raise ValueError(
                    f"On-ramp merge edge {merge_edge_id} is not on the mainline route."
                ) from error
            ramp_segment = _shortest_route_edge_ids(network, ramp_edge_id, merge_edge_id)
            route_edge_ids = ramp_segment + mainline_edge_ids[merge_index + 1 :]
        else:
            raise ValueError(f"Ramp station {station_id} has unsupported lane type {lane_type}.")
        demands.append(
            RampDemand(
                station_id=station_id,
                lane_type=lane_type,
                name=str(mapping["name"]),
                route_id=f"ramp_{station_id}_{lane_type.lower()}",
                route_edge_ids=route_edge_ids,
                demand_profile=demand_points_from_report(ramp_report, warmup_seconds, station_id),
            )
        )
    return demands


def _expected_profile_input(
    profiles: list[list[DemandPoint]], warmup_seconds: int
) -> tuple[float, float]:
    """Return total and warmup vehicle inputs across all demand profiles."""

    warmup_input = sum(profile[0].vehicles_per_hour * warmup_seconds / 3600 for profile in profiles)
    observed_input = sum(
        point.vehicles_per_hour * (point.end_seconds - point.begin_seconds) / 3600
        for profile in profiles
        for point in profile
    )
    return warmup_input + observed_input, warmup_input


def prepare_human_baseline(config_path: Path) -> PreparedBaseline:
    """Build a route and provenance manifest from the corrected network and PeMS report."""

    root = repository_root()
    raw = json.loads(config_path.read_text())
    network_file = root / raw["network_file"]
    pems_report_file = root / raw["pems_report"]
    ramp_profile_file = root / raw["ramp_profile_file"]
    route_file = root / raw["route_file"]
    manifest_file = root / raw["manifest_file"]
    for required_file in (network_file, pems_report_file, ramp_profile_file):
        if not required_file.is_file():
            raise FileNotFoundError(f"Required baseline input not found: {required_file}")

    warmup_seconds = int(raw["warmup_seconds"])
    clearance_seconds = int(raw["clearance_seconds"])
    report = json.loads(pems_report_file.read_text())
    mainline_entry_points = demand_points_from_report(
        report, warmup_seconds, int(raw["mainline_entry_station_id"])
    )
    ramp_report = json.loads(ramp_profile_file.read_text())
    route_edges = _route_edges(network_file, raw["checkpoint_edge_ids"])
    route_edge_ids = [edge.getID() for edge in route_edges]
    route_length = sum(edge.getLength() for edge in route_edges)
    ramp_demands = _build_ramp_demands(
        network_file,
        route_edge_ids,
        raw["active_ramp_mappings"],
        ramp_report,
        warmup_seconds,
    )
    off_ramp_profiles = [ramp.demand_profile for ramp in ramp_demands if ramp.lane_type == "FR"]
    mainline_through_points = _subtract_demand_profiles(mainline_entry_points, off_ramp_profiles)
    write_route_file(
        route_file,
        route_edge_ids,
        mainline_through_points,
        warmup_seconds,
        ramp_demands,
    )

    all_profiles = [mainline_through_points] + [ramp.demand_profile for ramp in ramp_demands]
    expected_input, warmup_input = _expected_profile_input(all_profiles, warmup_seconds)
    simulation_end = mainline_through_points[-1].end_seconds + clearance_seconds
    corridor = load_corridor_config(root / raw["corridor_config"])
    detector_station_ids = load_station_ids(
        root / raw["virtual_detector_station_ids_file"],
        raw["virtual_detector_station_ids_key"],
    )
    detector_specs = build_virtual_detector_specs(
        network_file,
        sorted(root.glob(raw["metadata_glob"])),
        corridor.bounding_box,
        detector_station_ids,
    )
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
        demand_profile=mainline_through_points,
        ramp_demands=ramp_demands,
        virtual_detectors=detector_specs,
        assumptions=[
            *raw["assumptions"],
            f"Warmup contributes approximately {warmup_input:.1f} input vehicles.",
        ],
    )
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(prepared.as_dict(), indent=2) + "\n")
    return prepared


def run_human_baseline(
    config_path: Path, seed: int = 42
) -> tuple[PreparedBaseline, RunMetrics, Path]:
    """Run the draft real-corridor human baseline and read completed-trip metrics."""

    prepared = prepare_human_baseline(config_path)
    output_directory = Path(prepared.manifest_file).parent
    tripinfo_file = output_directory / f"h0_human_baseline_seed_{seed}.tripinfo.xml"
    log_file = output_directory / f"h0_human_baseline_seed_{seed}.log"
    raw = json.loads(config_path.read_text())
    detector_file = repository_root() / raw["detector_file_template"].format(seed=seed)
    detector_output_file = repository_root() / raw["detector_output_template"].format(seed=seed)
    detector_summary_file = repository_root() / raw["detector_summary_template"].format(seed=seed)
    write_virtual_detector_file(
        detector_file,
        detector_output_file,
        prepared.virtual_detectors,
    )
    subprocess.run(
        [
            str(binary("sumo")),
            "--net-file",
            prepared.network_file,
            "--route-files",
            prepared.route_file,
            "--additional-files",
            str(detector_file),
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
    detector_intervals = summarize_virtual_detector_output(detector_output_file)
    detector_summary_file.write_text(
        json.dumps(
            {
                "seed": seed,
                "period_seconds": SECONDS_PER_PROFILE_INTERVAL,
                "detectors": detector_specs_as_dict(prepared.virtual_detectors),
                "intervals": [asdict(interval) for interval in detector_intervals],
            },
            indent=2,
        )
        + "\n"
    )
    return prepared, read_tripinfo(tripinfo_file), detector_summary_file
