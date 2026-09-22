import json
from pathlib import Path
from xml.etree import ElementTree

from bay_area_traffic_sim.real_corridor import demand_points_from_report, write_route_file


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
        "warmup",
        "observed_0700",
        "observed_0705",
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
