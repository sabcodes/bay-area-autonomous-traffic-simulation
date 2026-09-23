"""Compare PeMS station profiles with matching SUMO virtual detectors."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import fmean, stdev


@dataclass(frozen=True)
class StationCalibrationComparison:
    station_id: int
    matched_intervals: int
    observed_mean_flow_vehicles_per_hour: float
    simulated_mean_flow_vehicles_per_hour: float
    flow_mean_absolute_percentage_error: float
    observed_mean_speed_mph: float | None
    simulated_mean_speed_mph: float | None
    speed_mean_absolute_error_mph: float | None


def _mean_and_spread(values: list[float | None]) -> dict[str, float | None]:
    if not values or any(value is None for value in values):
        return {"mean": None, "sample_standard_deviation": None}
    numeric_values = [float(value) for value in values if value is not None]
    return {
        "mean": fmean(numeric_values),
        "sample_standard_deviation": (stdev(numeric_values) if len(numeric_values) > 1 else 0.0),
    }


def summarize_detector_comparisons(
    reports: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Summarize station calibration error and its seed-to-seed spread."""

    if not reports:
        raise ValueError("At least one detector comparison report is required.")
    by_station: dict[int, list[dict[str, object]]] = {}
    for report in reports:
        for comparison in report["station_comparisons"]:
            station_id = int(comparison["station_id"])
            by_station.setdefault(station_id, []).append(comparison)

    expected_runs = len(reports)
    result: list[dict[str, object]] = []
    for station_id, comparisons in sorted(by_station.items()):
        if len(comparisons) != expected_runs:
            raise ValueError(f"Station {station_id} is missing from one or more seed reports.")
        first = comparisons[0]
        result.append(
            {
                "station_id": station_id,
                "runs": expected_runs,
                "matched_intervals_per_run": first["matched_intervals"],
                "observed_mean_flow_vehicles_per_hour": first[
                    "observed_mean_flow_vehicles_per_hour"
                ],
                "simulated_mean_flow_vehicles_per_hour": _mean_and_spread(
                    [
                        comparison["simulated_mean_flow_vehicles_per_hour"]
                        for comparison in comparisons
                    ]
                ),
                "flow_mean_absolute_percentage_error": _mean_and_spread(
                    [
                        comparison["flow_mean_absolute_percentage_error"]
                        for comparison in comparisons
                    ]
                ),
                "observed_mean_speed_mph": first["observed_mean_speed_mph"],
                "simulated_mean_speed_mph": _mean_and_spread(
                    [comparison["simulated_mean_speed_mph"] for comparison in comparisons]
                ),
                "speed_mean_absolute_error_mph": _mean_and_spread(
                    [comparison["speed_mean_absolute_error_mph"] for comparison in comparisons]
                ),
            }
        )
    return result


def compare_detector_profiles(
    observed_profile_file: Path,
    simulated_detector_file: Path,
    warmup_seconds: int = 900,
) -> dict[str, object]:
    """Compare matching station/time intervals without collapsing spatial differences."""

    observed_report = json.loads(observed_profile_file.read_text())
    simulated_report = json.loads(simulated_detector_file.read_text())
    observed_profiles = observed_report.get("summary", {}).get("profiles", [])
    simulated_intervals = simulated_report.get("intervals", [])
    lane_mismatch_station_ids = {
        int(detector["station_id"])
        for detector in simulated_report.get("detectors", [])
        if detector.get("reported_lane_count") is not None
        and int(detector["reported_lane_count"]) != len(detector.get("lane_ids", []))
    }
    if not observed_profiles:
        raise ValueError("Observed station profile report contains no profiles.")
    if not simulated_intervals:
        raise ValueError("Simulated virtual-detector report contains no intervals.")

    first_time = min(
        point["time"] for profile in observed_profiles for point in profile["time_profile"]
    )
    clock_start = datetime.strptime(first_time, "%H:%M")
    simulated_by_station_time = {
        (
            interval["station_id"],
            (clock_start + timedelta(seconds=interval["begin_seconds"] - warmup_seconds)).strftime(
                "%H:%M"
            ),
        ): interval
        for interval in simulated_intervals
        if interval["begin_seconds"] >= warmup_seconds
    }

    comparisons: list[StationCalibrationComparison] = []
    missing_simulated_station_ids: list[int] = []
    for profile in observed_profiles:
        station_id = profile["station_id"]
        if station_id in lane_mismatch_station_ids:
            continue
        pairs = [
            (point, simulated_by_station_time[(station_id, point["time"])])
            for point in profile["time_profile"]
            if (station_id, point["time"]) in simulated_by_station_time
        ]
        if not pairs:
            missing_simulated_station_ids.append(station_id)
            continue

        observed_flows = [
            float(observed["mean_flow_vehicles_per_5_minutes"]) * 12 for observed, _ in pairs
        ]
        simulated_flows = [float(simulated["flow_vehicles_per_hour"]) for _, simulated in pairs]
        observed_speeds = [
            float(observed["mean_speed_mph"])
            for observed, _ in pairs
            if observed["mean_speed_mph"] is not None
        ]
        speed_pairs = [
            (float(observed["mean_speed_mph"]), float(simulated["speed_mph"]))
            for observed, simulated in pairs
            if observed["mean_speed_mph"] is not None and simulated["speed_mph"] is not None
        ]
        comparisons.append(
            StationCalibrationComparison(
                station_id=station_id,
                matched_intervals=len(pairs),
                observed_mean_flow_vehicles_per_hour=fmean(observed_flows),
                simulated_mean_flow_vehicles_per_hour=fmean(simulated_flows),
                flow_mean_absolute_percentage_error=fmean(
                    abs(simulated - observed) / observed * 100
                    for observed, simulated in zip(observed_flows, simulated_flows, strict=True)
                    if observed > 0
                ),
                observed_mean_speed_mph=(fmean(observed_speeds) if observed_speeds else None),
                simulated_mean_speed_mph=(
                    fmean(simulated for _, simulated in speed_pairs) if speed_pairs else None
                ),
                speed_mean_absolute_error_mph=(
                    fmean(abs(simulated - observed) for observed, simulated in speed_pairs)
                    if speed_pairs
                    else None
                ),
            )
        )

    return {
        "observed_profile_file": str(observed_profile_file),
        "simulated_detector_file": str(simulated_detector_file),
        "warmup_seconds": warmup_seconds,
        "station_comparisons": [asdict(comparison) for comparison in comparisons],
        "missing_simulated_station_ids": missing_simulated_station_ids,
        "excluded_lane_mismatch_station_ids": sorted(lane_mismatch_station_ids),
        "limitation": (
            "Calibration targets are provisional until detector locations, ramp context, "
            "and held-out validation days are finalized."
        ),
    }
