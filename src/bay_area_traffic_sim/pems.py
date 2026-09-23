"""Read PeMS station five-minute files and create transparent calibration summaries."""

from __future__ import annotations

import csv
import gzip
from collections import defaultdict
from collections.abc import Iterable, Set
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import fmean


@dataclass(frozen=True)
class StationObservation:
    """One five-minute detector observation from a PeMS station export."""

    timestamp: datetime
    station_id: int
    district: int
    freeway: int
    direction: str
    lane_type: str
    observed_percent: float | None
    total_flow: float | None
    average_speed_mph: float | None

    @property
    def has_aggregate_measurement(self) -> bool:
        """Whether PeMS supplied the coverage and flow needed for calibration."""

        return self.observed_percent is not None and self.total_flow is not None


@dataclass(frozen=True)
class PemsFilter:
    """The explicit subset of observations used as a calibration target."""

    district: int = 4
    freeway: int = 101
    direction: str = "N"
    lane_type: str = "ML"
    start_hour: int = 7
    end_hour: int = 9
    minimum_observed_percent: float = 90.0
    station_ids: Set[int] | None = None
    lane_types: Set[str] | None = None

    def matches(self, observation: StationObservation) -> bool:
        return (
            observation.district == self.district
            and observation.freeway == self.freeway
            and observation.direction == self.direction
            and (
                observation.lane_type in self.lane_types
                if self.lane_types is not None
                else observation.lane_type == self.lane_type
            )
            and (self.station_ids is None or observation.station_id in self.station_ids)
            and self.start_hour <= observation.timestamp.hour < self.end_hour
            and observation.has_aggregate_measurement
            and observation.observed_percent is not None
            and observation.observed_percent >= self.minimum_observed_percent
        )


@dataclass(frozen=True)
class CalibrationSummary:
    """Aggregate facts derived from a declared PeMS filter and source files."""

    source_files: list[str]
    files_read: int
    rows_read: int
    invalid_rows: int
    unusable_aggregate_rows: int
    matching_rows: int
    rows_with_speed: int
    date_count: int
    station_count: int
    mean_flow_vehicles_per_5_minutes_per_station: float | None
    mean_speed_mph: float | None
    time_profile: list[dict[str, float | int | str | None]]

    def as_dict(self) -> dict[str, object]:
        """Return JSON-ready data without exposing a mutable internal object."""

        return asdict(self)


@dataclass(frozen=True)
class StationTimeProfile:
    """Observed five-minute traffic rhythm for one individual PeMS station."""

    station_id: int
    lane_type: str
    matching_rows: int
    date_count: int
    mean_flow_vehicles_per_5_minutes: float
    mean_speed_mph: float | None
    time_profile: list[dict[str, float | int | str | None]]
    daily_time_profile: list[dict[str, object]]


@dataclass(frozen=True)
class StationProfilesSummary:
    """Station-level profiles used for ramp demand and virtual-detector validation."""

    source_files: list[str]
    files_read: int
    rows_read: int
    invalid_rows: int
    matching_rows: int
    station_count: int
    profiles: list[StationTimeProfile]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def parse_station_row(row: list[str]) -> StationObservation:
    """Parse the shared leading fields of a PeMS Station 5-Minute CSV row."""

    if len(row) < 12:
        raise ValueError("A Station 5-Minute row needs at least 12 columns.")

    try:
        return StationObservation(
            timestamp=datetime.strptime(row[0], "%m/%d/%Y %H:%M:%S"),
            station_id=int(row[1]),
            district=int(row[2]),
            freeway=int(row[3]),
            direction=row[4],
            lane_type=row[5],
            observed_percent=_float_or_none(row[8]),
            total_flow=_float_or_none(row[9]),
            average_speed_mph=float(row[11]) if row[11] else None,
        )
    except (TypeError, ValueError) as error:
        raise ValueError("Could not parse Station 5-Minute row.") from error


def _float_or_none(value: str) -> float | None:
    return float(value) if value else None


def summarize_station_files(
    source_files: Iterable[Path], criteria: PemsFilter
) -> CalibrationSummary:
    """Stream PeMS files, filter their observations, and calculate a time-of-day profile."""

    files = list(source_files)
    if not files:
        raise ValueError("No PeMS source files matched the requested input pattern.")

    rows_read = 0
    invalid_rows = 0
    unusable_aggregate_rows = 0
    matching_rows = 0
    rows_with_speed = 0
    dates: set[str] = set()
    stations: set[int] = set()
    flows: list[float] = []
    speeds: list[float] = []
    profile_flows: defaultdict[str, list[float]] = defaultdict(list)
    profile_speeds: defaultdict[str, list[float]] = defaultdict(list)

    for source in files:
        with gzip.open(source, "rt", newline="") as raw_file:
            for row in csv.reader(raw_file):
                rows_read += 1
                try:
                    observation = parse_station_row(row)
                except ValueError:
                    invalid_rows += 1
                    continue

                if not observation.has_aggregate_measurement:
                    unusable_aggregate_rows += 1
                    continue

                if not criteria.matches(observation):
                    continue

                matching_rows += 1
                dates.add(observation.timestamp.date().isoformat())
                stations.add(observation.station_id)
                if observation.total_flow is None:
                    raise AssertionError("Aggregate measurements must include total flow.")
                flows.append(observation.total_flow)
                time_key = observation.timestamp.strftime("%H:%M")
                profile_flows[time_key].append(observation.total_flow)
                if observation.average_speed_mph is not None:
                    rows_with_speed += 1
                    speeds.append(observation.average_speed_mph)
                    profile_speeds[time_key].append(observation.average_speed_mph)

    time_profile = [
        {
            "time": time_key,
            "observations": len(profile_flows[time_key]),
            "mean_flow_vehicles_per_5_minutes_per_station": fmean(profile_flows[time_key]),
            "mean_speed_mph": (
                fmean(profile_speeds[time_key]) if profile_speeds[time_key] else None
            ),
        }
        for time_key in sorted(profile_flows)
    ]
    return CalibrationSummary(
        source_files=[str(source) for source in files],
        files_read=len(files),
        rows_read=rows_read,
        invalid_rows=invalid_rows,
        unusable_aggregate_rows=unusable_aggregate_rows,
        matching_rows=matching_rows,
        rows_with_speed=rows_with_speed,
        date_count=len(dates),
        station_count=len(stations),
        mean_flow_vehicles_per_5_minutes_per_station=fmean(flows) if flows else None,
        mean_speed_mph=fmean(speeds) if speeds else None,
        time_profile=time_profile,
    )


def summarize_station_profiles(
    source_files: Iterable[Path], criteria: PemsFilter
) -> StationProfilesSummary:
    """Stream PeMS files once and retain a separate five-minute profile per station."""

    files = list(source_files)
    if not files:
        raise ValueError("No PeMS source files matched the requested input pattern.")
    if not criteria.station_ids:
        raise ValueError("Station-level profiles require an explicit station ID set.")

    rows_read = 0
    invalid_rows = 0
    matching_rows = 0
    flows: defaultdict[int, list[float]] = defaultdict(list)
    speeds: defaultdict[int, list[float]] = defaultdict(list)
    dates: defaultdict[int, set[str]] = defaultdict(set)
    lane_types: dict[int, str] = {}
    profile_flows: defaultdict[tuple[int, str], list[float]] = defaultdict(list)
    profile_speeds: defaultdict[tuple[int, str], list[float]] = defaultdict(list)
    daily_flows: defaultdict[tuple[int, str, str], list[float]] = defaultdict(list)
    daily_speeds: defaultdict[tuple[int, str, str], list[float]] = defaultdict(list)

    for source in files:
        with gzip.open(source, "rt", newline="") as raw_file:
            for row in csv.reader(raw_file):
                rows_read += 1
                if not _could_match_station_filter(row, criteria):
                    continue
                try:
                    observation = parse_station_row(row)
                except ValueError:
                    invalid_rows += 1
                    continue
                if not criteria.matches(observation):
                    continue

                matching_rows += 1
                station_id = observation.station_id
                lane_types[station_id] = observation.lane_type
                dates[station_id].add(observation.timestamp.date().isoformat())
                if observation.total_flow is None:
                    raise AssertionError("Aggregate measurements must include total flow.")
                flows[station_id].append(observation.total_flow)
                time_key = observation.timestamp.strftime("%H:%M")
                date_key = observation.timestamp.date().isoformat()
                profile_flows[(station_id, time_key)].append(observation.total_flow)
                daily_flows[(station_id, date_key, time_key)].append(observation.total_flow)
                if observation.average_speed_mph is not None:
                    speeds[station_id].append(observation.average_speed_mph)
                    profile_speeds[(station_id, time_key)].append(
                        observation.average_speed_mph
                    )
                    daily_speeds[(station_id, date_key, time_key)].append(
                        observation.average_speed_mph
                    )

    profiles = [
        StationTimeProfile(
            station_id=station_id,
            lane_type=lane_types[station_id],
            matching_rows=len(flows[station_id]),
            date_count=len(dates[station_id]),
            mean_flow_vehicles_per_5_minutes=fmean(flows[station_id]),
            mean_speed_mph=fmean(speeds[station_id]) if speeds[station_id] else None,
            time_profile=[
                {
                    "time": time_key,
                    "observations": len(profile_flows[(station_id, time_key)]),
                    "mean_flow_vehicles_per_5_minutes": fmean(
                        profile_flows[(station_id, time_key)]
                    ),
                    "mean_speed_mph": (
                        fmean(profile_speeds[(station_id, time_key)])
                        if profile_speeds[(station_id, time_key)]
                        else None
                    ),
                }
                for time_key in sorted(
                    key_time
                    for key_station, key_time in profile_flows
                    if key_station == station_id
                )
            ],
            daily_time_profile=[
                {
                    "date": date_key,
                    "time_profile": [
                        {
                            "time": time_key,
                            "observations": len(daily_flows[(station_id, date_key, time_key)]),
                            "mean_flow_vehicles_per_5_minutes": fmean(
                                daily_flows[(station_id, date_key, time_key)]
                            ),
                            "mean_speed_mph": (
                                fmean(daily_speeds[(station_id, date_key, time_key)])
                                if daily_speeds[(station_id, date_key, time_key)]
                                else None
                            ),
                        }
                        for key_station, date_key_for_time, time_key in sorted(daily_flows)
                        if key_station == station_id and date_key_for_time == date_key
                    ],
                }
                for date_key in sorted(
                    {
                        date_key
                        for key_station, date_key, _ in daily_flows
                        if key_station == station_id
                    }
                )
            ],
        )
        for station_id in sorted(flows)
    ]
    return StationProfilesSummary(
        source_files=[str(source) for source in files],
        files_read=len(files),
        rows_read=rows_read,
        invalid_rows=invalid_rows,
        matching_rows=matching_rows,
        station_count=len(profiles),
        profiles=profiles,
    )


def _could_match_station_filter(row: list[str], criteria: PemsFilter) -> bool:
    """Cheaply reject unrelated district-wide rows before parsing their timestamps."""

    if len(row) < 12:
        return True
    try:
        station_id = int(row[1])
        hour = int(row[0][11:13])
        lane_type_matches = (
            row[5] in criteria.lane_types
            if criteria.lane_types is not None
            else row[5] == criteria.lane_type
        )
        return (
            station_id in criteria.station_ids
            and int(row[2]) == criteria.district
            and int(row[3]) == criteria.freeway
            and row[4] == criteria.direction
            and lane_type_matches
            and criteria.start_hour <= hour < criteria.end_hour
        )
    except (TypeError, ValueError):
        return True
