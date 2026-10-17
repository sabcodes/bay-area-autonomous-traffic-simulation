"""Explainable centralized feedback VSL through native lane speed limits."""

from __future__ import annotations

import json
import math
from pathlib import Path

STEP = 0.5
DEFAULT_CONTROLLER = {
    "policy": "central_vsl",
    "backend": "libsumo",
    "control_edge_ids": ["395354963", "28485321", "28485321-AddedOffRampEdge"],
    "observation_edge_ids": ["509747302", "509747310-AddedOnRampEdge"],
    "update_seconds": 30.0,
    "activate_below_m_per_s": 15.0,
    "release_above_m_per_s": 20.0,
    "congested_limit_m_per_s": 25.0,
    "max_change_m_per_s": 1.0,
    "control_end_seconds": 8100.0,
}


def validate_controller(config: dict) -> None:
    """Require the complete explicit contract before starting a runtime."""
    if set(config) != set(DEFAULT_CONTROLLER):
        raise ValueError("Central controller requires exactly the documented keys.")
    if config["policy"] != "central_vsl" or config["backend"] != "libsumo":
        raise ValueError("Central VSL requires policy central_vsl and backend libsumo.")
    for key in ("control_edge_ids", "observation_edge_ids"):
        edges = config[key]
        if (
            not isinstance(edges, list)
            or not edges
            or any(not isinstance(e, str) or not e or e.startswith(":") for e in edges)
            or len(set(edges)) != len(edges)
        ):
            raise ValueError("Central edge lists must be nonempty, unique external edge IDs.")
    if set(config["control_edge_ids"]) & set(config["observation_edge_ids"]):
        raise ValueError("Control and observation edges must be disjoint.")
    for key in set(config) - {"policy", "backend", "control_edge_ids", "observation_edge_ids"}:
        value = config[key]
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"Central {key} must be finite and positive.")
    if config["activate_below_m_per_s"] >= config["release_above_m_per_s"]:
        raise ValueError("Central hysteresis thresholds must be increasing.")
    update, end = config["update_seconds"], config["control_end_seconds"]
    if not math.isclose(update / STEP, round(update / STEP)) or not math.isclose(
        end / update, round(end / update)
    ):
        raise ValueError("Central update must align with steps and divide control end.")


def congestion_mode(config: dict, previous: bool, speed: float | None) -> bool:
    if speed is None or speed > config["release_above_m_per_s"]:
        return False
    if speed < config["activate_below_m_per_s"]:
        return True
    return previous


def next_limit(config: dict, current: float, native: float, congested: bool) -> float:
    target = min(native, config["congested_limit_m_per_s"]) if congested else native
    change = config["max_change_m_per_s"]
    return min(native, max(current - change, min(current + change, target)))


def observed_totals(observations: list[tuple[int, float]]) -> tuple[int, float]:
    count, weighted = 0, 0.0
    for number, speed in observations:
        if type(number) is not int or number < 0:
            raise ValueError("Invalid central observation count.")
        if number:
            if not math.isfinite(speed) or speed < 0:
                raise ValueError("Invalid populated central observation speed.")
            count += number
            weighted += number * speed
    return count, weighted


def run_controlled(command: list[str], end_seconds: float, config: dict, path: Path) -> dict:
    """Apply only lane limits; record every decision and restore on every exit."""
    import libsumo as connection

    validate_controller(config)
    diagnostics = {
        "controller": config,
        "backend": "libsumo",
        "engine_version": None,
        "completed": False,
        "restored": False,
        "updates": 0,
        "commands": 0,
        "limited_lane_seconds": 0.0,
        "native_lane_limits": {},
        "observation_lane_ids": [],
        "ledger": [],
    }
    started = False
    native = diagnostics["native_lane_limits"]
    try:
        connection.start(command)
        started = True
        diagnostics["engine_version"] = connection.getVersion()[1]
        lanes = list(connection.lane.getIDList())
        by_edge = {}
        for lane in lanes:
            by_edge.setdefault(connection.lane.getEdgeID(lane), []).append(lane)
        for edge in config["control_edge_ids"] + config["observation_edge_ids"]:
            if edge not in by_edge:
                raise ValueError(f"Unknown or empty central edge: {edge}")
        control = sorted(lane for edge in config["control_edge_ids"] for lane in by_edge[edge])
        observed = sorted(lane for edge in config["observation_edge_ids"] for lane in by_edge[edge])
        diagnostics["observation_lane_ids"] = observed
        for lane in control:
            value = connection.lane.getMaxSpeed(lane)
            if not math.isfinite(value) or value <= 0:
                raise ValueError("Invalid native central lane speed.")
            native[lane] = value
        limits = dict(native)
        every = round(config["update_seconds"] / STEP)
        count, weighted, congested = 0, 0.0, False
        for step in range(1, round(end_seconds / STEP) + 1):
            diagnostics["limited_lane_seconds"] += STEP * sum(
                limits[lane] < native[lane] for lane in control
            )
            connection.simulationStep()
            time = step * STEP
            if time <= config["control_end_seconds"]:
                n, total = observed_totals(
                    [
                        (
                            connection.lane.getLastStepVehicleNumber(lane),
                            connection.lane.getLastStepMeanSpeed(lane),
                        )
                        for lane in observed
                    ]
                )
                count += n
                weighted += total
            if step % every:
                continue
            speed = weighted / count if count else None
            congested = (
                congestion_mode(config, congested, speed)
                if time < config["control_end_seconds"]
                else False
            )
            for lane in control:
                value = next_limit(config, limits[lane], native[lane], congested)
                if value != limits[lane]:
                    connection.lane.setMaxSpeed(lane, value)
                    diagnostics["commands"] += 1
                limits[lane] = value
            diagnostics["updates"] += 1
            diagnostics["ledger"].append(
                {
                    "time_seconds": time,
                    "vehicle_samples": count,
                    "speed_sum_m_per_s": weighted,
                    "mean_speed_m_per_s": speed,
                    "congested": congested,
                    "lane_limits": dict(limits),
                }
            )
            count, weighted = 0, 0.0
        diagnostics["completed"] = True
    finally:
        try:
            if started:
                try:
                    for lane, value in native.items():
                        connection.lane.setMaxSpeed(lane, value)
                    diagnostics["restored"] = True
                finally:
                    connection.close()
        finally:
            path.write_text(json.dumps(diagnostics, indent=2, allow_nan=False) + "\n")
    return diagnostics
