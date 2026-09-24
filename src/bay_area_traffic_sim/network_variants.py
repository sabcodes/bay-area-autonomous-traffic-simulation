"""Build isolated network variants for documented geometry sensitivities."""

from __future__ import annotations

import subprocess
from pathlib import Path
from xml.etree import ElementTree

import sumolib

from bay_area_traffic_sim.sumo_install import binary


def build_sr85_two_lane_variant(
    base_network: Path,
    output_network: Path,
    plain_directory: Path,
    ramp_edge_id: str = "11479095",
    feeder_edge_id: str = "1343445177",
    merge_edge_id: str = "509747406",
    merge_lane_targets: tuple[int, int] = (5, 5),
) -> Path:
    """Build a separate two-lane SR-85 connector sensitivity network.

    This hypothetical maps PeMS station 402920 to the one-lane OSM-derived HOV
    connector and adds a second lane on that edge. VTA documents a separate
    general-purpose ramp at the interchange, so station-to-path identity is
    unresolved and must not be inferred from proximity. The sensitivity
    explicitly splits the two rightmost feeder lanes across the connector; the
    requested pair maps connector lanes 0 and 1 to their target lanes at the
    US-101 merge. This is a topology experiment, not an assertion that PeMS
    detector lanes align with those SUMO lanes.
    """

    if not base_network.is_file():
        raise FileNotFoundError(f"Base SUMO network not found: {base_network}")
    generated_files = {
        "network.nod.xml",
        "network.edg.xml",
        "network.con.xml",
        "network.tll.xml",
        "network.typ.xml",
        "network.netccfg",
        "variant.edg.xml",
        "variant.con.xml",
    }
    if plain_directory.exists():
        unexpected = {path.name for path in plain_directory.iterdir()} - generated_files
        if unexpected:
            raise FileExistsError(
                f"Refusing to overwrite non-generated files in {plain_directory}: "
                f"{sorted(unexpected)}"
            )
    plain_directory.mkdir(parents=True, exist_ok=True)
    prefix = plain_directory / "network"
    subprocess.run(
        [
            str(binary("netconvert")),
            "--sumo-net-file",
            str(base_network),
            "--plain-output-prefix",
            str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )

    edge_file = prefix.with_suffix(".edg.xml")
    connection_file = prefix.with_suffix(".con.xml")
    edge_tree = ElementTree.parse(edge_file)
    edge = edge_tree.find(f".//edge[@id='{ramp_edge_id}']")
    if edge is None:
        raise ValueError(f"Ramp edge {ramp_edge_id} is missing from {edge_file}.")
    if edge.get("numLanes") != "1":
        raise ValueError(
            f"Expected {ramp_edge_id} to have one lane, got {edge.get('numLanes')!r}."
        )
    edge_patch = ElementTree.Element("edges")
    ElementTree.SubElement(edge_patch, "edge", {"id": ramp_edge_id, "numLanes": "2"})

    connection_tree = ElementTree.parse(connection_file)
    connections = connection_tree.getroot()
    feeder_connections = [
        item
        for item in connections.findall("connection")
        if item.get("from") == feeder_edge_id and item.get("to") == ramp_edge_id
    ]
    if len(feeder_connections) != 1 or feeder_connections[0].get("fromLane") != "4":
        raise ValueError(
            f"Expected exactly one audited feeder connection from lane 4 of "
            f"{feeder_edge_id} to {ramp_edge_id}; found "
            f"{[(item.get('fromLane'), item.get('toLane')) for item in feeder_connections]}"
        )
    merge_connections = [
        item
        for item in connections.findall("connection")
        if item.get("from") == ramp_edge_id and item.get("to") == merge_edge_id
    ]
    if len(merge_connections) != 1 or merge_connections[0].get("toLane") != "5":
        raise ValueError(
            f"Expected exactly one audited merge connection from {ramp_edge_id} "
            f"to lane 5 of {merge_edge_id}; found "
            f"{[(item.get('fromLane'), item.get('toLane')) for item in merge_connections]}"
        )
    connection_patch = ElementTree.Element("connections")
    ElementTree.SubElement(
        connection_patch,
        "connection",
        {"from": feeder_edge_id, "to": ramp_edge_id, "fromLane": "3", "toLane": "1"},
    )
    if merge_lane_targets[0] != 5:
        ElementTree.SubElement(
            connection_patch,
            "delete",
            {"from": ramp_edge_id, "to": merge_edge_id, "fromLane": "0", "toLane": "5"},
        )
        ElementTree.SubElement(
            connection_patch,
            "connection",
            {
                "from": ramp_edge_id,
                "to": merge_edge_id,
                "fromLane": "0",
                "toLane": str(merge_lane_targets[0]),
            },
        )
    for from_lane, to_lane in (("1", str(merge_lane_targets[1])),):
        ElementTree.SubElement(
            connection_patch,
            "connection",
            {
                "from": ramp_edge_id,
                "to": merge_edge_id,
                "fromLane": from_lane,
                "toLane": to_lane,
            },
        )
    edge_patch_path = plain_directory / "variant.edg.xml"
    connection_patch_path = plain_directory / "variant.con.xml"
    ElementTree.ElementTree(edge_patch).write(
        edge_patch_path, encoding="utf-8", xml_declaration=True
    )
    ElementTree.ElementTree(connection_patch).write(
        connection_patch_path, encoding="utf-8", xml_declaration=True
    )

    output_network.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(binary("netconvert")),
            "--sumo-net-file",
            str(base_network),
            "--edge-files",
            str(edge_patch_path),
            "--connection-files",
            str(connection_patch_path),
            "--output-file",
            str(output_network),
        ],
        check=True,
    )

    network = sumolib.net.readNet(str(output_network))
    ramp = network.getEdge(ramp_edge_id)
    if len(ramp.getLanes()) != 2:
        raise RuntimeError(f"Built network does not contain two lanes on {ramp_edge_id}.")
    feeder = network.getEdge(feeder_edge_id)
    merge = network.getEdge(merge_edge_id)
    feeder_links = {
        (connection.getFromLane().getIndex(), connection.getToLane().getIndex())
        for connection in feeder.getOutgoing().get(ramp, [])
    }
    merge_links = {
        (connection.getFromLane().getIndex(), connection.getToLane().getIndex())
        for lane in ramp.getLanes()
        for connection in lane.getOutgoing()
        if connection.getToLane().getEdge() == merge
    }
    if feeder_links != {(3, 1), (4, 0)}:
        raise RuntimeError(f"Unexpected feeder lane mapping into {ramp_edge_id}: {feeder_links}")
    expected_merge_links = {(0, merge_lane_targets[0]), (1, merge_lane_targets[1])}
    if merge_links != expected_merge_links:
        raise RuntimeError(
            f"Unexpected lane mapping from {ramp_edge_id} to {merge_edge_id}: {merge_links}"
        )
    return output_network
