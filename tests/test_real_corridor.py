import json
from pathlib import Path
from xml.etree import ElementTree

from bay_area_traffic_sim.real_corridor import (
    RampDemand,
    _load_baseline_config,
    _subtract_demand_profiles,
    common_observation_dates,
    demand_points_from_report,
    write_route_file,
)


def _report() -> dict[str, object]:
    return {
        "summary": {
            "time_profile": [
                {
                    "time": "07:00",
                    "mean_flow_vehicles_per_5_minutes_per_station": 400.0,
                    "mean_speed_mph": 55.0,
                },
                {
                    "time": "07:05",
                    "mean_flow_vehicles_per_5_minutes_per_station": 450.0,
                    "mean_speed_mph": 45.0,
                },
            ]
        }
    }


def test_demand_points_convert_five_minute_flow_to_hourly_rate() -> None:
    points = demand_points_from_report(_report(), warmup_seconds=900)

    assert points[0].observed_time == "07:00"
    assert points[0].begin_seconds == 900
    assert points[0].end_seconds == 1200
    assert points[0].vehicles_per_hour == 4800
    assert points[1].begin_seconds == 1200
    assert points[1].vehicles_per_hour == 5400


def test_write_route_file_includes_warmup_and_observed_flows(tmp_path: Path) -> None:
    points = demand_points_from_report(_report(), warmup_seconds=900)
    destination = tmp_path / "human.rou.xml"

    write_route_file(destination, ["start", "middle", "end"], points, 900)

    root = ElementTree.parse(destination).getroot()
    assert root.find("route").attrib["edges"] == "start middle end"
    flows = root.findall("flow")
    assert [flow.attrib["id"] for flow in flows] == [
        "mainline_warmup",
        "mainline_0700",
        "mainline_0705",
    ]
    assert flows[0].attrib["vehsPerHour"] == "4800.00"
    assert flows[-1].attrib["begin"] == "1200"


def test_demand_points_require_a_profile() -> None:
    try:
        demand_points_from_report(json.loads('{"summary": {}}'), warmup_seconds=900)
    except ValueError as error:
        assert "time profile" in str(error)
    else:
        raise AssertionError("Expected a helpful error for a missing time profile.")


def test_demand_points_select_one_station_profile() -> None:
    report = {
        "summary": {
            "profiles": [
                {
                    "station_id": 123,
                    "time_profile": [
                        {
                            "time": "07:00",
                            "mean_flow_vehicles_per_5_minutes": 10.0,
                            "mean_speed_mph": None,
                        }
                    ],
                }
            ]
        }
    }

    points = demand_points_from_report(report, warmup_seconds=900, station_id=123)

    assert points[0].vehicles_per_hour == 120
    assert points[0].observed_speed_mph is None


def test_demand_points_can_use_only_selected_observation_dates() -> None:
    report = {
        "summary": {
            "profiles": [
                {
                    "station_id": 123,
                    "time_profile": [
                        {"time": "07:00", "mean_flow_vehicles_per_5_minutes": 100}
                    ],
                    "daily_time_profile": [
                        {
                            "date": "2025-10-07",
                            "time_profile": [
                                {"time": "07:00", "observations": 1,
                                 "mean_flow_vehicles_per_5_minutes": 80,
                                 "mean_speed_mph": 50}
                            ],
                        },
                        {
                            "date": "2025-10-08",
                            "time_profile": [
                                {"time": "07:00", "observations": 1,
                                 "mean_flow_vehicles_per_5_minutes": 120,
                                 "mean_speed_mph": 60}
                            ],
                        },
                    ],
                }
            ]
        }
    }

    points = demand_points_from_report(
        report, warmup_seconds=0, station_id=123, observation_dates={"2025-10-08"}
    )

    assert points[0].vehicles_per_hour == 1440
    assert points[0].observed_speed_mph == 60


def test_common_observation_dates_require_complete_matching_time_slots() -> None:
    def profile(station_id: int, second_day_times: list[str]) -> dict[str, object]:
        return {
            "station_id": station_id,
            "time_profile": [{"time": "07:00"}, {"time": "07:05"}],
            "daily_time_profile": [
                {
                    "date": "2025-10-07",
                    "time_profile": [
                        {"time": "07:00"}, {"time": "07:05"}
                    ],
                },
                {
                    "date": "2025-10-08",
                    "time_profile": [{"time": time} for time in second_day_times],
                },
            ],
        }

    report = {"summary": {"profiles": [profile(1, ["07:00", "07:05"]),
                                          profile(2, ["07:00"])]}}

    assert common_observation_dates([report], [1, 2]) == {"2025-10-07"}


def test_scenario_config_can_inherit_and_override_a_parent(tmp_path: Path) -> None:
    configs = tmp_path / "configs"
    configs.mkdir()
    (configs / "base.json").write_text(
        json.dumps({"scenario": "base", "ramp_mappings": [1], "route_file": "base.rou.xml"})
    )
    (configs / "candidate.json").write_text(
        json.dumps(
            {
                "extends": "configs/base.json",
                "scenario": "candidate",
                "route_file": "candidate.rou.xml",
            }
        )
    )

    config = _load_baseline_config(Path("configs/candidate.json"), tmp_path)

    assert config == {
        "scenario": "candidate",
        "ramp_mappings": [1],
        "route_file": "candidate.rou.xml",
    }


def test_subtract_demand_profiles_preserves_time_and_removes_flow() -> None:
    mainline = demand_points_from_report(_report(), warmup_seconds=900)
    off_ramp_report = _report()
    off_ramp_report["summary"]["time_profile"][0][
        "mean_flow_vehicles_per_5_minutes_per_station"
    ] = 25.0
    off_ramp_report["summary"]["time_profile"][1][
        "mean_flow_vehicles_per_5_minutes_per_station"
    ] = 50.0
    off_ramp = demand_points_from_report(off_ramp_report, warmup_seconds=900)

    result = _subtract_demand_profiles(mainline, [off_ramp])

    assert [point.vehicles_per_hour for point in result] == [4500, 4800]
    assert [point.observed_time for point in result] == ["07:00", "07:05"]


def test_write_route_file_includes_audited_ramp_demand(tmp_path: Path) -> None:
    points = demand_points_from_report(_report(), warmup_seconds=900)
    ramp = RampDemand(
        station_id=123,
        lane_type="OR",
        name="Test on-ramp",
        route_id="ramp_123_or",
        route_edge_ids=["ramp", "merge", "end"],
        demand_profile=points,
    )
    destination = tmp_path / "human.rou.xml"

    write_route_file(destination, ["start", "merge", "end"], points, 900, [ramp])

    root = ElementTree.parse(destination).getroot()
    routes = {route.attrib["id"]: route.attrib["edges"] for route in root.findall("route")}
    assert routes["ramp_123_or"] == "ramp merge end"
    assert root.find("flow[@id='ramp_123_warmup']").attrib["route"] == "ramp_123_or"
    assert [int(flow.attrib["begin"]) for flow in root.findall("flow")] == [
        0,
        0,
        900,
        900,
        1200,
        1200,
    ]
