"""Conservative deterministic CACC commands inside SUMO's native safety envelope."""

from __future__ import annotations

import json
import math
import os
import subprocess
from pathlib import Path

STEP_SECONDS = 0.5
DEFAULT_CONTROLLER = {
    "policy": "cacc_overlay",
    "backend": "libsumo",
    "headway_seconds": 1.5,
    "cruise_gain": 0.4,
    "gap_gain": 0.2,
    "relative_speed_gain": 0.8,
    "feedforward_gain": 0.5,
    "max_acceleration": 2.6,
    "max_deceleration": 4.5,
    "communication_range_meters": 250.0,
}


def validate_controller(config: dict, human_parameters: dict) -> None:
    """Require explicit finite settings compatible with the frozen safety layer."""
    if not isinstance(config, dict) or set(config) != set(DEFAULT_CONTROLLER):
        raise ValueError("Controller requires exactly the documented policy and parameter keys.")
    if config["policy"] != "cacc_overlay":
        raise ValueError("Unsupported controller policy.")
    if config["backend"] not in ("traci", "libsumo"):
        raise ValueError("Controller backend must be traci or libsumo.")
    for key in set(config) - {"policy", "backend"}:
        value = config[key]
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError(f"Controller {key} must be finite and nonnegative.")
    if config["headway_seconds"] < max(STEP_SECONDS, human_parameters["tau"]):
        raise ValueError("Controller headway must retain the frozen safety headway.")
    for setting, physical in [("max_acceleration", "accel"), ("max_deceleration", "decel")]:
        if not 0 < config[setting] <= human_parameters[physical]:
            raise ValueError(f"Controller {setting} must respect frozen passenger limits.")
    if config["communication_range_meters"] <= 0 or config["feedforward_gain"] > 1:
        raise ValueError("Controller needs positive range and feedforward gain in [0, 1].")


def requested_speed(
    config: dict,
    speed: float,
    allowed_speed: float,
    leader: tuple[float, float, float, bool] | None = None,
) -> float:
    """Return next-step speed; leader tuple is (TraCI gap, speed, accel, cooperative)."""
    acceleration = config["cruise_gain"] * (allowed_speed - speed)
    if leader is not None:
        gap, leader_speed, leader_acceleration, cooperative = leader
        follow = (
            config["gap_gain"] * (gap - config["headway_seconds"] * speed)
            + config["relative_speed_gain"] * (leader_speed - speed)
            + (config["feedforward_gain"] * leader_acceleration if cooperative else 0)
        )
        acceleration = min(acceleration, follow)
    acceleration = max(-config["max_deceleration"], min(config["max_acceleration"], acceleration))
    return max(0.0, min(allowed_speed, speed + STEP_SECONDS * acceleration))


def needs_native_maneuver(lane_id: str, best_lanes: tuple | list) -> bool:
    """Yield speed authority when the current lane requires a strategic transition."""
    current = next((lane for lane in best_lanes if lane[0] == lane_id), None)
    return current is None or current[3] != 0 or not current[4]


def run_controlled(
    command: list[str],
    end_seconds: float,
    config: dict,
    diagnostics_path: Path,
    min_gap: float,
) -> dict:
    """Subscribe to bounded leaders and command passengers from one snapshot per step."""
    import traci
    from traci import constants as tc

    label = f"m5-{os.getpid()}-{diagnostics_path.resolve()}"
    connection = None
    diagnostics = {
        "controller": config,
        "backend": config["backend"],
        "engine_version": None,
        "control_step_seconds": STEP_SECONDS,
        "speed_mode": 31,
        "lane_change_mode": 1621,
        "controlled_vehicles": 0,
        "commands": 0,
        "cooperative_commands": 0,
        "acc_commands": 0,
        "cruise_commands": 0,
        "native_fallbacks": 0,
        "strategic_native_releases": 0,
        "minimum_queried_bumper_gap_meters": None,
        "minimum_realized_acceleration_m_per_s2": None,
        "maximum_realized_acceleration_m_per_s2": None,
        "completed": False,
    }
    passengers = set()
    try:
        if config["backend"] == "libsumo":
            import libsumo

            libsumo.start(command)
            connection = libsumo
        else:
            traci.start(command, label=label, doSwitch=False, stdout=subprocess.DEVNULL)
            connection = traci.getConnection(label)
        diagnostics["engine_version"] = connection.getVersion()[1]
        connection.simulation.subscribe([tc.VAR_DEPARTED_VEHICLES_IDS, tc.VAR_ARRIVED_VEHICLES_IDS])
        for _ in range(round(end_seconds / STEP_SECONDS)):
            connection.simulationStep()
            events = connection.simulation.getSubscriptionResults()
            passengers.difference_update(events[tc.VAR_ARRIVED_VEHICLES_IDS])
            for vehicle in sorted(events[tc.VAR_DEPARTED_VEHICLES_IDS]):
                connection.vehicle.subscribe(
                    vehicle,
                    [
                        tc.VAR_SPEED,
                        tc.VAR_ACCELERATION,
                        tc.VAR_ALLOWED_SPEED,
                        tc.VAR_TYPE,
                        tc.VAR_LANE_ID,
                    ],
                )
                state = connection.vehicle.getSubscriptionResults(vehicle)
                if state[tc.VAR_TYPE] == "human_passenger":
                    if (
                        connection.vehicle.getSpeedMode(vehicle) != 31
                        or connection.vehicle.getLaneChangeMode(vehicle) != 1621
                    ):
                        raise ValueError("Unexpected native safety or lane-change mode.")
                    passengers.add(vehicle)
                    diagnostics["controlled_vehicles"] += 1
            snapshot = connection.vehicle.getAllSubscriptionResults()
            for vehicle in sorted(passengers):
                if vehicle in snapshot:
                    snapshot[vehicle][tc.VAR_BEST_LANES] = connection.vehicle.getBestLanes(vehicle)
                    snapshot[vehicle][tc.VAR_LEADER] = connection.vehicle.getLeader(
                        vehicle, config["communication_range_meters"]
                    )
            for vehicle in sorted(passengers):
                state = snapshot.get(vehicle)
                if state is None:
                    connection.vehicle.setSpeed(vehicle, -1)
                    diagnostics["native_fallbacks"] += 1
                    continue
                speed = state[tc.VAR_SPEED]
                realized = state[tc.VAR_ACCELERATION]
                for key, operation in [
                    ("minimum_realized_acceleration_m_per_s2", min),
                    ("maximum_realized_acceleration_m_per_s2", max),
                ]:
                    previous = diagnostics[key]
                    diagnostics[key] = (
                        realized if previous is None else operation(previous, realized)
                    )
                if needs_native_maneuver(state[tc.VAR_LANE_ID], state[tc.VAR_BEST_LANES]):
                    connection.vehicle.setSpeed(vehicle, -1)
                    diagnostics["strategic_native_releases"] += 1
                    continue
                leader = state[tc.VAR_LEADER]
                following = None
                mode = "cruise_commands"
                if leader and leader[0] and leader[1] <= config["communication_range_meters"]:
                    ahead = snapshot.get(leader[0])
                    if ahead is None:
                        connection.vehicle.setSpeed(vehicle, -1)
                        diagnostics["native_fallbacks"] += 1
                        continue
                    cooperative = ahead[tc.VAR_TYPE] == "human_passenger"
                    following = (
                        leader[1],
                        ahead[tc.VAR_SPEED],
                        ahead[tc.VAR_ACCELERATION],
                        cooperative,
                    )
                    mode = "cooperative_commands" if cooperative else "acc_commands"
                    bumper_gap = leader[1] + min_gap
                    previous = diagnostics["minimum_queried_bumper_gap_meters"]
                    diagnostics["minimum_queried_bumper_gap_meters"] = (
                        bumper_gap if previous is None else min(previous, bumper_gap)
                    )
                target = requested_speed(config, speed, state[tc.VAR_ALLOWED_SPEED], following)
                if not math.isfinite(target):
                    raise ValueError("Nonfinite controller command.")
                connection.vehicle.setSpeed(vehicle, target)
                diagnostics["commands"] += 1
                diagnostics[mode] += 1
        diagnostics["completed"] = True
    finally:
        try:
            if connection is not None:
                connection.close()
        finally:
            diagnostics_path.write_text(json.dumps(diagnostics, indent=2, allow_nan=False) + "\n")
    return diagnostics
