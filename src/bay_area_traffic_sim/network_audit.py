"""Match PeMS station coordinates to the draft SUMO network for manual review."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

import sumolib

from bay_area_traffic_sim.pems_metadata import MetadataStation, select_corridor_stations


@dataclass(frozen=True)
class StationNetworkMatch:
    """The closest non-internal SUMO edge to one PeMS station coordinate."""

    station_id: int
    station_name: str
    latitude: float
    longitude: float
    nearest_edge_id: str | None
    nearest_edge_name: str | None
    nearest_edge_lanes: int | None
    distance_meters: float | None


@dataclass(frozen=True)
class NetworkAudit:
    """Automatic evidence that still needs human review at complex interchanges."""

    network_file: str
    station_count: int
    matches: list[StationNetworkMatch]

    def as_dict(self) -> dict[str, object]:
        """Return JSON-ready output for an audit record."""

        return asdict(self)


def audit_network(
    network_file: Path, source_files: Iterable[Path], bounding_box: Mapping[str, float]
) -> NetworkAudit:
    """Find the nearest draft-network edge to every candidate corridor station."""

    if not network_file.is_file():
        raise FileNotFoundError(f"SUMO network not found: {network_file}")

    network = sumolib.net.readNet(str(network_file))
    selected_stations = select_corridor_stations(source_files, bounding_box).stations
    stations = _unique_stations(selected_stations)
    matches = [_match_station_to_network(station, network) for station in stations]
    return NetworkAudit(
        network_file=str(network_file), station_count=len(stations), matches=matches
    )


def _unique_stations(stations: Iterable[MetadataStation]) -> list[MetadataStation]:
    """Keep one coordinate record per station across metadata snapshots."""

    by_station_id: dict[int, MetadataStation] = {}
    for station in stations:
        by_station_id.setdefault(station.station_id, station)
    return [by_station_id[station_id] for station_id in sorted(by_station_id)]


def _match_station_to_network(station: MetadataStation, network: object) -> StationNetworkMatch:
    x, y = network.convertLonLat2XY(station.longitude, station.latitude)
    nearby = network.getNeighboringEdges(x, y, 250)
    usable_edges = [
        (edge, distance) for edge, distance in nearby if not edge.getID().startswith(":")
    ]
    if not usable_edges:
        return StationNetworkMatch(
            station_id=station.station_id,
            station_name=station.name,
            latitude=station.latitude,
            longitude=station.longitude,
            nearest_edge_id=None,
            nearest_edge_name=None,
            nearest_edge_lanes=None,
            distance_meters=None,
        )

    edge, distance = min(usable_edges, key=lambda match: match[1])
    return StationNetworkMatch(
        station_id=station.station_id,
        station_name=station.name,
        latitude=station.latitude,
        longitude=station.longitude,
        nearest_edge_id=edge.getID(),
        nearest_edge_name=edge.getName() or None,
        nearest_edge_lanes=edge.getLaneNumber(),
        distance_meters=distance,
    )
