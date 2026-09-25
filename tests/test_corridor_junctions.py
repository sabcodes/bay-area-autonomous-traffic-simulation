"""The lane ledger must cover both through routes without a ramp shortcut."""

import json
from pathlib import Path

import pytest

from bay_area_traffic_sim.corridor_junctions import build_lane_connection_audit

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/us101_lane_connection_audit.json"
NETWORK = ROOT / "outputs/us101_corridor/us101_corridor.net.xml"
ROUTE = ROOT / "outputs/us101_corridor/h0_human_baseline.rou.xml"


def test_audit_configuration_requires_a_southbound_through_checkpoint() -> None:
    raw = json.loads(CONFIG.read_text())
    northbound, southbound = raw["routes"]
    assert northbound["name"] == "northbound"
    assert southbound["name"] == "southbound"
    assert southbound["checkpoint_edge_ids"] == ["619117737", "867247243", "867204829"]


def test_full_route_ledger_rejects_sr85_ramp_shortcut(tmp_path: Path) -> None:
    if not NETWORK.is_file() or not ROUTE.is_file():
        pytest.skip("Build the ignored US-101 network and H0 route before the integration audit")

    report = build_lane_connection_audit(CONFIG)
    northbound, southbound = report["routes"]
    assert (northbound["edge_count"], northbound["transition_count"]) == (37, 36)
    assert (southbound["edge_count"], southbound["transition_count"]) == (36, 35)
    assert all(edge["lane_count"] >= 4 for route in report["routes"] for edge in route["edges"])
    assert all(
        transition["through_lane_links"] and transition["passenger_through_lane_links"]
        for route in report["routes"]
        for transition in route["transitions"]
    )
    branches = [
        branch
        for route in report["routes"]
        for transition in route["transitions"]
        for field in ("incoming_branches", "outgoing_branches")
        for branch in transition[field]
    ]
    assert len(branches) == 40
    assert all(branch["corridor_paths"] for branch in branches)
    assert all(
        path["edge_ids"][0] == branch["edge_id"]
        for branch in branches
        for path in branch["corridor_paths"]
    )
    assert report["branch_path_endpoint_counts"]["depth_limit_unresolved"] == 0
    assert report["branch_path_endpoint_counts"]["cycle_unresolved"] == 0
    southbound_ids = {edge["edge_id"] for edge in southbound["edges"]}
    assert "867247243" in southbound_ids
    assert "394382945" not in southbound_ids
    assert "9899589" not in southbound_ids

    shoreline_split = next(
        transition
        for transition in northbound["transitions"]
        if transition["from_edge_id"] == "1343740299"
    )
    assert [branch["edge_id"] for branch in shoreline_split["outgoing_branches"]] == [
        "5005672"
    ]
    assert all(
        path["endpoint"] == "surface_or_other_road"
        for path in shoreline_split["outgoing_branches"][0]["corridor_paths"]
    )
    warned_nb_branch = northbound["transitions"][28]["incoming_branches"][0]
    assert warned_nb_branch["edge_id"] == "685973436"
    assert any(
        "690599564#0" in path["edge_ids"]
        for path in warned_nb_branch["corridor_paths"]
    )
    warned_sb_branch = southbound["transitions"][11]["outgoing_branches"][0]
    assert warned_sb_branch["edge_id"] == "8924695"
    assert any(
        "348360455" in path["edge_ids"]
        for path in warned_sb_branch["corridor_paths"]
    )
    sr85_split = next(
        transition
        for transition in southbound["transitions"]
        if transition["from_edge_id"] == "706447588-AddedOffRampEdge"
    )
    assert sr85_split["to_edge_id"] == "867247243"
    assert [branch["edge_id"] for branch in sr85_split["outgoing_branches"]] == [
        "394382945"
    ]

    bad_config = json.loads(CONFIG.read_text())
    bad_config["routes"][1]["checkpoint_edge_ids"] = ["619117737", "867204829"]
    bad_config["routes"][1]["expected_edge_count"] = 41
    bad_path = tmp_path / "unguided.json"
    bad_path.write_text(json.dumps(bad_config))
    with pytest.raises(ValueError, match="unexpected narrow links"):
        build_lane_connection_audit(bad_path)
