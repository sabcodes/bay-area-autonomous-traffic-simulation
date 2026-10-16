"""Windowed M4 metrics from native SUMO trajectories and completed trip records."""

from __future__ import annotations

import gzip
import math
from pathlib import Path
from statistics import fmean, pstdev
from xml.etree import ElementTree as ET

from bay_area_traffic_sim.metrics import METERS_PER_SECOND_TO_MPH


def read_window_trip_metrics(path: Path, begin: float, end: float) -> dict:
    """Follow departure-window trips through clearance; count exits in the window."""
    durations, waits, losses = [], [], []
    exits = unfinished = 0
    for _, trip in ET.iterparse(path, events=("end",)):
        if trip.tag != "tripinfo":
            continue
        depart, arrival = float(trip.attrib["depart"]), float(trip.attrib["arrival"])
        exits += begin <= arrival < end
        if begin <= depart < end:
            if arrival < 0:
                unfinished += 1
            else:
                durations.append(float(trip.attrib["duration"]))
                waits.append(float(trip.attrib["waitingTime"]))
                losses.append(float(trip.attrib["timeLoss"]))
        trip.clear()
    durations.sort()
    p95 = None
    if durations:
        position = (len(durations) - 1) * 0.95
        lower = math.floor(position)
        p95 = durations[lower] + (durations[math.ceil(position)] - durations[lower]) * (
            position - lower
        )
    return {
        "window_exit_vehicles": exits,
        "network_exit_throughput_vehicles_per_hour": exits * 3600 / (end - begin),
        "cohort_completed_vehicles": len(durations),
        "cohort_unfinished_vehicles": unfinished,
        "cohort_mean_travel_time_seconds": fmean(durations) if durations else None,
        "cohort_p95_travel_time_seconds": p95,
        "cohort_mean_waiting_time_seconds": fmean(waits) if waits else None,
        "cohort_mean_time_loss_seconds": fmean(losses) if losses else None,
    }


def entrance_queue_edges(route_file: Path) -> set[str]:
    """Find entrance-route edges before their first shared through-route edge."""
    routes = ET.parse(route_file).getroot().findall("route")
    through = next(route for route in routes if route.attrib["id"] == "us101_northbound")
    mainline = set(through.attrib["edges"].split())
    edges = set()
    for route in routes:
        route_edges = route.attrib["edges"].split()
        if not route_edges or route_edges[0] in mainline:
            continue
        for edge in route_edges:
            if edge in mainline:
                break
            edges.add(edge)
    return edges


def read_trajectory_metrics(
    path: Path,
    begin: float,
    end: float,
    period: float,
    stop_speed: float,
    ramp_edges: set[str],
) -> dict:
    """Stream fixed-period samples, retaining at most one timestep's vehicles."""
    expected_samples = round((end - begin) / period)
    if expected_samples <= 0 or not math.isclose(expected_samples * period, end - begin):
        raise ValueError("Measurement window must contain a whole number of samples.")
    samples = vehicles = stopped_sum = stopped_max = ramp_sum = ramp_max = 0
    acceleration_squared = 0.0
    mean_speeds = []
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as source:
        tree = ET.iterparse(source, events=("start", "end"))
        _, root = next(tree)
        for event, step in tree:
            if event != "end" or step.tag != "timestep":
                continue
            time = float(step.attrib["time"])
            if begin <= time < end:
                if not math.isclose(time, begin + samples * period, abs_tol=1e-6):
                    raise ValueError(f"Missing or irregular trajectory timestep at {time}.")
                stopped = ramp_stopped = 0
                speeds = []
                for vehicle in step.findall("vehicle"):
                    speed = float(vehicle.attrib["speed"])
                    acceleration = float(vehicle.attrib["acceleration"])
                    if not math.isfinite(speed) or speed < 0 or not math.isfinite(acceleration):
                        raise ValueError("Trajectory speed/acceleration must be finite and valid.")
                    speeds.append(speed)
                    acceleration_squared += acceleration * acceleration
                    if speed < stop_speed:
                        stopped += 1
                        if vehicle.attrib["lane"].rsplit("_", 1)[0] in ramp_edges:
                            ramp_stopped += 1
                vehicles += len(speeds)
                if speeds:
                    mean_speeds.append(fmean(speeds) * METERS_PER_SECOND_TO_MPH)
                samples += 1
                stopped_sum += stopped
                stopped_max = max(stopped_max, stopped)
                ramp_sum += ramp_stopped
                ramp_max = max(ramp_max, ramp_stopped)
            root.clear()
    if samples != expected_samples:
        raise ValueError(f"Expected {expected_samples} trajectory samples; found {samples}.")
    mean_square = acceleration_squared / vehicles if vehicles else None
    return {
        "trajectory_timesteps": samples,
        "populated_timesteps": len(mean_speeds),
        "vehicle_samples": vehicles,
        "mean_stopped_vehicles": stopped_sum / samples,
        "peak_stopped_vehicles": stopped_max,
        "stopped_vehicle_seconds": stopped_sum * period,
        "mean_ramp_stopped_vehicles": ramp_sum / samples,
        "peak_ramp_stopped_vehicles": ramp_max,
        "mean_timestep_speed_mph": fmean(mean_speeds) if mean_speeds else None,
        "temporal_mean_speed_stddev_mph": pstdev(mean_speeds) if mean_speeds else None,
        "mean_squared_acceleration_m2_per_s4": mean_square,
        "rms_acceleration_m_per_s2": math.sqrt(mean_square) if mean_square is not None else None,
    }


def clean_and_cleared(health: dict) -> bool:
    """Missing health evidence cannot qualify as a clean, fully cleared run."""
    try:
        final = health["final_summary"]
        return (
            not health["warning_lines"]
            and all(
                float(final[key]) == 0
                for key in ("running", "waiting", "collisions", "teleports", "discarded")
            )
            and float(final["loaded"]) == float(final["inserted"]) == float(final["ended"])
        )
    except (KeyError, TypeError, ValueError):
        return False


def read_insertion_metrics(trips: Path, summary: Path, begin: float, end: float) -> dict:
    """Keep actual and scheduled cohorts separate; expose temporary insertion backlog."""
    delays, scheduled_delays, scheduled_totals = [], [], []
    scheduled_count = actual_count = unknown_schedule = 0
    for _, trip in ET.iterparse(trips, events=("end",)):
        if trip.tag != "tripinfo":
            continue
        depart = float(trip.attrib["depart"])
        delay = float(trip.attrib["departDelay"])
        arrival = float(trip.attrib["arrival"])
        actual_count += begin <= depart < end
        if depart < 0 or delay < 0:
            unknown_schedule += 1
        else:
            delays.append(delay)
            # Native tripinfo rounds seconds to two decimals; tolerate its boundary rounding.
            scheduled = round(depart - delay, 2)
            if begin <= scheduled < end:
                scheduled_count += 1
                scheduled_delays.append(delay)
                if arrival >= 0:
                    scheduled_totals.append(float(trip.attrib["duration"]) + delay)
        trip.clear()
    peak = window_peak = 0
    for _, step in ET.iterparse(summary, events=("end",)):
        if step.tag == "step":
            waiting = int(step.attrib["waiting"])
            peak = max(peak, waiting)
            if begin <= float(step.attrib["time"]) < end:
                window_peak = max(window_peak, waiting)
            step.clear()
    return {
        "window_actual_departures": actual_count,
        "unreconstructed_scheduled_departures": unknown_schedule,
        "scheduled_cohort_vehicles": scheduled_count if not unknown_schedule else None,
        "scheduled_cohort_completed_vehicles": len(scheduled_totals)
        if not unknown_schedule
        else None,
        "scheduled_cohort_mean_depart_delay_seconds": (
            fmean(scheduled_delays) if scheduled_delays and not unknown_schedule else None
        ),
        "scheduled_cohort_mean_total_time_seconds": (
            fmean(scheduled_totals) if scheduled_totals and not unknown_schedule else None
        ),
        "whole_run_mean_depart_delay_seconds": fmean(delays) if delays else None,
        "whole_run_max_depart_delay_seconds": max(delays) if delays else None,
        "peak_insertion_backlog_vehicles": peak,
        "window_peak_insertion_backlog_vehicles": window_peak,
    }
