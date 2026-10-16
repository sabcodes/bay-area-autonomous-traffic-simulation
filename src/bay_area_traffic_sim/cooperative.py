"""Native SUMO CACC treatment and bounded leader/mode evidence."""

from __future__ import annotations

import json
import math
import os
import subprocess
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

STEP_SECONDS = 0.5
NATIVE_PARAMETERS = {
    "collisionAvoidanceOverride": 0.0,
    "collisionMinGapFactor": 1.0,
    "tauCACCToACC": 1.5,
    "applyDriverState": 0,
    "speedControlGainCACC": -0.4,
    "gapClosingControlGainGap": 0.005,
    "gapClosingControlGainGapDot": 0.05,
    "gapControlGainGap": 0.45,
    "gapControlGainGapDot": 0.0125,
    "collisionAvoidanceGainGap": 0.45,
    "collisionAvoidanceGainGapDot": 0.05,
    "speedControlMinGap": 1.66,
    "speedControlGain": -0.4,
    "gapClosingControlGainSpeed": 0.8,
    "gapClosingControlGainSpace": 0.04,
    "gapControlGainSpeed": 0.07,
    "gapControlGainSpace": 0.23,
    "collisionAvoidanceGainSpeed": 0.23,
    "collisionAvoidanceGainSpace": 0.8,
}
DEFAULT_CONTROLLER = {
    "policy": "sumo_cacc",
    "backend": "libsumo",
    "observation_period_seconds": 1.0,
    "leader_lookahead_meters": 250.0,
    "vehicle_parameters": NATIVE_PARAMETERS,
}


def validate_controller(config: dict, human_parameters: dict) -> None:
    """Reject implicit, unknown or unsafe native-CACC settings before simulation."""
    if not isinstance(config, dict) or set(config) != set(DEFAULT_CONTROLLER):
        raise ValueError("Controller requires exactly the documented policy and parameter keys.")
    if config["policy"] != "sumo_cacc" or config["backend"] not in ("traci", "libsumo"):
        raise ValueError("Unsupported controller policy or backend.")
    for key in ["observation_period_seconds", "leader_lookahead_meters"]:
        value = config[key]
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"Controller {key} must be finite and positive.")
    period = config["observation_period_seconds"]
    if not math.isclose(period / STEP_SECONDS, round(period / STEP_SECONDS)):
        raise ValueError("Controller observation period must match the 0.5 s step.")
    parameters = config["vehicle_parameters"]
    if not isinstance(parameters, dict) or set(parameters) != set(NATIVE_PARAMETERS):
        raise ValueError("Declare exactly the native CACC and ACC fallback parameters.")
    for key, value in parameters.items():
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"Native parameter {key} must be finite.")
    expected = {**NATIVE_PARAMETERS, "tauCACCToACC": human_parameters["tau"]}
    if parameters != expected:
        raise ValueError(
            "M5 fixes native gains, full minGap checking, zero override and frozen tau."
        )


def apply_native_cacc(route_file: Path, config: dict) -> list[dict]:
    """Change only passenger following attributes in a generated, isolated route file."""
    tree = ET.parse(route_file)
    passenger = next(
        (kind for kind in tree.iter("vType") if kind.attrib["id"] == "human_passenger"), None
    )
    if passenger is None:
        raise ValueError("Native CACC requires the frozen passenger vType.")
    passenger.attrib.update(
        {
            "carFollowModel": "CACC",
            **{key: str(value) for key, value in config["vehicle_parameters"].items()},
        }
    )
    ET.indent(tree, space="    ")
    tree.write(route_file, encoding="utf-8", xml_declaration=True)
    return [kind.attrib for kind in tree.iter("vType")]


def run_controlled(
    command: list[str],
    end_seconds: float,
    config: dict,
    diagnostics_path: Path,
    min_gap: float,
) -> dict:
    """Observe native CACC; never override speed, acceleration or lane-change decisions."""
    import traci
    from traci import constants as tc

    connection = None
    diagnostics = {
        "controller": config,
        "backend": config["backend"],
        "engine_version": None,
        "control_step_seconds": STEP_SECONDS,
        "speed_mode": 31,
        "lane_change_mode": 1621,
        "external_control_commands": 0,
        "equipped_vehicles": 0,
        "passenger_samples": 0,
        "passenger_leader_samples": 0,
        "truck_leader_samples": 0,
        "no_leader_samples": 0,
        "missing_state_samples": 0,
        "mode_sample_counts": {},
        "minimum_queried_bumper_gap_meters": None,
        "minimum_realized_acceleration_m_per_s2": None,
        "maximum_realized_acceleration_m_per_s2": None,
        "completed": False,
    }
    passengers = set()
    modes = Counter()
    sample_steps = round(config["observation_period_seconds"] / STEP_SECONDS)
    try:
        if config["backend"] == "libsumo":
            import libsumo

            libsumo.start(command)
            connection = libsumo
        else:
            label = f"m5-{os.getpid()}-{diagnostics_path.resolve()}"
            traci.start(command, label=label, doSwitch=False, stdout=subprocess.DEVNULL)
            connection = traci.getConnection(label)
        diagnostics["engine_version"] = connection.getVersion()[1]
        connection.simulation.subscribe([tc.VAR_DEPARTED_VEHICLES_IDS, tc.VAR_ARRIVED_VEHICLES_IDS])
        for step in range(round(end_seconds / STEP_SECONDS)):
            connection.simulationStep()
            events = connection.simulation.getSubscriptionResults()
            passengers.difference_update(events[tc.VAR_ARRIVED_VEHICLES_IDS])
            for vehicle in sorted(events[tc.VAR_DEPARTED_VEHICLES_IDS]):
                connection.vehicle.subscribe(
                    vehicle, [tc.VAR_SPEED, tc.VAR_ACCELERATION, tc.VAR_TYPE]
                )
                state = connection.vehicle.getSubscriptionResults(vehicle)
                if state[tc.VAR_TYPE] == "human_passenger":
                    if (
                        connection.vehicle.getSpeedMode(vehicle) != 31
                        or connection.vehicle.getLaneChangeMode(vehicle) != 1621
                    ):
                        raise ValueError("Unexpected native safety or lane-change mode.")
                    passengers.add(vehicle)
                    diagnostics["equipped_vehicles"] += 1
            if (step + 1) % sample_steps:
                continue
            snapshot = connection.vehicle.getAllSubscriptionResults()
            for vehicle in sorted(passengers):
                state = snapshot.get(vehicle)
                if state is None:
                    diagnostics["missing_state_samples"] += 1
                    continue
                diagnostics["passenger_samples"] += 1
                modes[
                    connection.vehicle.getParameter(vehicle, "caccVehicleMode") or "unreported"
                ] += 1
                acceleration = state[tc.VAR_ACCELERATION]
                for key, operation in [
                    ("minimum_realized_acceleration_m_per_s2", min),
                    ("maximum_realized_acceleration_m_per_s2", max),
                ]:
                    previous = diagnostics[key]
                    diagnostics[key] = (
                        acceleration if previous is None else operation(previous, acceleration)
                    )
                leader = connection.vehicle.getLeader(vehicle, config["leader_lookahead_meters"])
                if not leader or not leader[0] or leader[1] > config["leader_lookahead_meters"]:
                    diagnostics["no_leader_samples"] += 1
                    continue
                ahead = snapshot.get(leader[0])
                if ahead is None:
                    diagnostics["missing_state_samples"] += 1
                    continue
                key = (
                    "passenger_leader_samples"
                    if ahead[tc.VAR_TYPE] == "human_passenger"
                    else "truck_leader_samples"
                )
                diagnostics[key] += 1
                gap = leader[1] + min_gap
                previous = diagnostics["minimum_queried_bumper_gap_meters"]
                diagnostics["minimum_queried_bumper_gap_meters"] = (
                    gap if previous is None else min(previous, gap)
                )
        diagnostics["completed"] = True
    finally:
        diagnostics["mode_sample_counts"] = dict(sorted(modes.items()))
        try:
            if connection is not None:
                connection.close()
        finally:
            diagnostics_path.write_text(json.dumps(diagnostics, indent=2, allow_nan=False) + "\n")
    return diagnostics
