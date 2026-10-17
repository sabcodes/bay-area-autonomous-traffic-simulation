"""Prepare and run the first PeMS-driven human baseline on the real corridor."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import sumolib

from bay_area_traffic_sim.cooperative import run_controlled, validate_controller
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
    """One visually audited ramp route and its measured or assumed demand profile."""

    station_id: int | None
    lane_type: str
    name: str
    route_id: str
    route_edge_ids: list[str]
    demand_profile: list[DemandPoint]
    source_kind: str = "measured_pems"
    source_note: str | None = None
    vehicle_type: str | None = None


@dataclass(frozen=True)
class PreparedBaseline:
    """Files and assumptions needed to reproduce one draft baseline."""

    scenario: str
    network_file: str
    network_sha256: str
    route_file: str
    manifest_file: str
    aligned_observed_profile_file: str
    observation_dates: list[str]
    human_parameters: dict[str, float]
    truck_share: float
    vehicle_types: list[dict[str, str]]
    provenance: dict[str, Any]
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
    report: dict[str, Any],
    warmup_seconds: int,
    station_id: int | None = None,
    observation_dates: set[str] | None = None,
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
        if station_profile and observation_dates is not None:
            raw_profile = _average_daily_profile(station_profile, observation_dates)
        else:
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


def _average_daily_profile(
    profile: dict[str, Any], observation_dates: set[str]
) -> list[dict[str, Any]]:
    """Average a station profile over only the requested actual dates."""

    daily_profiles = profile.get("daily_time_profile")
    if not isinstance(daily_profiles, list):
        raise ValueError(
            f"Station {profile.get('station_id')} has no date-level profile; regenerate "
            "the PeMS station profiles before preparing a date-aligned scenario."
        )
    by_time: defaultdict[str, list[tuple[float, int, float | None]]] = defaultdict(list)
    for daily in daily_profiles:
        if daily.get("date") not in observation_dates:
            continue
        for point in daily.get("time_profile", []):
            flow = point.get("mean_flow_vehicles_per_5_minutes")
            if not isinstance(flow, (int, float)):
                continue
            observations = int(point.get("observations", 1))
            speed = point.get("mean_speed_mph")
            by_time[str(point["time"])].append(
                (
                    float(flow),
                    observations,
                    float(speed) if isinstance(speed, (int, float)) else None,
                )
            )
    if not by_time:
        raise ValueError(
            f"Station {profile.get('station_id')} has no observations on the selected dates."
        )
    return [
        {
            "time": time,
            "observations": sum(count for _, count, _ in values),
            "mean_flow_vehicles_per_5_minutes": (
                sum(flow * count for flow, count, _ in values)
                / sum(count for _, count, _ in values)
            ),
            "mean_speed_mph": (
                sum(speed * count for _, count, speed in values if speed is not None)
                / sum(count for _, count, speed in values if speed is not None)
                if any(speed is not None for _, _, speed in values)
                else None
            ),
        }
        for time, values in sorted(by_time.items())
    ]


def common_observation_dates(reports: list[dict[str, Any]], station_ids: list[int]) -> set[str]:
    """Find dates where every selected station has all of the same time slots."""

    profiles: dict[int, dict[str, Any]] = {}
    for report in reports:
        for profile in report.get("summary", {}).get("profiles", []):
            station_id = int(profile["station_id"])
            if station_id in profiles:
                raise ValueError(f"Station {station_id} appears in more than one profile report.")
            profiles[station_id] = profile
    missing = sorted(set(station_ids) - set(profiles))
    if missing:
        raise ValueError(f"No PeMS profiles are available for required stations: {missing}.")
    date_sets: list[set[str]] = []
    time_sets_by_station: dict[int, dict[str, set[str]]] = {}
    for station_id in station_ids:
        profile = profiles[station_id]
        daily_profiles = profile.get("daily_time_profile")
        if not isinstance(daily_profiles, list):
            raise ValueError(
                f"Station {station_id} has no date-level profile; regenerate PeMS profiles."
            )
        date_sets.append({str(day["date"]) for day in daily_profiles})
        time_sets_by_station[station_id] = {
            str(day["date"]): {str(point["time"]) for point in day.get("time_profile", [])}
            for day in daily_profiles
        }
    common_dates = set.intersection(*date_sets) if date_sets else set()
    if not common_dates:
        raise ValueError("The selected demand stations have no shared observation dates.")
    expected_times = {
        str(point["time"]) for point in profiles[station_ids[0]].get("time_profile", [])
    }
    complete_dates = {
        date
        for date in common_dates
        if all(
            time_sets_by_station[station_id][date] >= expected_times for station_id in station_ids
        )
    }
    if not complete_dates:
        raise ValueError("No shared observation dates have complete matching time slots.")
    return complete_dates


def _align_profile_report(report: dict[str, Any], dates: set[str]) -> dict[str, Any]:
    """Return a copy of a station report whose summaries use the chosen dates."""

    aligned = deepcopy(report)
    profiles = aligned.get("summary", {}).get("profiles", [])
    for profile in profiles:
        profile["daily_time_profile"] = [
            day for day in profile.get("daily_time_profile", []) if day.get("date") in dates
        ]
        profile["date_count"] = len(profile["daily_time_profile"])
        profile["time_profile"] = _average_daily_profile(profile, dates)
        profile["matching_rows"] = sum(
            int(point.get("observations", 0))
            for day in profile["daily_time_profile"]
            for point in day.get("time_profile", [])
        )
        all_points = [
            point for day in profile["daily_time_profile"] for point in day["time_profile"]
        ]
        total_observations = sum(int(point.get("observations", 0)) for point in all_points)
        profile["mean_flow_vehicles_per_5_minutes"] = (
            sum(
                float(point["mean_flow_vehicles_per_5_minutes"]) * int(point.get("observations", 0))
                for point in all_points
            )
            / total_observations
            if total_observations
            else None
        )
        speed_points = [
            point for point in all_points if isinstance(point.get("mean_speed_mph"), (int, float))
        ]
        speed_observations = sum(int(point.get("observations", 0)) for point in speed_points)
        profile["mean_speed_mph"] = (
            sum(
                float(point["mean_speed_mph"]) * int(point.get("observations", 0))
                for point in speed_points
            )
            / speed_observations
            if speed_observations
            else None
        )
    summary = aligned.get("summary", {})
    summary["matching_rows"] = sum(profile.get("matching_rows", 0) for profile in profiles)
    summary["station_count"] = len(profiles)
    aligned["date_alignment"] = {
        "method": "shared complete dates across all scenario demand stations",
        "observation_dates": sorted(dates),
    }
    return aligned


def _load_baseline_config(
    config_path: Path, root: Path, parents: frozenset[Path] = frozenset()
) -> dict[str, Any]:
    """Load a full baseline config, optionally inheriting a parent scenario."""

    config_file = (config_path if config_path.is_absolute() else root / config_path).resolve()
    if config_file in parents:
        raise ValueError(f"Scenario config inheritance cycle at {config_file}.")
    raw = json.loads(config_file.read_text())
    parent_config = raw.pop("extends", None)
    if parent_config:
        inherited = _load_baseline_config(Path(parent_config), root, parents | {config_file})
        inherited.update(raw)
        raw = inherited
    return raw


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
    human_parameters: dict[str, float] | None = None,
    truck_share: float = 0.0,
) -> None:
    """Write a transparent SUMO route file for human passenger traffic."""

    if not route_edge_ids:
        raise ValueError("The baseline route needs at least one edge.")
    if not demand_points:
        raise ValueError("The baseline route needs at least one demand point.")
    if not math.isfinite(truck_share) or not 0 <= truck_share <= 1:
        raise ValueError("truck_share must be a finite proportion in [0, 1].")

    root = ElementTree.Element("routes")
    root.append(
        ElementTree.Comment(
            "Draft human baseline: measured mainline and audited ramp passenger demand."
        )
    )
    passenger_attributes = {
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
    }
    passenger_attributes.update(
        {key: str(value) for key, value in (human_parameters or {}).items()}
    )
    type_id = "human_mix" if truck_share else "human_passenger"
    parent = (
        ElementTree.SubElement(root, "vTypeDistribution", {"id": type_id}) if truck_share else root
    )
    if truck_share:
        # ponytail: one heavy-vehicle proxy; use axle-class types if measured data become available.
        passenger_attributes["probability"] = str(1.0 - truck_share)
    ElementTree.SubElement(parent, "vType", passenger_attributes)
    if truck_share:
        ElementTree.SubElement(
            parent,
            "vType",
            {
                **passenger_attributes,
                "id": "human_truck",
                "vClass": "truck",
                "probability": str(truck_share),
                "length": "12.0",
                "accel": "1.2",
                "decel": "4.0",
                "maxSpeed": "24.59",
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

    _add_profile_flows(root, "mainline", "us101_northbound", demand_points, warmup_seconds, type_id)
    for ramp in ramp_demands or []:
        _add_profile_flows(
            root,
            f"ramp_{ramp.station_id}" if ramp.station_id is not None else ramp.route_id,
            ramp.route_id,
            ramp.demand_profile,
            warmup_seconds,
            ramp.vehicle_type or type_id,
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
    type_id: str = "human_passenger",
) -> None:
    ElementTree.SubElement(
        root,
        "flow",
        {
            "id": flow_id,
            "type": type_id,
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
    type_id: str = "human_passenger",
) -> None:
    if warmup_seconds:
        _add_flow(
            root,
            f"{flow_prefix}_warmup",
            0,
            warmup_seconds,
            demand_points[0].vehicles_per_hour,
            route_id,
            type_id,
        )
    for point in demand_points:
        _add_flow(
            root,
            f"{flow_prefix}_{point.observed_time.replace(':', '')}",
            point.begin_seconds,
            point.end_seconds,
            point.vehicles_per_hour,
            route_id,
            type_id,
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
    observation_dates: set[str],
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
                demand_profile=demand_points_from_report(
                    ramp_report, warmup_seconds, station_id, observation_dates
                ),
                source_kind="measured_pems",
                source_note=None,
            )
        )
    return demands


def _build_estimated_ramp_demands(
    network_file: Path,
    mainline_edge_ids: list[str],
    mappings: list[dict[str, Any]],
    time_template: list[DemandPoint],
) -> list[RampDemand]:
    """Create labeled constant-flow ramp hypotheses, not PeMS observations."""

    if not mappings:
        return []
    network = sumolib.net.readNet(str(network_file))
    demands: list[RampDemand] = []
    used_ids: set[str] = set()
    for mapping in mappings:
        estimate_id = str(mapping["id"])
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", estimate_id):
            raise ValueError(f"Invalid estimated entrance ID: {estimate_id!r}.")
        if estimate_id in used_ids:
            raise ValueError(f"Duplicate estimated entrance ID: {estimate_id}.")
        used_ids.add(estimate_id)
        flow = float(mapping["vehicles_per_hour"])
        if not math.isfinite(flow) or flow < 0:
            raise ValueError(f"Estimated entrance {estimate_id} needs finite non-negative flow.")
        lane_type = str(mapping.get("lane_type", "OR"))
        if lane_type == "OR":
            merge_edge_id = str(mapping["merge_edge_id"])
            try:
                merge_index = mainline_edge_ids.index(merge_edge_id)
            except ValueError as error:
                raise ValueError(
                    f"Estimated entrance merge edge {merge_edge_id} is not on the mainline."
                ) from error
            ramp_segment = _shortest_route_edge_ids(
                network, str(mapping["sumo_edge_id"]), merge_edge_id
            )
            route_edge_ids = ramp_segment + mainline_edge_ids[merge_index + 1 :]
        elif lane_type == "FR":
            diverge = str(mapping["diverge_edge_id"])
            diverge_index = mainline_edge_ids.index(diverge)
            exit_edge = network.getEdge(str(mapping["sumo_edge_id"]))
            if exit_edge not in network.getEdge(diverge).getOutgoing():
                raise ValueError(f"Estimated exit is not directly connected to {diverge}.")
            route_edge_ids = mainline_edge_ids[: diverge_index + 1] + [exit_edge.getID()]
        else:
            raise ValueError(f"Unsupported estimated ramp type: {lane_type}.")
        demands.append(
            RampDemand(
                station_id=None,
                lane_type=lane_type,
                name=str(mapping["name"]),
                route_id=f"estimated_{estimate_id}",
                route_edge_ids=route_edge_ids,
                demand_profile=[
                    DemandPoint(
                        observed_time=point.observed_time,
                        begin_seconds=point.begin_seconds,
                        end_seconds=point.end_seconds,
                        vehicles_per_hour=flow,
                        observed_speed_mph=None,
                    )
                    for point in time_template
                ],
                source_kind="assumed_sensitivity",
                source_note=str(mapping["basis"]),
                vehicle_type="human_passenger" if mapping.get("passenger_only") else None,
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
    raw = _load_baseline_config(config_path, root)
    network_file = root / raw["network_file"]
    pems_report_file = root / raw["pems_report"]
    ramp_profile_file = root / raw["ramp_profile_file"]
    route_file = root / raw["route_file"]
    manifest_file = root / raw["manifest_file"]
    supplemental_ramp_reports = [
        json.loads((root / path).read_text())
        for path in raw.get("supplemental_ramp_profile_files", [])
    ]
    for required_file in (network_file, pems_report_file, ramp_profile_file):
        if not required_file.is_file():
            raise FileNotFoundError(f"Required baseline input not found: {required_file}")
    for filename, expected in raw.get("expected_input_sha256", {}).items():
        actual = hashlib.sha256((root / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Frozen M3 input changed: {filename}. Rebaseline explicitly.")

    warmup_seconds = int(raw["warmup_seconds"])
    clearance_seconds = int(raw["clearance_seconds"])
    human_parameters = {
        "accel": 2.6,
        "decel": 4.5,
        "emergencyDecel": 9.0,
        "sigma": 0.5,
        "tau": 1.2,
        "length": 5.0,
        "minGap": 2.5,
        "speedFactor": 1.0,
        "speedDev": 0.1,
    }
    overrides = raw.get("human_parameters", {})
    allowed_parameters = set(human_parameters) | {"lcCooperative", "lcSpeedGain", "lcStrategic"}
    if set(overrides) - allowed_parameters:
        raise ValueError(
            f"Unsupported human parameters: {sorted(set(overrides) - allowed_parameters)}"
        )
    human_parameters.update({key: float(value) for key, value in overrides.items()})
    if any(not math.isfinite(value) or value < 0 for value in human_parameters.values()):
        raise ValueError("Human parameters must be finite and non-negative.")
    if human_parameters["tau"] < 0.5 or not 0 <= human_parameters["sigma"] <= 1:
        raise ValueError("tau must be at least the 0.5-second step; sigma must be in [0, 1].")
    truck_share = float(raw.get("truck_share", 0.0))
    if not math.isfinite(truck_share) or not 0 <= truck_share <= 1:
        raise ValueError("truck_share must be a finite proportion in [0, 1].")
    report = json.loads(pems_report_file.read_text())
    ramp_report = json.loads(ramp_profile_file.read_text())
    ramp_reports = [ramp_report, *supplemental_ramp_reports]
    ramp_profiles = [
        profile
        for source_report in ramp_reports
        for profile in source_report.get("summary", {}).get("profiles", [])
    ]
    ramp_report = {
        **ramp_report,
        "summary": {**ramp_report.get("summary", {}), "profiles": ramp_profiles},
    }
    ramp_mappings = [
        *raw["active_ramp_mappings"],
        *raw.get("additional_ramp_mappings", []),
    ]
    station_ids_for_demand = [
        int(raw["mainline_entry_station_id"]),
        *(int(mapping["station_id"]) for mapping in ramp_mappings),
    ]
    available_dates = common_observation_dates([report, *ramp_reports], station_ids_for_demand)
    configured_dates = raw.get("observation_dates")
    if configured_dates is None:
        observation_dates = available_dates
    else:
        if not isinstance(configured_dates, list) or not configured_dates:
            raise ValueError("observation_dates must be a non-empty list of ISO dates.")
        for selected_date in configured_dates:
            if not isinstance(selected_date, str):
                raise ValueError("Every observation date must be an ISO date string.")
            date.fromisoformat(selected_date)
        if len(configured_dates) != len(set(configured_dates)):
            raise ValueError("observation_dates contains a duplicate date.")
        unavailable = sorted(set(configured_dates) - available_dates)
        if unavailable:
            raise ValueError(
                f"Selected observation dates lack complete common demand profiles: {unavailable}"
            )
        observation_dates = set(configured_dates)
    mainline_entry_points = demand_points_from_report(
        report,
        warmup_seconds,
        int(raw["mainline_entry_station_id"]),
        observation_dates,
    )
    route_edges = _route_edges(network_file, raw["checkpoint_edge_ids"])
    route_edge_ids = [edge.getID() for edge in route_edges]
    route_length = sum(edge.getLength() for edge in route_edges)
    ramp_demands = _build_ramp_demands(
        network_file,
        route_edge_ids,
        ramp_mappings,
        ramp_report,
        warmup_seconds,
        observation_dates,
    )
    ramp_demands.extend(
        _build_estimated_ramp_demands(
            network_file,
            route_edge_ids,
            raw.get("estimated_ramp_mappings", raw.get("estimated_entrance_mappings", [])),
            mainline_entry_points,
        )
    )
    off_ramp_profiles = [ramp.demand_profile for ramp in ramp_demands if ramp.lane_type == "FR"]
    mainline_through_points = _subtract_demand_profiles(mainline_entry_points, off_ramp_profiles)
    write_route_file(
        route_file,
        route_edge_ids,
        mainline_through_points,
        warmup_seconds,
        ramp_demands,
        human_parameters,
        truck_share,
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
        {
            int(station): indices
            for station, indices in raw.get("detector_lane_indices", {}).items()
        },
    )
    aligned_observed_profile_file = root / raw["aligned_pems_report_file"]
    aligned_observed_profile_file.parent.mkdir(parents=True, exist_ok=True)
    aligned_observed_profile_file.write_text(
        json.dumps(_align_profile_report(report, observation_dates), indent=2) + "\n"
    )
    prepared = PreparedBaseline(
        scenario=raw["scenario"],
        network_file=str(network_file),
        network_sha256=hashlib.sha256(network_file.read_bytes()).hexdigest(),
        route_file=str(route_file),
        manifest_file=str(manifest_file),
        aligned_observed_profile_file=str(aligned_observed_profile_file),
        observation_dates=sorted(observation_dates),
        human_parameters=human_parameters,
        truck_share=truck_share,
        vehicle_types=[
            kind.attrib for kind in ElementTree.parse(route_file).getroot().iter("vType")
        ],
        provenance={
            "mainline_profile_sha256": hashlib.sha256(pems_report_file.read_bytes()).hexdigest(),
            "ramp_profile_sha256": hashlib.sha256(ramp_profile_file.read_bytes()).hexdigest(),
            "metadata_sha256": {
                str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(root.glob(raw["metadata_glob"]))
            },
            "sumo_version": subprocess.check_output(
                [str(binary("sumo")), "--version"], text=True
            ).splitlines()[0],
        },
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
            *raw.get("additional_assumptions", []),
            "Mainline and active ramp demand profiles use the same dates and complete "
            "five-minute intervals.",
            f"Warmup contributes approximately {warmup_input:.1f} input vehicles.",
        ],
    )
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(prepared.as_dict(), indent=2) + "\n")
    return prepared


def run_human_baseline(
    config_path: Path,
    seed: int = 42,
    *,
    trajectory_output: Path | None = None,
    trajectory_period_seconds: float = 1.0,
    controller: dict | None = None,
) -> tuple[PreparedBaseline, RunMetrics, Path]:
    """Run the draft real-corridor human baseline and read completed-trip metrics."""

    prepared = prepare_human_baseline(config_path)
    raw = _load_baseline_config(config_path, repository_root())
    if controller is not None:
        validate_controller(controller, prepared.human_parameters)
    output_directory = Path(prepared.manifest_file).parent
    tripinfo_file = output_directory / f"h0_human_baseline_seed_{seed}.tripinfo.xml"
    log_file = output_directory / f"h0_human_baseline_seed_{seed}.log"
    summary_file = output_directory / f"h0_summary_seed_{seed}.xml"
    detector_file = repository_root() / raw["detector_file_template"].format(seed=seed)
    detector_output_file = repository_root() / raw["detector_output_template"].format(seed=seed)
    detector_summary_file = repository_root() / raw["detector_summary_template"].format(seed=seed)
    write_virtual_detector_file(
        detector_file,
        detector_output_file,
        prepared.virtual_detectors,
    )
    trajectory_options = []
    if trajectory_output is not None:
        span = prepared.demand_profile[-1].end_seconds - raw["warmup_seconds"]
        period = trajectory_period_seconds
        if (
            not math.isfinite(period)
            or period <= 0
            or not math.isclose(period / 0.5, round(period / 0.5))
            or not math.isclose(span / period, round(span / period))
        ):
            raise ValueError("Trajectory period must divide the window and match the 0.5 s step.")
        trajectory_options = [
            "--fcd-output",
            str(trajectory_output),
            "--fcd-output.attributes",
            "id,speed,acceleration,lane",
            "--fcd-output.skip-empty",
            "false",
            "--device.fcd.begin",
            str(raw["warmup_seconds"]),
            "--device.fcd.period",
            str(trajectory_period_seconds),
            "--device.fcd.probability",
            "1",
            "--device.fcd.deterministic",
            "true",
            "--tripinfo-output.write-unfinished",
            "true",
            "--tripinfo-output.write-undeparted",
            "true",
        ]
    command = [
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
        "--summary-output",
        str(summary_file),
        "--log",
        str(log_file),
        "--no-step-log",
        "true",
        "--duration-log.disable",
        "true",
        "--xml-validation",
        "never",
        *trajectory_options,
    ]
    if controller is None:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    else:
        run_controlled(
            command,
            prepared.simulation_end_seconds,
            controller,
            output_directory / "controller_diagnostics.json",
            prepared.human_parameters["minGap"],
        )
    final_step = ElementTree.parse(summary_file).getroot().findall("step")[-1].attrib
    log_lines = log_file.read_text().splitlines()
    warning_lines = [
        line
        for line in log_lines
        if any(
            word in line.lower()
            for word in ("warning", "error", "teleport", "collision", "emergency")
        )
    ]
    vehicle_types: dict[str, int] = defaultdict(int)
    for _, trip in ElementTree.iterparse(tripinfo_file, events=("end",)):
        if trip.tag == "tripinfo" and float(trip.attrib.get("arrival", "0")) >= 0:
            vehicle_types[trip.attrib.get("vType", "unknown")] += 1
            trip.clear()
    (output_directory / f"h0_run_health_seed_{seed}.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "final_summary": final_step,
                "warning_lines": warning_lines,
                "completed_vehicle_types": dict(vehicle_types),
            },
            indent=2,
        )
        + "\n"
    )
    detector_intervals = summarize_virtual_detector_output(
        detector_output_file,
        {
            spec.station_id: {int(lane.rsplit("_", 1)[1]) for lane in spec.lane_ids}
            for spec in prepared.virtual_detectors
            if spec.recorded_lane_ids is not None
        },
    )
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
