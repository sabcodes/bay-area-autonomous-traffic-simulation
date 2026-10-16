"""Small, transparent metrics for early SUMO experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

METERS_PER_SECOND_TO_MPH = 2.2369362921


@dataclass(frozen=True)
class RunMetrics:
    """Summary of vehicles that finished a simulation run."""

    completed_vehicles: int
    average_travel_time_seconds: float | None
    average_waiting_time_seconds: float | None
    average_time_loss_seconds: float | None
    average_trip_speed_mph: float | None = None


def summarize_tripinfos(root: ElementTree.Element) -> RunMetrics:
    """Summarize SUMO ``tripinfo`` elements from an already-parsed XML tree."""

    trips = [
        trip for trip in root.findall("tripinfo") if float(trip.attrib.get("arrival", "0")) >= 0
    ]
    if not trips:
        return RunMetrics(0, None, None, None, None)

    durations = [float(trip.attrib["duration"]) for trip in trips]
    waiting_times = [float(trip.attrib["waitingTime"]) for trip in trips]
    time_losses = [float(trip.attrib["timeLoss"]) for trip in trips]
    trip_speeds_mph = [
        float(trip.attrib["routeLength"])
        / float(trip.attrib["duration"])
        * METERS_PER_SECOND_TO_MPH
        for trip in trips
        if float(trip.attrib["duration"]) > 0 and "routeLength" in trip.attrib
    ]
    count = len(trips)
    return RunMetrics(
        completed_vehicles=count,
        average_travel_time_seconds=sum(durations) / count,
        average_waiting_time_seconds=sum(waiting_times) / count,
        average_time_loss_seconds=sum(time_losses) / count,
        average_trip_speed_mph=(
            sum(trip_speeds_mph) / len(trip_speeds_mph) if trip_speeds_mph else None
        ),
    )


def read_tripinfo(path: Path) -> RunMetrics:
    """Load a SUMO trip-info report and return its completed-trip metrics."""

    return summarize_tripinfos(ElementTree.parse(path).getroot())
