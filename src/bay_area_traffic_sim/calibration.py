"""Compare PeMS station profiles with matching SUMO virtual detectors."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import fmean


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
    if not observed_profiles:
        raise ValueError("Observed station profile report contains no profiles.")
    if not simulated_intervals:
        raise ValueError("Simulated virtual-detector report contains no intervals.")

    first_time = min(
        point["time"]
        for profile in observed_profiles
        for point in profile["time_profile"]
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
        pairs = [
            (point, simulated_by_station_time[(station_id, point["time"])])
            for point in profile["time_profile"]
            if (station_id, point["time"]) in simulated_by_station_time
        ]
        if not pairs:
            missing_simulated_station_ids.append(station_id)
            continue

        observed_flows = [
            float(observed["mean_flow_vehicles_per_5_minutes"]) * 12
            for observed, _ in pairs
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
                    for observed, simulated in zip(
                        observed_flows, simulated_flows, strict=True
                    )
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
        "limitation": (
            "Calibration targets are provisional until detector locations, ramp context, "
            "and held-out validation days are finalized."
        ),
    }
