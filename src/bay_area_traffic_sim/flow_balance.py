"""Diagnose net traffic gains and losses between ordered PeMS stations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean
from typing import Any
from xml.etree import ElementTree

import sumolib

COMPLEX_STATION_LABELS = ("rm-", "coll", "diag")


@dataclass(frozen=True)
class OrderedFlowStation:
    """One observed station placed along the SUMO mainline route."""

    station_id: int
    station_name: str
    edge_id: str
    route_distance_meters: float
    represented_lanes: int
    reported_lanes: int
    mean_flow_vehicles_per_hour: float
    flow_by_time: dict[str, float]
    cautions: list[str]
    full_cross_section_confirmed: bool = False


def _route_edge_ids(route_file: Path, route_id: str) -> list[str]:
    route = ElementTree.parse(route_file).getroot().find(f"route[@id='{route_id}']")
    if route is None or not route.attrib.get("edges"):
        raise ValueError(f"Route {route_id!r} is missing from {route_file}.")
    return route.attrib["edges"].split()


def _observed_profiles(report: dict[str, Any]) -> dict[int, dict[str, float]]:
    profiles: dict[int, dict[str, float]] = {}
    for profile in report.get("summary", {}).get("profiles", []):
        station_id = int(profile["station_id"])
        profiles[station_id] = {
            str(point["time"]): float(point["mean_flow_vehicles_per_5_minutes"]) * 12
            for point in profile["time_profile"]
        }
    if not profiles:
        raise ValueError("Observed station profile report contains no profiles.")
    return profiles


def order_observed_stations(
    observed_report: dict[str, Any],
    manifest: dict[str, Any],
    route_file: Path,
    network_file: Path,
    audit: dict[str, Any] | None = None,
) -> list[OrderedFlowStation]:
    """Place reporting detector profiles in northbound route order."""

    profiles = _observed_profiles(observed_report)
    audit = audit or {}
    accepted_ids = {
        int(station_id) for station_id in audit.get("accepted_full_cross_section_station_ids", [])
    }
    excluded_ids = {int(station_id) for station_id in audit.get("excluded_station_ids", [])}
    route_edges = _route_edge_ids(route_file, "us101_northbound")
    network = sumolib.net.readNet(str(network_file))
    edge_offsets: dict[str, float] = {}
    offset = 0.0
    for edge_id in route_edges:
        if edge_id in edge_offsets:
            raise ValueError(f"Mainline route repeats edge {edge_id}; ordering is ambiguous.")
        edge_offsets[edge_id] = offset
        offset += network.getEdge(edge_id).getLength()

    ordered: list[OrderedFlowStation] = []
    for detector in manifest.get("virtual_detectors", []):
        station_id = int(detector["station_id"])
        if station_id not in profiles or station_id in excluded_ids:
            continue
        edge_id = str(detector["edge_id"])
        if edge_id not in edge_offsets:
            continue
        name = str(detector["station_name"])
        confirmed = station_id in accepted_ids
        cautions = []
        if not confirmed and any(marker in name.lower() for marker in COMPLEX_STATION_LABELS):
            cautions.append("Station label suggests ramp, diagonal, or collector-road context.")
        represented_lanes = len(detector["lane_ids"])
        reported_lanes = int(detector.get("reported_lane_count") or represented_lanes)
        if represented_lanes != reported_lanes:
            cautions.append(
                "PeMS reports a different lane count than the mapped SUMO edge "
                f"({reported_lanes} versus {represented_lanes})."
            )
        flow_by_time = profiles[station_id]
        ordered.append(
            OrderedFlowStation(
                station_id=station_id,
                station_name=name,
                edge_id=edge_id,
                route_distance_meters=(edge_offsets[edge_id] + float(detector["position_meters"])),
                represented_lanes=represented_lanes,
                reported_lanes=reported_lanes,
                mean_flow_vehicles_per_hour=fmean(flow_by_time.values()),
                flow_by_time=flow_by_time,
                cautions=cautions,
                full_cross_section_confirmed=confirmed,
            )
        )
    return sorted(ordered, key=lambda station: station.route_distance_meters)


def compare_adjacent_stations(
    stations: list[OrderedFlowStation],
) -> list[dict[str, object]]:
    """Calculate observed net flow changes and label unsafe comparisons."""

    segments: list[dict[str, object]] = []
    for upstream, downstream in zip(stations[:-1], stations[1:], strict=True):
        common_times = sorted(upstream.flow_by_time.keys() & downstream.flow_by_time.keys())
        if not common_times:
            continue
        changes = [
            downstream.flow_by_time[time] - upstream.flow_by_time[time] for time in common_times
        ]
        cautions = [*upstream.cautions, *downstream.cautions]
        if upstream.reported_lanes != downstream.reported_lanes and not (
            upstream.full_cross_section_confirmed and downstream.full_cross_section_confirmed
        ):
            cautions.append(
                "Represented lane count changes between the two stations "
                f"({upstream.reported_lanes} to {downstream.reported_lanes})."
            )
        mean_change = fmean(changes)
        segments.append(
            {
                "upstream_station_id": upstream.station_id,
                "downstream_station_id": downstream.station_id,
                "distance_meters": (
                    downstream.route_distance_meters - upstream.route_distance_meters
                ),
                "matched_intervals": len(common_times),
                "mean_net_flow_change_vehicles_per_hour": mean_change,
                "interpretation": (
                    "net_inflow"
                    if mean_change > 0
                    else "net_outflow"
                    if mean_change < 0
                    else "balanced"
                ),
                "minimum_interval_change_vehicles_per_hour": min(changes),
                "maximum_interval_change_vehicles_per_hour": max(changes),
                "usable_for_missing_ramp_estimation": not cautions,
                "cautions": sorted(set(cautions)),
            }
        )
    return segments


def build_flow_balance_report(
    observed_profile_file: Path,
    manifest_file: Path,
    route_file: Path,
    network_file: Path,
    audit_file: Path | None = None,
) -> dict[str, object]:
    """Build an auditable observed flow-conservation diagnostic."""

    stations = order_observed_stations(
        json.loads(observed_profile_file.read_text()),
        json.loads(manifest_file.read_text()),
        route_file,
        network_file,
        json.loads(audit_file.read_text()) if audit_file else None,
    )
    if len(stations) < 2:
        raise ValueError("At least two ordered reporting stations are required.")
    segments = compare_adjacent_stations(stations)
    return {
        "observed_profile_file": str(observed_profile_file),
        "manifest_file": str(manifest_file),
        "route_file": str(route_file),
        "network_file": str(network_file),
        "audit_file": str(audit_file) if audit_file else None,
        "ordered_stations": [asdict(station) for station in stations],
        "segments": segments,
        "summary": {
            "reporting_stations": len(stations),
            "adjacent_segments": len(segments),
            "usable_segments": sum(
                bool(segment["usable_for_missing_ramp_estimation"]) for segment in segments
            ),
            "review_required_segments": sum(
                not bool(segment["usable_for_missing_ramp_estimation"]) for segment in segments
            ),
        },
        "limitation": (
            "A net flow change combines every entrance, exit, detector error, and lane-coverage "
            "difference between two stations. It is not assigned to an individual ramp until "
            "the station pair and intervening ramps are audited."
        ),
    }
