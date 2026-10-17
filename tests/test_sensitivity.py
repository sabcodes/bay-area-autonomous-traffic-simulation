"""M7 contract checks: selection, message age, scaling, suppression and null control."""

import hashlib
import json
from collections import deque
from copy import deepcopy
from xml.etree import ElementTree as ET

import pytest

from bay_area_traffic_sim.cooperative import (
    DEFAULT_CONTROLLER,
    hash_fraction,
    is_equipped,
    received_acceleration,
    run_controlled,
    validate_controller,
)
from bay_area_traffic_sim.real_corridor import DemandPoint, scale_demand
from bay_area_traffic_sim.sensitivity import distribution, summarize, validate_campaign
from bay_area_traffic_sim.sumo_install import binary
from bay_area_traffic_sim.toy_corridor import build_network, repository_root

PARAMETERS = {"tau": 1.5, "accel": 2.6, "decel": 4.5}


def test_scaling_preserves_targets_and_does_not_mutate_source():
    points = [DemandPoint("07:00", 900, 1200, 1000, 45)]
    assert scale_demand(points, 1) == points
    scaled = scale_demand(points, 1.2)
    assert scaled[0].vehicles_per_hour == 1200
    assert scaled[0].observed_speed_mph == 45
    assert points[0].vehicles_per_hour == 1000
    for invalid in [0, -1, True, float("nan"), float("inf"), "1"]:
        with pytest.raises(ValueError):
            scale_demand(points, invalid)


def test_independent_hash_selection_and_strict_boundaries():
    value = int(hashlib.sha256(b"equipment|car").hexdigest()[:16], 16) / (1 << 64)
    assert value == hash_fraction("equipment|car")
    assert not is_equipped("car", value)
    assert is_equipped("car", value + 1e-12)
    assert not is_equipped("car", 0) and is_equipped("car", 1)
    names = [f"car_{i}" for i in range(1000)]
    assert {v for v in names if is_equipped(v, 0.5)} == {
        v for v in reversed(names) if is_equipped(v, 0.5)
    }


def test_extra_delay_tracks_same_leader_and_drops_without_stale_hold():
    config = {**DEFAULT_CONTROLLER, "message_delay_seconds": 1.0}
    history = deque(maxlen=3)
    history.append({"leader": 2})
    assert received_acceleration(config, "ego", "leader", 0, history) == (None, "unavailable")
    history.extend([{"leader": 3}, {"leader": 4, "new": 8}])
    assert received_acceleration(config, "ego", "leader", 2, history) == (2, "delivered")
    assert received_acceleration(config, "ego", "new", 2, history) == (None, "unavailable")
    loss = {**config, "message_loss_probability": 1}
    assert received_acceleration(loss, "ego", "leader", 2, history) == (None, "lost")
    assert received_acceleration(DEFAULT_CONTROLLER, "ego", "leader", 2, [{"leader": -2}]) == (
        -2,
        "delivered",
    )


@pytest.mark.parametrize(
    "key,value",
    [
        ("penetration", -0.1),
        ("penetration", 1.1),
        ("penetration", True),
        ("message_delay_seconds", -0.5),
        ("message_delay_seconds", 0.1),
        ("message_delay_seconds", 5.5),
        ("message_loss_probability", float("nan")),
        ("message_loss_probability", 1.1),
        ("message_loss_probability", True),
    ],
)
def test_invalid_extension_rejected(key, value):
    with pytest.raises(ValueError):
        validate_controller({**DEFAULT_CONTROLLER, key: value}, PARAMETERS)


def test_frozen_matrix_and_matching_demand_guard():
    root = repository_root()
    config = json.loads((root / "configs/us101_m7_sensitivity.json").read_text())
    validate_campaign(config, root)
    assert sum(len(c["seeds"]) * len(c["policies"]) for c in config["cases"]) == 54
    config["cases"][3]["demand_scale"] = 0.8
    with pytest.raises(ValueError, match="matching-demand"):
        validate_campaign(config, root)


def test_complete_population_spread_and_failure_suppression():
    assert distribution([1, 3], 2) == {
        "valid_seed_count": 2,
        "mean": 2,
        "sample_standard_deviation": 2**0.5,
        "minimum": 1,
        "maximum": 3,
    }
    for values in [[1, None], [1, float("nan")], [1, float("inf")], [1]]:
        assert distribution(values, 2)["mean"] is None
    config = {
        "cases": [
            {"id": "base", "seeds": [41, 42], "policies": {"H0": {}}},
            {"id": "half", "seeds": [41, 42], "policies": {"CACC": {}}},
        ]
    }
    metric = "cohort_mean_travel_time_seconds"
    runs = [
        {"case": case, "scenario": name, "seed": seed, "accepted": True, "metrics": {metric: x}}
        for case, name, seed, x in [
            ("base", "H0", 41, 10),
            ("base", "H0", 42, 20),
            ("half", "CACC", 41, 12),
            ("half", "CACC", 42, 24),
        ]
    ]
    pair = summarize(config, runs)[1]["paired_metrics"][metric]
    assert pair["mean"] == 3 and pair["sample_standard_deviation"] == pytest.approx(2**0.5)
    assert pair["percent_of_reference_mean"] == 20 and pair["positive_count"] == 2
    for mode in ["missing", "failed", "nonfinite"]:
        changed = deepcopy(runs)
        if mode == "missing":
            changed.pop()
        elif mode == "failed":
            changed[-1]["accepted"] = False
        else:
            changed[-1]["metrics"][metric] = float("nan")
        assert summarize(config, changed)[1]["paired_metrics"][metric]["mean"] is None


def test_real_sumo_zero_equipment_exactly_matches_native_and_degraded_replays(tmp_path):
    import subprocess

    network = build_network(tmp_path)
    route = tmp_path / "routes.xml"
    route.write_text("""<routes><vType id="human_passenger" tau="1.5" accel="2.6" decel="4.5"/>
      <route id="r" edges="main_in main_out"/>
      <flow id="cars" type="human_passenger" route="r" begin="0" end="40" period="2"/>
      </routes>""")
    outputs = []
    for i, controller in enumerate(
        [
            None,
            {**DEFAULT_CONTROLLER, "penetration": 0},
            {
                **DEFAULT_CONTROLLER,
                "penetration": 0.5,
                "message_delay_seconds": 1,
                "message_loss_probability": 0.2,
            },
            {
                **DEFAULT_CONTROLLER,
                "penetration": 0.5,
                "message_delay_seconds": 1,
                "message_loss_probability": 0.2,
            },
        ]
    ):
        trips, log = tmp_path / f"{i}.xml", tmp_path / f"{i}.log"
        command = [
            str(binary("sumo")),
            "-n",
            str(network),
            "-r",
            str(route),
            "--seed",
            "41",
            "--step-length",
            ".5",
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
        if controller is None:
            subprocess.run(command, check=True, capture_output=True)
        else:
            d = run_controlled(command, 500, controller, tmp_path / f"{i}.json", 2.5)
            assert d["completed"] and d["native_fallbacks"] == 0
            assert (
                d["messages_delivered"] + d["messages_lost"] + d["messages_unavailable"]
                == d["message_opportunities"]
            )
            if i >= 2:
                assert 0 < d["controlled_vehicles"] < d["eligible_vehicles"]
                assert d["messages_delivered"] > 0 and d["messages_lost"] > 0
            if i == 1:
                assert d["controlled_vehicles"] == d["commands"] == d["equipped_samples"] == 0
                assert d["eligible_vehicles"] == 20
        outputs.append([t.attrib for t in ET.parse(trips).getroot().findall("tripinfo")])
        assert not any(
            w in log.read_text().lower() for w in ["warning", "collision", "teleport", "error"]
        )
    assert outputs[0] == outputs[1] and outputs[2] == outputs[3]
    assert json.loads((tmp_path / "2.json").read_text()) == json.loads(
        (tmp_path / "3.json").read_text()
    )
