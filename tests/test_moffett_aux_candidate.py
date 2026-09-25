"""Guard the provisional Moffett-to-Shoreline lane-layout sensitivity."""

import json
import subprocess
from pathlib import Path
from xml.etree import ElementTree

import pytest
import sumolib

from bay_area_traffic_sim.sumo_install import binary

ROOT = Path(__file__).resolve().parents[1]
BASE_NETWORK = ROOT / "outputs/us101_corridor/us101_corridor.net.xml"
PATCH_DIRECTORY = ROOT / "network/us101_corridor/patches"


def _links(network: sumolib.net.Net, source_id: str, target_id: str) -> set[tuple[int, int]]:
    source = network.getEdge(source_id)
    target = network.getEdge(target_id)
    return {
        (connection.getFromLane().getIndex(), connection.getToLane().getIndex())
        for connection in source.getOutgoing().get(target, [])
    }


def _all_links(network: sumolib.net.Net) -> set[tuple[str, int, str, int]]:
    return {
        (
            edge.getID(),
            connection.getFromLane().getIndex(),
            connection.getTo().getID(),
            connection.getToLane().getIndex(),
        )
        for edge in network.getEdges()
        for connections in edge.getOutgoing().values()
        for connection in connections
    }


def _patch_link(element: ElementTree.Element) -> tuple[str, int, str, int]:
    return (
        element.attrib["from"],
        int(element.attrib["fromLane"]),
        element.attrib["to"],
        int(element.attrib["toLane"]),
    )


def test_candidate_config_keeps_all_generated_outputs_separate() -> None:
    config = json.loads(
        (ROOT / "configs/us101_human_baseline_moffett_aux_candidate.json").read_text()
    )
    output_keys = (
        "network_file",
        "aligned_pems_report_file",
        "route_file",
        "manifest_file",
        "detector_file_template",
        "detector_output_template",
        "detector_summary_template",
    )
    assert config["extends"] == "configs/us101_human_baseline.json"
    output_prefix = "outputs/us101_corridor/moffett_aux_five_lane/"
    assert all(config[key].startswith(output_prefix) for key in output_keys)
    assert ElementTree.parse(PATCH_DIRECTORY / "moffett_aux_five_lane.edg.xml").getroot().find(
        "edge"
    ).attrib == {"id": "617335302", "numLanes": "5"}


def test_candidate_rebuild_has_expected_lane_connections(tmp_path: Path) -> None:
    if not BASE_NETWORK.is_file():
        pytest.skip("Build the ignored base US-101 network before testing the candidate rebuild")

    baseline = sumolib.net.readNet(str(BASE_NETWORK))
    assert baseline.getEdge("617335302").getLaneNumber() == 4
    assert _links(baseline, "1343740299", "617335302") == {
        (2, 0), (3, 1), (4, 2), (5, 3)
    }
    assert _links(baseline, "617335302", "361615811") == {
        (0, 1), (1, 2), (2, 3), (3, 4)
    }

    candidate_file = tmp_path / "moffett_aux_five_lane.net.xml"
    subprocess.run(
        [
            str(binary("netconvert")),
            "--sumo-net-file",
            str(BASE_NETWORK),
            "--edge-files",
            str(PATCH_DIRECTORY / "moffett_aux_five_lane.edg.xml"),
            "--connection-files",
            str(PATCH_DIRECTORY / "moffett_aux_five_lane.con.xml"),
            "--output-file",
            str(candidate_file),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    candidate = sumolib.net.readNet(str(candidate_file))
    assert candidate.getEdge("617335302").getLaneNumber() == 5
    assert _links(candidate, "1343740299", "617335302") == {
        (1, 0), (2, 1), (3, 2), (4, 3), (5, 4)
    }
    assert _links(candidate, "617335302", "361615811") == {
        (0, 0), (1, 1), (2, 2), (3, 3), (4, 4)
    }
    assert _links(candidate, "1343740299", "5005672") == {(0, 0), (1, 1)}
    assert _links(candidate, "394387883", "361615811") == {(0, 0)}

    identity_file = tmp_path / "identity_rebuild.net.xml"
    subprocess.run(
        [
            str(binary("netconvert")),
            "--sumo-net-file",
            str(BASE_NETWORK),
            "--output-file",
            str(identity_file),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    identity = sumolib.net.readNet(str(identity_file))
    identity_edges = {edge.getID(): edge for edge in identity.getEdges()}
    candidate_edges = {edge.getID(): edge for edge in candidate.getEdges()}
    assert identity_edges.keys() == candidate_edges.keys()
    assert {
        edge_id: (edge.getLaneNumber(), candidate_edges[edge_id].getLaneNumber())
        for edge_id, edge in identity_edges.items()
        if edge.getLaneNumber() != candidate_edges[edge_id].getLaneNumber()
    } == {"617335302": (4, 5)}

    connection_patch = ElementTree.parse(
        PATCH_DIRECTORY / "moffett_aux_five_lane.con.xml"
    ).getroot()
    assert _all_links(identity) - _all_links(candidate) == {
        _patch_link(element) for element in connection_patch.findall("delete")
    }
    assert _all_links(candidate) - _all_links(identity) == {
        _patch_link(element) for element in connection_patch.findall("connection")
    }
