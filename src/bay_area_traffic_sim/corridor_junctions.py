"""Inventory every modeled lane transition and side connection on study routes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import sumolib

from bay_area_traffic_sim.toy_corridor import repository_root


def _connections(source: Any, destination: Any) -> list[dict[str, object]]:
    """Return all directed lane links from one SUMO edge to another."""

    return sorted(
        (
            {
                "from_lane": connection.getFromLane().getIndex(),
                "to_lane": connection.getToLane().getIndex(),
                "direction": connection.getDirection(),
            }
            for connection in source.getOutgoing().get(destination, [])
        ),
        key=lambda link: (link["from_lane"], link["to_lane"]),
    )


def _route_from_file(network: Any, path: Path, route_id: str) -> list[Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Route file not found: {path}")
    route = ElementTree.parse(path).find(f".//route[@id='{route_id}']")
    if route is None:
        raise ValueError(f"Route {route_id!r} is missing from {path}")
    return [network.getEdge(edge_id) for edge_id in route.attrib["edges"].split()]


def _route_via_checkpoints(network: Any, edge_ids: list[str]) -> list[Any]:
    if len(edge_ids) < 2:
        raise ValueError("A guided route needs at least two checkpoints")
    checkpoints = [network.getEdge(edge_id) for edge_id in edge_ids]
    route: list[Any] = []
    for source, destination in zip(checkpoints[:-1], checkpoints[1:], strict=True):
        segment, _ = network.getShortestPath(source, destination)
        if not segment:
            raise ValueError(f"No path from {source.getID()} to {destination.getID()}")
        route.extend(segment if not route else segment[1:])
    return route


def _edge_record(edge: Any) -> dict[str, object]:
    return {
        "edge_id": edge.getID(),
        "lane_count": edge.getLaneNumber(),
        "length_meters": edge.getLength(),
        "road_type": edge.getType(),
        "passenger_allowed_lanes": [
            lane.getIndex() for lane in edge.getLanes() if lane.allows("passenger")
        ],
    }


def _branch_record(source: Any, destination: Any, branch: Any) -> dict[str, object]:
    return {
        "edge_id": branch.getID(),
        "lane_count": branch.getLaneNumber(),
        "road_type": branch.getType(),
        "passenger_allowed_lanes": [
            lane.getIndex() for lane in branch.getLanes() if lane.allows("passenger")
        ],
        "lane_links": _connections(source, destination),
    }


def _transition_record(
    network: Any, source: Any, destination: Any, index: int
) -> dict[str, object]:
    if source.getToNode().getID() != destination.getFromNode().getID():
        raise ValueError(f"Disconnected route edges: {source.getID()} → {destination.getID()}")
    through_links = _connections(source, destination)
    if not through_links:
        raise ValueError(f"No lane connection: {source.getID()} → {destination.getID()}")
    passenger_links = [
        link
        for link in through_links
        if source.getLanes()[link["from_lane"]].allows("passenger")
        and destination.getLanes()[link["to_lane"]].allows("passenger")
    ]
    if not passenger_links:
        raise ValueError(
            f"No passenger-permitted lane connection: {source.getID()} → {destination.getID()}"
        )

    outgoing = [
        _branch_record(source, branch, branch)
        for branch in source.getOutgoing()
        if branch != destination
    ]
    incoming = [
        _branch_record(branch, destination, branch)
        for branch in destination.getIncoming()
        if branch != source
    ]
    longitude, latitude = network.convertXY2LonLat(*source.getToNode().getCoord())
    return {
        "index": index,
        "from_edge_id": source.getID(),
        "to_edge_id": destination.getID(),
        "junction_id": source.getToNode().getID(),
        "latitude": latitude,
        "longitude": longitude,
        "from_lane_count": source.getLaneNumber(),
        "to_lane_count": destination.getLaneNumber(),
        "through_lane_links": through_links,
        "passenger_through_lane_links": passenger_links,
        "outgoing_branches": sorted(outgoing, key=lambda item: item["edge_id"]),
        "incoming_branches": sorted(incoming, key=lambda item: item["edge_id"]),
    }


def _passenger_successors(edge: Any, direction: str) -> list[Any]:
    """Follow only lane links usable by passenger vehicles."""

    neighbors = edge.getOutgoing() if direction == "outgoing" else edge.getIncoming()
    permitted = []
    for neighbor in neighbors:
        source, destination = (
            (edge, neighbor) if direction == "outgoing" else (neighbor, edge)
        )
        if any(
            source.getLanes()[link["from_lane"]].allows("passenger")
            and destination.getLanes()[link["to_lane"]].allows("passenger")
            for link in _connections(source, destination)
        ):
            permitted.append(neighbor)
    return sorted(permitted, key=lambda item: item.getID())


def _trace_branch(
    network: Any, branch_id: str, direction: str, through_edge_routes: dict[str, str]
) -> list[dict[str, object]]:
    """Trace legal forks to the first trunk road, surface road, or graph boundary."""

    maximum_depth = 24
    maximum_paths = 100
    paths: list[dict[str, object]] = []
    start = network.getEdge(branch_id)
    pending = [([start], {branch_id})]
    while pending:
        chain, seen = pending.pop()
        edge = chain[-1]
        edge_type = edge.getType()
        if len(chain) > 1 and edge.getID() in through_edge_routes:
            endpoint = "audited_through_route"
        elif len(chain) > 1 and edge_type == "highway.motorway" and edge.getLaneNumber() >= 2:
            endpoint = "other_motorway"
        elif edge_type not in {"highway.motorway", "highway.motorway_link"}:
            endpoint = "surface_or_other_road"
        elif len(chain) >= maximum_depth:
            endpoint = "depth_limit_unresolved"
        else:
            neighbors = _passenger_successors(edge, direction)
            if not neighbors:
                endpoint = "graph_boundary_or_disallowed"
            else:
                for neighbor in reversed(neighbors):
                    if neighbor.getID() in seen:
                        paths.append(
                            {
                                "edge_ids": [item.getID() for item in chain]
                                + [neighbor.getID()],
                                "endpoint": "cycle_unresolved",
                            }
                        )
                    else:
                        pending.append((chain + [neighbor], seen | {neighbor.getID()}))
                if len(paths) + len(pending) > maximum_paths:
                    raise ValueError(f"Branch {branch_id} exceeds {maximum_paths} paths")
                continue
        record: dict[str, object] = {
            "edge_ids": [item.getID() for item in chain],
            "endpoint": endpoint,
        }
        if endpoint == "audited_through_route":
            record["endpoint_route"] = through_edge_routes[edge.getID()]
        paths.append(record)
    return sorted(paths, key=lambda item: item["edge_ids"])


def build_lane_connection_audit(config_path: Path) -> dict[str, object]:
    """Report complete route-edge and lane-link inventory, without certifying geometry."""

    root = repository_root()
    config_file = config_path if config_path.is_absolute() else root / config_path
    config = json.loads(config_file.read_text())
    network_file = root / config["network_file"]
    if not network_file.is_file():
        raise FileNotFoundError(f"SUMO network not found: {network_file}")
    network = sumolib.net.readNet(str(network_file))

    routes: list[dict[str, object]] = []
    for specification in config["routes"]:
        if "route_file" in specification:
            route_edges = _route_from_file(
                network, root / specification["route_file"], specification["route_id"]
            )
        else:
            route_edges = _route_via_checkpoints(network, specification["checkpoint_edge_ids"])
        expected = int(specification["expected_edge_count"])
        if len(route_edges) != expected:
            raise ValueError(
                f"{specification['name']} route has {len(route_edges)} edges, expected {expected}"
            )
        minimum_lanes = int(specification["minimum_lane_count"])
        too_narrow = [
            edge.getID() for edge in route_edges if edge.getLaneNumber() < minimum_lanes
        ]
        if too_narrow:
            raise ValueError(
                f"{specification['name']} route has unexpected narrow links: {too_narrow}"
            )
        transitions = [
            _transition_record(network, source, destination, index)
            for index, (source, destination) in enumerate(
                zip(route_edges[:-1], route_edges[1:], strict=True)
            )
        ]
        routes.append(
            {
                "name": specification["name"],
                "edge_count": len(route_edges),
                "transition_count": len(transitions),
                "branch_transition_count": sum(
                    bool(transition["incoming_branches"] or transition["outgoing_branches"])
                    for transition in transitions
                ),
                "edges": [_edge_record(edge) for edge in route_edges],
                "transitions": transitions,
            }
        )
    through_edge_routes = {
        edge["edge_id"]: route["name"]
        for route in routes
        for edge in route["edges"]
    }
    for route in routes:
        for transition in route["transitions"]:
            for direction, field in (
                ("incoming", "incoming_branches"),
                ("outgoing", "outgoing_branches"),
            ):
                for branch in transition[field]:
                    branch["corridor_paths"] = _trace_branch(
                        network, branch["edge_id"], direction, through_edge_routes
                    )
    return {
        "network_file": str(network_file),
        "config_file": str(config_file),
        "routes": routes,
        "branch_path_endpoint_counts": {
            endpoint: sum(
                path["endpoint"] == endpoint
                for route in routes
                for transition in route["transitions"]
                for field in ("incoming_branches", "outgoing_branches")
                for branch in transition[field]
                for path in branch["corridor_paths"]
            )
            for endpoint in (
                "audited_through_route",
                "other_motorway",
                "surface_or_other_road",
                "graph_boundary_or_disallowed",
                "depth_limit_unresolved",
                "cycle_unresolved",
            )
        },
        "limitation": (
            "This inventories the configured through routes and passenger-legal side paths "
            "to the first trunk/surface road or an explicit search bound. Stopping at a trunk "
            "does not verify a complete interchange movement, current lane markings, or "
            "ramp safety."
        ),
    }
