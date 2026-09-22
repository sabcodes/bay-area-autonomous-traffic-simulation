from bay_area_traffic_sim.experiments import summarize_runs
from bay_area_traffic_sim.metrics import RunMetrics


def test_summarize_runs_reports_mean_and_sample_spread() -> None:
    summary = summarize_runs(
        [
            RunMetrics(10, 20.0, 3.0, 4.0),
            RunMetrics(14, 40.0, 5.0, 8.0),
        ]
    )

    assert summary["completed_vehicles"] == {
        "mean": 12.0,
        "sample_standard_deviation": 2.8284271247461903,
    }
    assert summary["average_travel_time_seconds"] == {
        "mean": 30.0,
        "sample_standard_deviation": 14.142135623730951,
    }


def test_summarize_runs_rejects_an_empty_experiment() -> None:
    try:
        summarize_runs([])
    except ValueError as error:
        assert str(error) == "At least one simulation run is required."
    else:
        raise AssertionError("An empty experiment must be rejected.")
