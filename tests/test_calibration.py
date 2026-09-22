import json
from pathlib import Path

import pytest

from bay_area_traffic_sim.calibration import (
    compare_detector_profiles,
    summarize_detector_comparisons,
)


def test_compare_detector_profiles_matches_station_and_five_minute_time(tmp_path: Path) -> None:
    observed = tmp_path / "observed.json"
    simulated = tmp_path / "simulated.json"
    observed.write_text(
        json.dumps(
            {
                "summary": {
                    "profiles": [
                        {
                            "station_id": 400001,
                            "time_profile": [
                                {
                                    "time": "07:00",
                                    "mean_flow_vehicles_per_5_minutes": 40,
                                    "mean_speed_mph": 50,
                                },
                                {
                                    "time": "07:05",
                                    "mean_flow_vehicles_per_5_minutes": 50,
                                    "mean_speed_mph": 40,
                                },
                            ],
                        }
                    ]
                }
            }
        )
    )
    simulated.write_text(
        json.dumps(
            {
                "intervals": [
                    {
                        "station_id": 400001,
                        "begin_seconds": 900,
                        "flow_vehicles_per_hour": 480,
                        "speed_mph": 55,
                    },
                    {
                        "station_id": 400001,
                        "begin_seconds": 1200,
                        "flow_vehicles_per_hour": 540,
                        "speed_mph": 50,
                    },
                ]
            }
        )
    )

    report = compare_detector_profiles(observed, simulated)
    comparison = report["station_comparisons"][0]

    assert comparison["matched_intervals"] == 2
    assert comparison["observed_mean_flow_vehicles_per_hour"] == 540
    assert comparison["simulated_mean_flow_vehicles_per_hour"] == 510
    assert comparison["flow_mean_absolute_percentage_error"] == pytest.approx(5.0)
    assert comparison["observed_mean_speed_mph"] == 45
    assert comparison["simulated_mean_speed_mph"] == 52.5
    assert comparison["speed_mean_absolute_error_mph"] == 7.5


def test_summarize_detector_comparisons_reports_seed_spread() -> None:
    reports = [
        {
            "station_comparisons": [
                {
                    "station_id": 400001,
                    "matched_intervals": 24,
                    "observed_mean_flow_vehicles_per_hour": 500.0,
                    "simulated_mean_flow_vehicles_per_hour": simulated_flow,
                    "flow_mean_absolute_percentage_error": flow_error,
                    "observed_mean_speed_mph": 50.0,
                    "simulated_mean_speed_mph": simulated_speed,
                    "speed_mean_absolute_error_mph": speed_error,
                }
            ]
        }
        for simulated_flow, flow_error, simulated_speed, speed_error in (
            (480.0, 4.0, 52.0, 2.0),
            (520.0, 4.0, 48.0, 2.0),
        )
    ]

    summary = summarize_detector_comparisons(reports)[0]

    assert summary["runs"] == 2
    assert summary["simulated_mean_flow_vehicles_per_hour"]["mean"] == 500
    assert summary["simulated_mean_flow_vehicles_per_hour"][
        "sample_standard_deviation"
    ] == pytest.approx(28.2842712475)
    assert summary["simulated_mean_speed_mph"]["mean"] == 50
