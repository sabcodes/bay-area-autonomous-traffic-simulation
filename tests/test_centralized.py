"""M6 spec checks: rule boundaries, input gates, runtime timing and restoration."""

import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from xml.etree import ElementTree as ET

import pytest

from bay_area_traffic_sim.centralized import (
    DEFAULT_CONTROLLER,
    congestion_mode,
    next_limit,
    observed_totals,
    run_controlled,
    validate_controller,
)
from bay_area_traffic_sim.cooperative import validate_controller as validate_policy
from bay_area_traffic_sim.sumo_install import binary
from bay_area_traffic_sim.toy_corridor import build_network


def test_hand_calculated_rule_and_strict_boundaries():
    c = DEFAULT_CONTROLLER
    assert observed_totals([(2, 10), (1, 40), (0, -1)]) == (3, 60)
    assert congestion_mode(c, False, 14.99)
    assert not congestion_mode(c, False, 15)
    assert congestion_mode(c, True, 20)
    assert not congestion_mode(c, True, 20.01)
    assert not congestion_mode(c, True, None)
    assert next_limit(c, 29.06, 29.06, True) == 28.06
    assert next_limit(c, 25.06, 29.06, True) == 25
    assert next_limit(c, 25, 29.06, False) == 26
    assert next_limit(c, 29, 29.06, False) == 29.06
    assert next_limit(c, 20, 20, True) == 20  # never raise a lower native limit
    for sample in [[(-1, 0)], [(True, 0)], [(1, float("nan"))], [(1, -1)]]:
        with pytest.raises(ValueError):
            observed_totals(sample)


@pytest.mark.parametrize(
    "key,value",
    [
        ("policy", "bad"),
        ("backend", "traci"),
        ("update_seconds", 0.7),
        ("update_seconds", True),
        ("control_end_seconds", 31),
        ("activate_below_m_per_s", 20),
        ("max_change_m_per_s", -1),
        ("congested_limit_m_per_s", float("inf")),
        ("control_edge_ids", []),
        ("control_edge_ids", ["x", "x"]),
        ("control_edge_ids", [":internal"]),
        ("observation_edge_ids", ["395354963"]),
        ("observation_edge_ids", [None]),
        ("extra", 1),
    ],
)
def test_invalid_settings(key, value):
    config = {**DEFAULT_CONTROLLER, key: value}
    with pytest.raises(ValueError):
        validate_controller(config)
    with pytest.raises(ValueError):
        validate_policy(config, {"tau": 1.5, "accel": 2.6, "decel": 4.5})


def test_fake_runtime_interval_clearance_and_error_cleanup(tmp_path, monkeypatch):
    import libsumo

    ticks, calls, closed = [0], [], []
    lane = SimpleNamespace(
        getIDList=lambda: ["up_0", "down_0"],
        getEdgeID=lambda lane: lane.split("_")[0],
        getMaxSpeed=lambda _: 29,
        getLastStepVehicleNumber=lambda _: 2,
        getLastStepMeanSpeed=lambda _: 10,
        setMaxSpeed=lambda lane, value: calls.append((ticks[0], lane, value)),
    )
    monkeypatch.setattr(libsumo, "lane", lane)
    monkeypatch.setattr(libsumo, "start", lambda _: None)
    monkeypatch.setattr(libsumo, "getVersion", lambda: (22, "SUMO 1.27.1"))
    monkeypatch.setattr(libsumo, "simulationStep", lambda: ticks.__setitem__(0, ticks[0] + 1))
    monkeypatch.setattr(libsumo, "close", lambda: closed.append(True))
    c = {
        **DEFAULT_CONTROLLER,
        "control_edge_ids": ["up"],
        "observation_edge_ids": ["down"],
        "update_seconds": 1,
        "control_end_seconds": 3,
    }
    path = tmp_path / "diagnostics.json"
    d = run_controlled([], 4, c, path)
    assert [r["time_seconds"] for r in d["ledger"]] == [1, 2, 3, 4]
    assert [r["lane_limits"]["up_0"] for r in d["ledger"]] == [28, 27, 28, 29]
    assert [r["vehicle_samples"] for r in d["ledger"]] == [4, 4, 4, 0]
    assert d["limited_lane_seconds"] == 3
    assert d["completed"] and d["restored"] and closed == [True]
    assert calls[-1] == (8, "up_0", 29)
    assert json.loads(path.read_text()) == d

    def fail():
        raise RuntimeError("injected step failure")

    monkeypatch.setattr(libsumo, "simulationStep", fail)
    with pytest.raises(RuntimeError, match="injected"):
        run_controlled([], 4, c, path)
    failed = json.loads(path.read_text())
    assert not failed["completed"] and failed["restored"]
    assert len(closed) == 2
    with pytest.raises(ValueError, match="Unknown"):
        run_controlled([], 4, {**c, "control_edge_ids": ["missing"]}, path)
    assert not json.loads(path.read_text())["completed"]
    assert len(closed) == 3


def test_real_sumo_replay_and_visible_actuation(tmp_path):
    network = build_network(tmp_path)
    route = tmp_path / "routes.xml"
    route.write_text(
        '<routes><vType id="human_passenger" tau="1.5"/>'
        '<route id="r" edges="main_in main_out"/>'
        '<flow id="f" type="human_passenger" route="r" '
        'begin="0" end="50" period="3"/></routes>'
    )
    c = {
        **DEFAULT_CONTROLLER,
        "control_edge_ids": ["main_in"],
        "observation_edge_ids": ["main_out"],
        "activate_below_m_per_s": 35,
        "release_above_m_per_s": 40,
        "congested_limit_m_per_s": 15,
        "update_seconds": 5,
        "control_end_seconds": 90,
    }
    results = []
    for replay in range(2):
        trip, log = tmp_path / f"trips{replay}.xml", tmp_path / f"run{replay}.log"
        d = run_controlled(
            [
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
                str(trip),
                "--log",
                str(log),
                "--no-step-log",
                "true",
                "--duration-log.disable",
                "true",
            ],
            500,
            c,
            tmp_path / f"diagnostics{replay}.json",
        )
        trips = [t.attrib for t in ET.parse(trip).getroot().findall("tripinfo")]
        assert len(trips) == 17
        assert d["completed"] and d["restored"]
        assert d["commands"] > 0 and d["limited_lane_seconds"] > 0
        assert any(r["congested"] for r in d["ledger"])
        assert not any(
            w in log.read_text().lower()
            for w in ["warning", "error", "teleport", "collision", "emergency"]
        )
        results.append((d, trips))
    assert results[0] == results[1]


def test_central_comparison_rejects_physical_changes(tmp_path, monkeypatch):
    from bay_area_traffic_sim import experiment_harness as h

    c = json.loads((Path(__file__).parents[1] / "configs/us101_m6_experiment.json").read_text())
    base = {"human_parameters": {"tau": 1.5, "accel": 2.6, "decel": 4.5}, "warmup_seconds": 900}
    monkeypatch.setattr(h, "_load_baseline_config", lambda *args: deepcopy(base))
    h.validate_experiment(c, tmp_path)

    def changed(path, root):
        return {
            **base,
            "human_parameters": {
                **base["human_parameters"],
                "tau": 2 if str(path) == "other" else 1.5,
            },
        }

    monkeypatch.setattr(h, "_load_baseline_config", changed)
    c["scenarios"][-1]["baseline_config"] = "other"
    with pytest.raises(ValueError, match="Scenarios differ"):
        h.validate_experiment(c, tmp_path)
