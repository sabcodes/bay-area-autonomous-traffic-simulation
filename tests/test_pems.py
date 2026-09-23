import gzip
from pathlib import Path

from bay_area_traffic_sim.pems import (
    PemsFilter,
    summarize_station_files,
    summarize_station_profiles,
)


def _row(
    timestamp: str,
    station_id: int,
    *,
    freeway: int = 101,
    direction: str = "N",
    lane_type: str = "ML",
    observed_percent: float = 100,
    flow: float = 100,
    speed: float = 60,
) -> str:
    return ",".join(
        [
            timestamp,
            str(station_id),
            "4",
            str(freeway),
            direction,
            lane_type,
            ".25",
            "10",
            str(observed_percent),
            str(flow),
            ".01",
            str(speed),
        ]
    )


def test_summary_filters_records_and_builds_a_time_profile(tmp_path: Path) -> None:
    source = tmp_path / "d04_text_station_5min_2025_10_07.txt.gz"
    rows = [
        _row("10/07/2025 07:00:00", 400001, flow=100, speed=60),
        _row("10/07/2025 07:05:00", 400001, observed_percent=80, flow=200, speed=50),
        _row("10/07/2025 07:10:00", 400002, flow=50, speed=40),
        _row("10/07/2025 07:15:00", 400003, freeway=280, flow=300, speed=55),
        "not,a,valid,pems,row",
    ]
    with gzip.open(source, "wt", newline="") as destination:
        destination.write("\n".join(rows))

    summary = summarize_station_files(
        [source],
        PemsFilter(start_hour=7, end_hour=8, minimum_observed_percent=90),
    )

    assert summary.files_read == 1
    assert summary.rows_read == 5
    assert summary.invalid_rows == 1
    assert summary.unusable_aggregate_rows == 0
    assert summary.matching_rows == 2
    assert summary.rows_with_speed == 2
    assert summary.station_count == 2
    assert summary.date_count == 1
    assert summary.mean_flow_vehicles_per_5_minutes_per_station == 75
    assert summary.mean_speed_mph == 50
    assert summary.time_profile == [
        {
            "time": "07:00",
            "observations": 1,
            "mean_flow_vehicles_per_5_minutes_per_station": 100.0,
            "mean_speed_mph": 60.0,
        },
        {
            "time": "07:10",
            "observations": 1,
            "mean_flow_vehicles_per_5_minutes_per_station": 50.0,
            "mean_speed_mph": 40.0,
        },
    ]


def test_summary_requires_at_least_one_source_file() -> None:
    try:
        summarize_station_files([], PemsFilter())
    except ValueError as error:
        assert "No PeMS source files" in str(error)
    else:
        raise AssertionError("Expected a helpful error for an empty file list.")


def test_summary_can_retain_only_selected_station_ids(tmp_path: Path) -> None:
    source = tmp_path / "d04_text_station_5min_2025_10_08.txt.gz"
    rows = [
        _row("10/08/2025 07:00:00", 400001, flow=100),
        _row("10/08/2025 07:00:00", 400002, flow=200),
    ]
    with gzip.open(source, "wt", newline="") as destination:
        destination.write("\n".join(rows))

    summary = summarize_station_files(
        [source], PemsFilter(start_hour=7, end_hour=8, station_ids={400001})
    )

    assert summary.station_count == 1
    assert summary.matching_rows == 1
    assert summary.mean_flow_vehicles_per_5_minutes_per_station == 100


def test_summary_keeps_a_flow_when_pems_omits_its_speed(tmp_path: Path) -> None:
    source = tmp_path / "d04_text_station_5min_2025_10_08.txt.gz"
    source_row = _row("10/08/2025 07:00:00", 400001, flow=125, speed=60)
    with gzip.open(source, "wt", newline="") as destination:
        destination.write(source_row.rsplit(",", maxsplit=1)[0] + ",")

    summary = summarize_station_files([source], PemsFilter(start_hour=7, end_hour=8))

    assert summary.matching_rows == 1
    assert summary.rows_with_speed == 0
    assert summary.mean_flow_vehicles_per_5_minutes_per_station == 125
    assert summary.mean_speed_mph is None


def test_summary_counts_rows_without_a_usable_aggregate_measurement(tmp_path: Path) -> None:
    source = tmp_path / "d04_text_station_5min_2025_10_09.txt.gz"
    source_row = _row("10/09/2025 07:00:00", 400001)
    fields = source_row.split(",")
    fields[8] = ""
    fields[9] = ""
    with gzip.open(source, "wt", newline="") as destination:
        destination.write(",".join(fields))

    summary = summarize_station_files([source], PemsFilter(start_hour=7, end_hour=8))

    assert summary.invalid_rows == 0
    assert summary.unusable_aggregate_rows == 1
    assert summary.matching_rows == 0


def test_station_profiles_keep_on_and_off_ramps_separate(tmp_path: Path) -> None:
    source = tmp_path / "d04_text_station_5min_2025_10_09.txt.gz"
    rows = [
        _row("10/09/2025 07:00:00", 400001, lane_type="OR", flow=20, speed=35),
        _row("10/10/2025 07:00:00", 400001, lane_type="OR", flow=30, speed=45),
        _row("10/09/2025 07:00:00", 400002, lane_type="FR", flow=10, speed=30),
        _row("10/09/2025 07:00:00", 400003, lane_type="ML", flow=100, speed=60),
    ]
    with gzip.open(source, "wt", newline="") as destination:
        destination.write("\n".join(rows))

    summary = summarize_station_profiles(
        [source],
        PemsFilter(
            start_hour=7,
            end_hour=8,
            station_ids={400001, 400002},
            lane_types={"OR", "FR"},
        ),
    )

    assert summary.station_count == 2
    assert summary.matching_rows == 3
    assert summary.profiles[0].station_id == 400001
    assert summary.profiles[0].lane_type == "OR"
    assert summary.profiles[0].date_count == 2
    assert summary.profiles[0].mean_flow_vehicles_per_5_minutes == 25
    assert summary.profiles[0].time_profile[0]["mean_speed_mph"] == 40
    assert summary.profiles[0].daily_time_profile == [
        {
            "date": "2025-10-09",
            "time_profile": [
                {
                    "time": "07:00",
                    "observations": 1,
                    "mean_flow_vehicles_per_5_minutes": 20.0,
                    "mean_speed_mph": 35.0,
                }
            ],
        },
        {
            "date": "2025-10-10",
            "time_profile": [
                {
                    "time": "07:00",
                    "observations": 1,
                    "mean_flow_vehicles_per_5_minutes": 30.0,
                    "mean_speed_mph": 45.0,
                }
            ],
        },
    ]
    assert summary.profiles[1].station_id == 400002


def test_station_profiles_require_station_ids(tmp_path: Path) -> None:
    source = tmp_path / "empty.txt.gz"
    with gzip.open(source, "wt", newline=""):
        pass

    try:
        summarize_station_profiles([source], PemsFilter(station_ids=None))
    except ValueError as error:
        assert "explicit station ID" in str(error)
    else:
        raise AssertionError("Expected a helpful error when station IDs are omitted.")
