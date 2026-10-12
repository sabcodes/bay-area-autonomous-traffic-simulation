"""Create PeMS-aligned SUMO induction loops and summarize their output."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Set
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean
from xml.etree import ElementTree

import sumolib
from sumolib import geomhelper

from bay_area_traffic_sim.network_audit import _match_station_to_network
from bay_area_traffic_sim.pems_metadata import MetadataStation, select_corridor_stations

METERS_PER_SECOND_TO_MPH = 2.2369362921


@dataclass(frozen=True)
class VirtualDetectorSpec:
    """Lane-level SUMO loops representing one PeMS mainline station."""

    station_id: int
    station_name: str
    edge_id: str
    lane_ids: list[str]
    position_meters: float
    reported_lane_count: int | None = None
    recorded_lane_ids: list[str] | None = None


@dataclass(frozen=True)
class VirtualDetectorInterval:
    """One station-level five-minute interval aggregated across its lanes."""

    station_id: int
    begin_seconds: float
    end_seconds: float
    contributing_vehicles: int
    flow_vehicles_per_hour: float
    speed_mph: float | None
    mean_lane_occupancy_percent: float


def build_virtual_detector_specs(
    network_file: Path,
    metadata_files: Iterable[Path],
    bounding_box: Mapping[str, float],
    station_ids: Set[int],
    lane_indices: Mapping[int, list[int]] | None = None,
) -> list[VirtualDetectorSpec]:
    """Place virtual loops at selected PeMS coordinates on their matched road edges."""

    network = sumolib.net.readNet(str(network_file))
    selected = select_corridor_stations(metadata_files, bounding_box).stations
    stations_by_id: dict[int, MetadataStation] = {}
    for station in selected:
        if station.station_id in station_ids:
            stations_by_id.setdefault(station.station_id, station)

    missing = station_ids - stations_by_id.keys()
    if missing:
        message = f"Selected virtual-detector stations are missing metadata: {sorted(missing)}"
        raise ValueError(message)

    specs: list[VirtualDetectorSpec] = []
    for station_id in sorted(stations_by_id):
        station = stations_by_id[station_id]
        match = _match_station_to_network(station, network)
        if match.nearest_edge_id is None:
            raise ValueError(f"Station {station_id} has no matched SUMO edge.")
        edge = network.getEdge(match.nearest_edge_id)
        point = network.convertLonLat2XY(station.longitude, station.latitude)
        position, _ = geomhelper.polygonOffsetAndDistanceToPoint(point, edge.getShape())
        lane_count = min(station.lanes or edge.getLaneNumber(), edge.getLaneNumber())
        indices = (lane_indices or {}).get(station_id)
        if indices is None:
            lanes = edge.getLanes()[-lane_count:]
        else:
            if (
                not indices
                or len(set(indices)) != len(indices)
                or any(index < 0 or index >= edge.getLaneNumber() for index in indices)
            ):
                raise ValueError(f"Invalid lane indices for station {station_id}: {indices}")
            lanes = [edge.getLanes()[index] for index in indices]
        recorded_lanes = edge.getLanes() if indices is not None else lanes
        maximum_position = min(lane.getLength() for lane in recorded_lanes) - 1
        specs.append(
            VirtualDetectorSpec(
                station_id=station_id,
                station_name=station.name,
                edge_id=edge.getID(),
                lane_ids=[lane.getID() for lane in lanes],
                position_meters=max(1.0, min(position, maximum_position)),
                reported_lane_count=station.lanes,
                recorded_lane_ids=(
                    [lane.getID() for lane in recorded_lanes] if indices is not None else None
                ),
            )
        )
    return specs


def write_virtual_detector_file(
    destination: Path,
    detector_output_file: Path,
    specs: Iterable[VirtualDetectorSpec],
    period_seconds: int = 300,
) -> None:
    """Write one induction loop per represented mainline lane."""

    root = ElementTree.Element("additional")
    for spec in specs:
        for lane_index, lane_id in enumerate(spec.recorded_lane_ids or spec.lane_ids):
            if spec.recorded_lane_ids is not None:
                lane_index = int(lane_id.rsplit("_", 1)[1])
            ElementTree.SubElement(
                root,
                "inductionLoop",
                {
                    "id": f"pems_{spec.station_id}_lane_{lane_index}",
                    "lane": lane_id,
                    "pos": f"{spec.position_meters:.2f}",
                    "period": str(period_seconds),
                    "file": str(detector_output_file),
                    "friendlyPos": "true",
                },
            )
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree = ElementTree.ElementTree(root)
    ElementTree.indent(tree, space="    ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def summarize_virtual_detector_output(
    path: Path, lane_indices: Mapping[int, Set[int]] | None = None
) -> list[VirtualDetectorInterval]:
    """Aggregate lane-level induction-loop output into PeMS-like station intervals."""

    grouped: defaultdict[tuple[int, float, float], list[ElementTree.Element]] = defaultdict(list)
    for interval in ElementTree.parse(path).getroot().findall("interval"):
        detector_id = interval.attrib["id"]
        if not detector_id.startswith("pems_"):
            continue
        station_id = int(detector_id.split("_", maxsplit=3)[1])
        if lane_indices and station_id in lane_indices:
            physical_lane = int(detector_id.rsplit("_", 1)[1])
            if physical_lane not in lane_indices[station_id]:
                continue
        begin = float(interval.attrib["begin"])
        end = float(interval.attrib["end"])
        grouped[(station_id, begin, end)].append(interval)

    summaries: list[VirtualDetectorInterval] = []
    for (station_id, begin, end), intervals in sorted(grouped.items()):
        vehicle_counts = [int(float(interval.attrib["nVehContrib"])) for interval in intervals]
        total_vehicles = sum(vehicle_counts)
        valid_speeds = [
            (float(interval.attrib["speed"]), count)
            for interval, count in zip(intervals, vehicle_counts, strict=True)
            if count > 0 and float(interval.attrib["speed"]) >= 0
        ]
        weighted_speed = (
            sum(speed * count for speed, count in valid_speeds)
            / sum(count for _, count in valid_speeds)
            if valid_speeds
            else None
        )
        summaries.append(
            VirtualDetectorInterval(
                station_id=station_id,
                begin_seconds=begin,
                end_seconds=end,
                contributing_vehicles=total_vehicles,
                flow_vehicles_per_hour=sum(
                    float(interval.attrib["flow"]) for interval in intervals
                ),
                speed_mph=(
                    weighted_speed * METERS_PER_SECOND_TO_MPH
                    if weighted_speed is not None
                    else None
                ),
                mean_lane_occupancy_percent=fmean(
                    float(interval.attrib["occupancy"]) for interval in intervals
                ),
            )
        )
    return summaries


def detector_specs_as_dict(specs: Iterable[VirtualDetectorSpec]) -> list[dict[str, object]]:
    return [asdict(spec) for spec in specs]
