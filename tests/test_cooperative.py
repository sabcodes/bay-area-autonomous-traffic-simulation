"""M5 native policy, paired measurement and actual SUMO contract checks."""

import json
import subprocess
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from xml.etree import ElementTree as ET

import pytest

from bay_area_traffic_sim.cooperative import (
    DEFAULT_CONTROLLER,
    apply_native_cacc,
    run_controlled,
    validate_controller,
)
from bay_area_traffic_sim.experiment_harness import paired_comparisons, validate_experiment
from bay_area_traffic_sim.experiment_metrics import read_insertion_metrics
from bay_area_traffic_sim.sumo_install import binary
from bay_area_traffic_sim.toy_corridor import build_network

PARAMETERS = {"tau": 1.5, "accel": 2.6, "decel": 4.5}


@pytest.mark.parametrize(
    "key,value",
    [
        ("policy", "unknown"),
        ("backend", "unknown"),
        ("unknown", 0),
        ("observation_period_seconds", 0.7),
        ("observation_period_seconds", True),
        ("leader_lookahead_meters", float("nan")),
        ("leader_lookahead_meters", 0),
    ],
)
def test_invalid_native_policy_rejected(key, value):
    with pytest.raises(ValueError):
        validate_controller({**DEFAULT_CONTROLLER, key: value}, PARAMETERS)


@pytest.mark.parametrize(
    "key,value",
    [
        ("collisionAvoidanceOverride", 2),
        ("collisionMinGapFactor", 0.1),
        ("tauCACCToACC", 1),
        ("speedControlGainCACC", float("nan")),
        ("gapControlGainGap", 0.46),
        ("unknown", 0),
    ],
)
def test_native_safety_and_fixed_gains_rejected(key, value):
    config = deepcopy(DEFAULT_CONTROLLER)
    config["vehicle_parameters"][key] = value
    with pytest.raises(ValueError):
        validate_controller(config, PARAMETERS)


def test_native_route_transform_changes_only_declared_passenger_attributes(tmp_path):
    route = tmp_path / "route.xml"
    route.write_text(
        '<routes><vType id="human_passenger" carFollowModel="Krauss" '
        'tau="1.5" length="5" probability="0.96"/>'
        '<vType id="human_truck" carFollowModel="Krauss" probability="0.04"/>'
        '<route id="r" edges="a b"/><flow id="f" route="r" number="10"/></routes>'
    )
    original = ET.parse(route).getroot()
    kinds = apply_native_cacc(route, DEFAULT_CONTROLLER)
    treated = ET.parse(route).getroot()
    passenger = treated.find("vType")
    assert passenger.attrib["carFollowModel"] == "CACC"
    for key, value in DEFAULT_CONTROLLER["vehicle_parameters"].items():
        assert float(passenger.attrib[key]) == value
    for key, value in original.find("vType").attrib.items():
        if key != "carFollowModel":
            assert passenger.attrib[key] == value
    assert [child.attrib for child in list(original)[1:]] == [
        child.attrib for child in list(treated)[1:]
    ]
    assert kinds == [kind.attrib for kind in treated.iter("vType")]
    route.write_text("<routes/>")
    with pytest.raises(ValueError, match="passenger"):
        apply_native_cacc(route, DEFAULT_CONTROLLER)


def test_physical_comparison_guard(tmp_path, monkeypatch):
    from bay_area_traffic_sim import experiment_harness as harness

    monkeypatch.setattr(
        harness,
        "_load_baseline_config",
        lambda path, root: {
            "human_parameters": {**PARAMETERS, "tau": 2 if str(path) == "other" else 1.5}
        },
    )
    config = {
        "experiment_id": "test",
        "seeds": [41, 42],
        "observation_dates": ["2025-10-08"],
        "measurement": {"period_seconds": 1, "stop_speed_m_per_s": 0.1},
        "output_directory": "outputs/test",
        "reference_scenario": "H0",
        "scenarios": [
            {"id": "H0", "baseline_config": "base"},
            {
                "id": "CACC",
                "baseline_config": "other",
                "controller": deepcopy(DEFAULT_CONTROLLER),
            },
        ],
    }
    config["scenarios"][1]["controller"]["vehicle_parameters"]["tauCACCToACC"] = 2
    with pytest.raises(ValueError, match="Scenarios differ"):
        validate_experiment(config, tmp_path)


def test_pairing_hand_calculation_and_missing_or_failed_pair():
    metric = "cohort_mean_travel_time_seconds"
    report = {
        "experiment": {
            "reference_scenario": "H0",
            "scenarios": [{"id": "CACC"}, {"id": "H0"}],
            "observation_dates": ["2025-10-08"],
            "seeds": [41, 42],
        },
        "runs": [
            {
                "scenario": name,
                "date": "2025-10-08",
                "seed": seed,
                "accepted": True,
                "metrics": {metric: value},
            }
            for name, seed, value in [
                ("H0", 41, 10),
                ("H0", 42, 20),
                ("CACC", 41, 12),
                ("CACC", 42, 24),
            ]
        ],
    }
    result = paired_comparisons(report)[0]["metrics"][metric]
    assert result["mean_difference"] == 3
    assert result["sample_standard_deviation"] == pytest.approx(2**0.5)
    assert result["percent_of_reference_mean"] == 20
    assert result["pairs"] == [{"seed": 41, "difference": 2}, {"seed": 42, "difference": 4}]
    for mode in ["missing", "failed", "null"]:
        broken = deepcopy(report)
        if mode == "missing":
            broken["runs"].pop()
        elif mode == "failed":
            broken["runs"][-1]["accepted"] = False
        else:
            broken["runs"][-1]["metrics"][metric] = None
        assert paired_comparisons(broken)[0]["metrics"][metric]["mean_difference"] is None


def test_insertion_populations_and_half_open_boundaries(tmp_path):
    trips, summary = tmp_path / "trips.xml", tmp_path / "summary.xml"
    trips.write_text("""<tripinfos>
      <tripinfo depart="10" departDelay="2" arrival="20" duration="10"/>
      <tripinfo depart="20" departDelay="10" arrival="40" duration="20"/>
      <tripinfo depart="30" departDelay="10" arrival="-1" duration="0"/>
      <tripinfo depart="40" departDelay="10" arrival="50" duration="10"/>
    </tripinfos>""")
    summary.write_text("""<summary><step time="9" waiting="9"/>
      <step time="10" waiting="5"/><step time="30" waiting="8"/></summary>""")
    metrics = read_insertion_metrics(trips, summary, 10, 30)
    assert metrics["window_actual_departures"] == 2
    assert metrics["scheduled_cohort_vehicles"] == 2
    assert metrics["scheduled_cohort_completed_vehicles"] == 1
    assert metrics["scheduled_cohort_mean_depart_delay_seconds"] == 10
    assert metrics["scheduled_cohort_mean_total_time_seconds"] == 30
    assert metrics["whole_run_mean_depart_delay_seconds"] == 8
    assert metrics["peak_insertion_backlog_vehicles"] == 9
    assert metrics["window_peak_insertion_backlog_vehicles"] == 5
    trips.write_text('<tripinfos><tripinfo depart="-1" departDelay="-1" arrival="-1"/></tripinfos>')
    metrics = read_insertion_metrics(trips, summary, 10, 30)
    assert metrics["scheduled_cohort_vehicles"] is None
    assert metrics["unreconstructed_scheduled_departures"] == 1


def test_real_sumo_controller_clears_and_replays_deterministically(tmp_path):
    network = build_network(tmp_path)
    source = Path(__file__).resolve().parents[1] / "network/toy_corridor"
    edges = tmp_path / "single_lane.edg.xml"
    edges.write_text(
        (source / "toy_corridor.edg.xml").read_text().replace('numLanes="2"', 'numLanes="1"')
    )
    subprocess.run(
        [
            str(binary("netconvert")),
            "--node-files",
            str(source / "toy_corridor.nod.xml"),
            "--edge-files",
            str(edges),
            "--output-file",
            str(network),
        ],
        check=True,
        capture_output=True,
    )
    # Truck departs first, then passenger leaders/followers. Natural leader changes
    # occur as vehicles exit; no controller lane-change or safety-mode override.
    route = tmp_path / "routes.xml"
    route.write_text("""<routes>
      <vType id="human_passenger" accel="2.6" decel="4.5" emergencyDecel="9"
        sigma="0.5" tau="1.5" minGap="2.5"/>
      <vType id="human_truck" vClass="truck" accel="1.2" decel="4"
        emergencyDecel="9" tau="1.5" maxSpeed="15"/>
      <route id="route" edges="main_in main_out"/>
      <vehicle id="truck" type="human_truck" route="route" depart="0" departLane="0"/>
      <flow id="passengers" type="human_passenger" route="route" begin="4" end="35"
        period="3" departLane="0"/>
    </routes>""")
    apply_native_cacc(route, DEFAULT_CONTROLLER)
    results = []
    for replay, backend in enumerate(["traci", "traci", "libsumo"]):
        trips, log = tmp_path / f"trips{replay}.xml", tmp_path / f"run{replay}.log"
        command = [
            str(binary("sumo")),
            "-n",
            str(network),
            "-r",
            str(route),
            "--seed",
            "41",
            "--step-length",
            "0.5",
            "--end",
            "500",
            "--tripinfo-output",
            str(trips),
            "--log",
            str(log),
            "--no-step-log",
            "true",
            "--duration-log.disable",
            "true",
        ]
        diagnostics = run_controlled(
            command,
            500,
            {**DEFAULT_CONTROLLER, "backend": backend},
            tmp_path / f"diagnostics{replay}.json",
            2.5,
        )
        records = [trip.attrib for trip in ET.parse(trips).getroot().findall("tripinfo")]
        results.append((diagnostics, records))
        assert len(records) == 12
        assert diagnostics["equipped_vehicles"] == 11
        assert diagnostics["passenger_samples"] > 0
        assert diagnostics["passenger_leader_samples"] > 0
        assert diagnostics["truck_leader_samples"] > 0
        assert diagnostics["no_leader_samples"] > 0
        assert diagnostics["missing_state_samples"] == 0
        assert diagnostics["minimum_queried_bumper_gap_meters"] >= 0
        assert diagnostics["completed"]
        assert diagnostics["mode_sample_counts"]["ACC"] > 0
        assert (
            sum(v for k, v in diagnostics["mode_sample_counts"].items() if k.startswith("CACC_"))
            > 0
        )
        assert diagnostics["external_control_commands"] == 0
        assert not any(
            word in log.read_text().lower()
            for word in ["warning", "collision", "teleport", "emergency", "error"]
        )
        assert json.loads((tmp_path / f"diagnostics{replay}.json").read_text()) == diagnostics
    assert results[0] == results[1]
    assert results[0][1] == results[2][1]  # Same numeric trip attributes across engines.
    for key in results[0][0]:
        if key not in {"controller", "backend"}:
            assert results[0][0][key] == results[2][0][key], key


def test_native_missing_state_and_error_cleanup_without_speed_commands(tmp_path, monkeypatch):
    import traci
    from traci import constants as tc

    closed = []
    state = {tc.VAR_SPEED: 10, tc.VAR_ACCELERATION: 0, tc.VAR_TYPE: "human_passenger"}
    vehicle = SimpleNamespace(
        subscribe=lambda *args: None,
        getSubscriptionResults=lambda _: state,
        getSpeedMode=lambda _: 31,
        getLaneChangeMode=lambda _: 1621,
        getAllSubscriptionResults=lambda: {},
        getLeader=lambda *args: ("", -1),
        getParameter=lambda *args: "CC",
    )
    connection = SimpleNamespace(
        simulationStep=lambda: None,
        vehicle=vehicle,
        simulation=SimpleNamespace(
            subscribe=lambda *args: None,
            getSubscriptionResults=lambda: {
                tc.VAR_DEPARTED_VEHICLES_IDS: ["ego"],
                tc.VAR_ARRIVED_VEHICLES_IDS: [],
            },
        ),
        close=lambda: closed.append(True),
        getVersion=lambda: (22, "SUMO 1.27.1"),
    )
    monkeypatch.setattr(traci, "start", lambda *args, **kwargs: None)
    monkeypatch.setattr(traci, "getConnection", lambda _: connection)
    path = tmp_path / "diagnostics.json"
    config = {**DEFAULT_CONTROLLER, "backend": "traci", "observation_period_seconds": 0.5}
    result = run_controlled([], 0.5, config, path, 2.5)
    assert result["missing_state_samples"] == 1
    assert result["external_control_commands"] == 0
    vehicle.getAllSubscriptionResults = lambda: {"ego": state}

    def fail(*args):
        raise RuntimeError("query failure")

    vehicle.getParameter = fail
    with pytest.raises(RuntimeError, match="query failure"):
        run_controlled([], 0.5, config, path, 2.5)
    assert len(closed) == 2
    assert not json.loads(path.read_text())["completed"]


def test_native_cacc_preserves_strategic_exit(tmp_path):
    import subprocess

    nodes, edges, links = [tmp_path / name for name in ["nodes.xml", "edges.xml", "links.xml"]]
    nodes.write_text(
        '<nodes><node id="s" x="0" y="0"/>'
        '<node id="j" x="1000" y="0"/>'
        '<node id="e" x="2000" y="0"/>'
        '<node id="x" x="1300" y="-300"/></nodes>'
    )
    edges.write_text(
        '<edges><edge id="approach" from="s" to="j" numLanes="3" speed="30"/>'
        '<edge id="through" from="j" to="e" numLanes="3" speed="30"/>'
        '<edge id="exit" from="j" to="x" numLanes="1" speed="20"/></edges>'
    )
    links.write_text(
        "<connections>"
        + "".join(
            f'<connection from="approach" to="through" fromLane="{lane}" toLane="{lane}"/>'
            for lane in range(3)
        )
        + '<connection from="approach" to="exit" fromLane="0" toLane="0"/></connections>'
    )
    network, route, trips = [tmp_path / name for name in ["network.xml", "routes.xml", "trips.xml"]]
    subprocess.run(
        [
            str(binary("netconvert")),
            "-n",
            str(nodes),
            "-e",
            str(edges),
            "-x",
            str(links),
            "-o",
            str(network),
        ],
        check=True,
        capture_output=True,
    )
    route.write_text(
        '<routes><vType id="human_passenger" tau="1.5" accel="2.6" decel="4.5"/>'
        '<route id="exit_route" edges="approach exit"/>'
        '<vehicle id="exit_car" type="human_passenger" route="exit_route" '
        'depart="0" departLane="2"/></routes>'
    )
    log = tmp_path / "sumo.log"
    command = [
        str(binary("sumo")),
        "-n",
        str(network),
        "-r",
        str(route),
        "--step-length",
        "0.5",
        "--end",
        "150",
        "--seed",
        "41",
        "--tripinfo-output",
        str(trips),
        "--log",
        str(log),
        "--no-step-log",
        "true",
        "--duration-log.disable",
        "true",
    ]
    apply_native_cacc(route, DEFAULT_CONTROLLER)
    result = run_controlled(command, 150, DEFAULT_CONTROLLER, tmp_path / "diagnostics.json", 2.5)
    assert result["equipped_vehicles"] == 1
    assert result["passenger_samples"] > 0 and result["missing_state_samples"] == 0
    assert len(ET.parse(trips).getroot().findall("tripinfo")) == 1
    assert not any(
        word in log.read_text().lower()
        for word in ["warning", "collision", "teleport", "emergency", "error"]
    )
