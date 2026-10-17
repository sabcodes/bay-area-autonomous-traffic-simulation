"""Acceptance examples for the M4 metric contract and failure handling."""

import gzip
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bay_area_traffic_sim import experiment_harness as harness
from bay_area_traffic_sim.experiment_metrics import (
    clean_and_cleared,
    entrance_queue_edges,
    read_trajectory_metrics,
    read_window_trip_metrics,
)
from bay_area_traffic_sim.metrics import METERS_PER_SECOND_TO_MPH, RunMetrics, read_tripinfo


def _trajectory(path: Path, body: str) -> None:
    with gzip.open(path, "wt") as stream:
        stream.write(f"<fcd-export>{body}</fcd-export>")


def test_metric_contract_hand_calculated_windows_thresholds_and_empty_samples(tmp_path):
    path = tmp_path / "fcd.xml.gz"
    _trajectory(
        path,
        """
        <timestep time="0"><vehicle speed="100" acceleration="100" lane="r_0"/></timestep>
        <timestep time="1"><vehicle speed="0" acceleration="2" lane="r_0"/>
          <vehicle speed="0.1" acceleration="-2" lane="m_0"/></timestep>
        <timestep time="2"/>
        <timestep time="3"><vehicle speed="10" acceleration="0" lane="m_0"/></timestep>
        <timestep time="4"><vehicle speed="100" acceleration="100" lane="r_0"/></timestep>
    """,
    )
    metrics = read_trajectory_metrics(path, 1, 4, 1, 0.1, {"r"})
    assert metrics["trajectory_timesteps"] == 3
    assert metrics["vehicle_samples"] == 3
    assert metrics["mean_stopped_vehicles"] == pytest.approx(1 / 3)
    assert metrics["peak_stopped_vehicles"] == 1
    assert metrics["stopped_vehicle_seconds"] == 1
    assert metrics["mean_ramp_stopped_vehicles"] == pytest.approx(1 / 3)
    assert metrics["temporal_mean_speed_stddev_mph"] == pytest.approx(
        (10 - 0.05) / 2 * METERS_PER_SECOND_TO_MPH
    )
    assert metrics["mean_squared_acceleration_m2_per_s4"] == pytest.approx(8 / 3)
    assert metrics["rms_acceleration_m_per_s2"] == pytest.approx((8 / 3) ** 0.5)
    _trajectory(path, '<timestep time="1"/><timestep time="2"/>')
    empty = read_trajectory_metrics(path, 1, 3, 1, 0.1, set())
    assert empty["peak_stopped_vehicles"] == 0
    assert empty["mean_squared_acceleration_m2_per_s4"] is None
    assert empty["temporal_mean_speed_stddev_mph"] is None
    with pytest.raises(ValueError, match="Expected 3"):
        read_trajectory_metrics(path, 1, 4, 1, 0.1, set())
    _trajectory(path, '<timestep time="1"/><timestep time="3"/>')
    with pytest.raises(ValueError, match="irregular"):
        read_trajectory_metrics(path, 1, 4, 1, 0.1, set())


def test_trip_cohort_and_exit_counts_use_different_boundaries(tmp_path):
    path = tmp_path / "trips.xml"
    path.write_text("""<tripinfos>
      <tripinfo depart="0" arrival="10" duration="10" waitingTime="0" timeLoss="0"/>
      <tripinfo depart="10" arrival="20" duration="10" waitingTime="2" timeLoss="4"/>
      <tripinfo depart="15" arrival="35" duration="20" waitingTime="4" timeLoss="6"/>
      <tripinfo depart="30" arrival="40" duration="10" waitingTime="0" timeLoss="0"/>
      <tripinfo depart="11" arrival="-1" duration="50" waitingTime="9" timeLoss="9"/>
      <tripinfo depart="-1" arrival="-1" duration="0" waitingTime="0" timeLoss="0"/>
    </tripinfos>""")
    result = read_window_trip_metrics(path, 10, 30)
    assert result["window_exit_vehicles"] == 2
    assert result["cohort_completed_vehicles"] == 2
    assert result["cohort_unfinished_vehicles"] == 1
    assert result["cohort_mean_travel_time_seconds"] == 15
    assert result["cohort_p95_travel_time_seconds"] == 19.5
    assert result["cohort_mean_waiting_time_seconds"] == 3
    assert result["cohort_mean_time_loss_seconds"] == 5
    assert result["network_exit_throughput_vehicles_per_hour"] == 360
    assert read_tripinfo(path).completed_vehicles == 4
    empty = read_window_trip_metrics(path, 100, 200)
    assert empty["cohort_mean_travel_time_seconds"] is None


def test_ramp_queue_edges_exclude_mainline_and_exits(tmp_path):
    path = tmp_path / "routes.xml"
    path.write_text("""<routes>
      <route id="us101_northbound" edges="m1 m2"/>
      <route id="entrance" edges="r1 r2 m2"/>
      <route id="exit" edges="m1 x"/>
    </routes>""")
    assert entrance_queue_edges(path) == {"r1", "r2"}


def _config():
    return {
        "experiment_id": "acceptance",
        "scenarios": [{"id": "H0", "baseline_config": "base"}],
        "observation_dates": ["2025-10-08"],
        "seeds": [43, 41],
        "measurement": {"period_seconds": 1, "stop_speed_m_per_s": 0.1},
        "output_directory": "outputs/m4",
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("workers", 0),
        ("workers", True),
        ("workers", 9),
        ("seeds", [41]),
        ("seeds", [41, 41]),
        ("seeds", [True, 42]),
        ("observation_dates", ["2025-10-08", "2025-10-08"]),
        ("observation_dates", ["2025-02-30"]),
        ("experiment_id", "../escape"),
        ("output_directory", "docs"),
        ("measurement", {"period_seconds": 0.7, "stop_speed_m_per_s": 0.1}),
        ("measurement", {"period_seconds": 1, "stop_speed_m_per_s": float("nan")}),
    ],
)
def test_invalid_experiments_fail_before_scenario_loading(tmp_path, field, value):
    config = {**_config(), field: value}
    with pytest.raises(ValueError):
        harness.validate_experiment(config, tmp_path)


def test_comparison_guard_and_seed_summary_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(
        harness, "_load_baseline_config", lambda path, root: {"truck_share": str(path)}
    )
    config = _config()
    config["scenarios"].append({"id": "H1", "baseline_config": "different"})
    with pytest.raises(ValueError, match="Scenarios differ"):
        harness.validate_experiment(config, tmp_path)
    metric = "cohort_mean_travel_time_seconds"
    runs = [{"accepted": True, "metrics": {metric: value}} for value in [10, 20]]
    summary = harness.summarize_seed_metrics(runs)[metric]
    assert summary["mean"] == 15
    assert summary["sample_standard_deviation"] == pytest.approx(50**0.5)
    runs[1]["metrics"][metric] = None
    assert harness.summarize_seed_metrics(runs)[metric]["mean"] is None
    assert not clean_and_cleared({"final_summary": {}, "warning_lines": []})


@pytest.mark.parametrize(
    "controlled",
    [
        False,
        True,
        "central",
        "central_no_commands",
        "central_no_exposure",
        "central_not_restored",
        "central_wrong_engine",
    ],
)
def test_orchestrator_isolates_runs_and_retains_failure_reports(tmp_path, monkeypatch, controlled):
    monkeypatch.setattr(harness, "repository_root", lambda: tmp_path)
    monkeypatch.setattr(
        harness,
        "_load_baseline_config",
        lambda path, root: {
            "warmup_seconds": 0,
            "human_parameters": {"tau": 1.5, "accel": 2.6, "decel": 4.5},
        },
    )
    calls = []

    def run(path, seed, **kwargs):
        calls.append(path)
        assert path.parent.name == f"seed_{seed}"
        if controlled:
            assert kwargs["controller"] == harness_policy
            diagnostics = {
                "completed": seed != 43,
                "commands": 1,
                "cooperative_commands": 1,
                "native_fallbacks": 0,
                "engine_version": "SUMO 1.27.1",
            }
            if isinstance(controlled, str):
                diagnostics.update(restored=True, updates=1, limited_lane_seconds=1)
                if controlled == "central_no_commands":
                    diagnostics["commands"] = 0
                elif controlled == "central_no_exposure":
                    diagnostics["limited_lane_seconds"] = 0
                elif controlled == "central_not_restored":
                    diagnostics["restored"] = False
                elif controlled == "central_wrong_engine":
                    diagnostics["engine_version"] = "SUMO 0.0"
            (path.parent / "controller_diagnostics.json").write_text(json.dumps(diagnostics))
        if seed == 43:
            raise RuntimeError("intentional acceptance failure")
        scenario = json.loads(path.read_text())
        directory = path.parent
        (directory / "h0_run_health_seed_41.json").write_text(
            json.dumps(
                {
                    "final_summary": {
                        key: 0
                        for key in [
                            "running",
                            "waiting",
                            "collisions",
                            "teleports",
                            "discarded",
                            "loaded",
                            "inserted",
                            "ended",
                        ]
                    },
                    "warning_lines": [],
                }
            )
        )
        Path(scenario["route_file"]).write_text(
            '<routes><route id="us101_northbound" edges="m"/></routes>'
        )
        (directory / "h0_human_baseline_seed_41.tripinfo.xml").write_text("<tripinfos/>")
        (directory / "h0_summary_seed_41.xml").write_text(
            '<summary><step time="0" waiting="0"/></summary>'
        )
        _trajectory(kwargs["trajectory_output"], '<timestep time="0"/>')
        return (
            SimpleNamespace(
                demand_profile=[SimpleNamespace(end_seconds=1)],
                route_file=scenario["route_file"],
                network_sha256="network",
                provenance={"sumo_version": "Eclipse SUMO sumo 1.27.1"},
                manifest_file=scenario["manifest_file"],
            ),
            RunMetrics(0, None, None, None),
            directory / "detectors.json",
        )

    monkeypatch.setattr(harness, "run_human_baseline", run)
    config_file = tmp_path / "experiment.json"
    from bay_area_traffic_sim.cooperative import DEFAULT_CONTROLLER

    if isinstance(controlled, str):
        from bay_area_traffic_sim.centralized import DEFAULT_CONTROLLER as CENTRAL

        harness_policy = dict(CENTRAL)
    else:
        harness_policy = dict(DEFAULT_CONTROLLER)
    config = _config()
    if controlled:
        config["scenarios"][0]["controller"] = harness_policy
    config_file.write_text(json.dumps(config))
    report = harness.run_experiment(config_file)
    assert [run["seed"] for run in report["runs"]] == [41, 43]
    assert len(calls) == 2 and len(set(calls)) == 2
    assert report["runs"][0]["accepted"] == (controlled in [False, True, "central"])
    assert "intentional acceptance failure" in report["runs"][1]["error"]
    assert not report["accepted"]
    if controlled:
        assert report["runs"][0]["controller"] == harness_policy
        resolved = json.loads(calls[0].read_text())
        assert resolved["controller"] == harness_policy
        assert not report["runs"][1]["controller_diagnostics"]["completed"]
    assert report["groups"][0]["metric_summary"]["mean_stopped_vehicles"]["mean"] is None
    assert (tmp_path / report["report_file"]).is_file()
    assert (tmp_path / report["report_file"]).with_name("summary.md").is_file()
    with pytest.raises(ValueError, match="existing runs"):
        harness.run_experiment(config_file)


def test_cli_failure_returns_nonzero(monkeypatch):
    from bay_area_traffic_sim import __main__ as cli

    monkeypatch.setattr("sys.argv", ["sim", "run-us101-experiment"])
    monkeypatch.setattr(cli, "run_experiment", lambda path: {"accepted": False})
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 1
