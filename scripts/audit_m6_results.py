"""Independent M6 raw-output and VSL ledger audit; imports no production metrics."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import mean, stdev
from xml.etree import ElementTree as ET

import numpy as np


def equal(actual, expected):
    assert (actual is None and expected is None) or (
        actual is not None
        and expected is not None
        and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-8)
    ), (actual, expected)


def ledger_audit(d, network, config):
    assert d["completed"] and d["restored"] and d["commands"] > 0
    assert d["controller"] == config and d["backend"] == "libsumo"
    control, observed = {}, []
    for edge in ET.parse(network).getroot().findall("edge"):
        if edge.get("id") in config["control_edge_ids"]:
            control.update(
                {lane.get("id"): float(lane.get("speed")) for lane in edge.findall("lane")}
            )
        if edge.get("id") in config["observation_edge_ids"]:
            observed.extend(lane.get("id") for lane in edge.findall("lane"))
    assert d["native_lane_limits"] == control
    assert d["observation_lane_ids"] == sorted(observed)
    assert len(control) == 14 and len(observed) == 9
    limits, previous, exposure, changes = dict(control), False, 0.0, 0
    interval = config["update_seconds"]
    for index, row in enumerate(d["ledger"], 1):
        assert row["time_seconds"] == index * interval
        exposure += interval * sum(limits[lane] < control[lane] for lane in control)
        samples, total = row["vehicle_samples"], row["speed_sum_m_per_s"]
        assert type(samples) is int and samples >= 0 and total >= 0
        speed = total / samples if samples else None
        equal(row["mean_speed_m_per_s"], speed)
        if row["time_seconds"] > config["control_end_seconds"]:
            assert samples == total == 0
        if row["time_seconds"] >= config["control_end_seconds"] or speed is None:
            previous = False
        elif speed < config["activate_below_m_per_s"]:
            previous = True
        elif speed > config["release_above_m_per_s"]:
            previous = False
        assert row["congested"] == previous
        assert row["lane_limits"].keys() == control.keys()
        for lane, native in control.items():
            target = min(native, config["congested_limit_m_per_s"]) if previous else native
            delta = target - limits[lane]
            value = limits[lane] + max(
                -config["max_change_m_per_s"], min(config["max_change_m_per_s"], delta)
            )
            equal(row["lane_limits"][lane], value)
            assert 0 < value <= native
            changes += not math.isclose(value, limits[lane], abs_tol=1e-12)
            limits[lane] = value
    assert d["updates"] == len(d["ledger"]) == 510
    equal(d["limited_lane_seconds"], exposure)
    assert d["commands"] == changes and exposure > 0
    return {
        "updates": len(d["ledger"]),
        "lane_commands": changes,
        "limited_lane_seconds": exposure,
        "congested_decisions": sum(r["congested"] for r in d["ledger"]),
    }


def trajectory_audit(path, ramps):
    # NumPy reductions provide a separate implementation from production's
    # Python accumulators; only one timestep's arrays stay resident.
    stopped, ramp, speeds, squared = [], [], [], 0.0
    count = 0
    with gzip.open(path, "rb") as source:
        tree = ET.iterparse(source, events=("start", "end"))
        _, root = next(tree)
        for event, step in tree:
            if event != "end" or step.tag != "timestep":
                continue
            time = float(step.get("time"))
            if 900 <= time < 8100:
                assert time == 900 + len(stopped)
                vehicles = step.findall("vehicle")
                velocity = np.array([float(v.get("speed")) for v in vehicles])
                acceleration = np.array([float(v.get("acceleration")) for v in vehicles])
                assert np.isfinite(velocity).all() and (velocity >= 0).all()
                assert np.isfinite(acceleration).all()
                mask = velocity < 0.1
                stopped.append(int(mask.sum()))
                ramp.append(
                    sum(
                        bool(s) and v.get("lane").rsplit("_", 1)[0] in ramps
                        for s, v in zip(mask, vehicles, strict=True)
                    )
                )
                squared += float(np.dot(acceleration, acceleration))
                count += len(vehicles)
                if len(vehicles):
                    speeds.append(float(velocity.mean()) / 0.44704)
            root.clear()
    assert len(stopped) == 7200
    return {
        "trajectory_timesteps": len(stopped),
        "populated_timesteps": len(speeds),
        "vehicle_samples": count,
        "mean_stopped_vehicles": float(np.mean(stopped)),
        "peak_stopped_vehicles": max(stopped),
        "stopped_vehicle_seconds": sum(stopped),
        "mean_ramp_stopped_vehicles": float(np.mean(ramp)),
        "peak_ramp_stopped_vehicles": max(ramp),
        "mean_timestep_speed_mph": float(np.mean(speeds)),
        "temporal_mean_speed_stddev_mph": float(np.std(speeds)),
        "mean_squared_acceleration_m2_per_s4": squared / count,
        "rms_acceleration_m_per_s2": math.sqrt(squared / count),
    }


def audit_run(job):
    root, run, old = job
    seed, name = run["seed"], run["scenario"]
    folder = root / run["directory"]
    trips = [
        t.attrib
        for t in ET.parse(folder / f"h0_human_baseline_seed_{seed}.tripinfo.xml")
        .getroot()
        .findall("tripinfo")
    ]
    assert run["accepted"] and len(trips) == 22951
    assert all(float(t["arrival"]) >= 0 and float(t["depart"]) >= 0 for t in trips)
    actual = [t for t in trips if 900 <= float(t["depart"]) < 8100]
    scheduled = [
        t for t in trips if 900 <= round(float(t["depart"]) - float(t["departDelay"]), 2) < 8100
    ]
    exits = sum(900 <= float(t["arrival"]) < 8100 for t in trips)
    values = {
        "window_exit_vehicles": exits,
        "network_exit_throughput_vehicles_per_hour": exits / 2,
        "cohort_completed_vehicles": len(actual),
        "cohort_unfinished_vehicles": 0,
        "cohort_mean_travel_time_seconds": mean(float(t["duration"]) for t in actual),
        "cohort_p95_travel_time_seconds": float(
            np.percentile([float(t["duration"]) for t in actual], 95)
        ),
        "cohort_mean_waiting_time_seconds": mean(float(t["waitingTime"]) for t in actual),
        "cohort_mean_time_loss_seconds": mean(float(t["timeLoss"]) for t in actual),
        "window_actual_departures": len(actual),
        "unreconstructed_scheduled_departures": 0,
        "scheduled_cohort_vehicles": len(scheduled),
        "scheduled_cohort_completed_vehicles": len(scheduled),
        "scheduled_cohort_mean_depart_delay_seconds": mean(
            float(t["departDelay"]) for t in scheduled
        ),
        "scheduled_cohort_mean_total_time_seconds": mean(
            float(t["duration"]) + float(t["departDelay"]) for t in scheduled
        ),
        "whole_run_mean_depart_delay_seconds": mean(float(t["departDelay"]) for t in trips),
        "whole_run_max_depart_delay_seconds": max(float(t["departDelay"]) for t in trips),
    }
    steps = ET.parse(folder / f"h0_summary_seed_{seed}.xml").getroot().findall("step")
    values["peak_insertion_backlog_vehicles"] = max(int(s.get("waiting")) for s in steps)
    values["window_peak_insertion_backlog_vehicles"] = max(
        int(s.get("waiting")) for s in steps if 900 <= float(s.get("time")) < 8100
    )
    final = steps[-1].attrib
    assert final == run["health"]["final_summary"]
    assert int(final["loaded"]) == int(final["inserted"]) == int(final["ended"]) == 22951
    assert all(
        int(final[k]) == 0 for k in ["running", "waiting", "collisions", "teleports", "discarded"]
    )
    log = (folder / f"h0_human_baseline_seed_{seed}.log").read_text().lower()
    assert not run["health"]["warning_lines"]
    assert not any(w in log for w in ["warning", "error", "teleport", "collision", "emergency"])
    route = folder / "h0.rou.xml"
    assert hashlib.sha256(route.read_bytes()).hexdigest() == run["route_sha256"]
    assert run["route_sha256"] == old["route_sha256"]
    assert run["network_sha256"] == old["network_sha256"]
    assert run["provenance"] == old["provenance"]
    for relative, expected in {
        "outputs/us101_corridor/us101_corridor.net.xml": run["network_sha256"],
        "outputs/pems_calibration/us101_m3_upstream_proxy_profiles.json": run["provenance"][
            "mainline_profile_sha256"
        ],
        "outputs/pems_calibration/us101_ramp_station_profiles.json": run["provenance"][
            "ramp_profile_sha256"
        ],
        **run["provenance"]["metadata_sha256"],
    }.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
    routes = {
        r.get("id"): r.get("edges").split() for r in ET.parse(route).getroot().findall("route")
    }
    mainline, ramps = set(routes["us101_northbound"]), set()
    for edges in routes.values():
        if edges[0] not in mainline:
            for edge in edges:
                if edge in mainline:
                    break
                ramps.add(edge)
    assert sorted(ramps) == run["measurement"]["ramp_approach_edge_ids"]
    values.update(trajectory_audit(folder / "trajectory.fcd.xml.gz", ramps))
    assert values.keys() == run["metrics"].keys()
    for metric, value in values.items():
        equal(run["metrics"][metric], value)
    policy = None
    if name == "CENTRAL":
        d = run["controller_diagnostics"]
        assert d == json.loads((folder / "controller_diagnostics.json").read_text())
        policy = ledger_audit(
            d, root / "outputs/us101_corridor/us101_corridor.net.xml", run["controller"]
        )
        assert d["engine_version"].split()[-1] == run["provenance"]["sumo_version"].split()[-1]
    else:
        assert run["metrics"] == old["metrics"]
        assert run["legacy_whole_run_metrics"] == old["legacy_whole_run_metrics"]
        detector_hashes = json.loads((root / "reports/m6/m5_detector_hashes.json").read_text())
        assert (
            hashlib.sha256((root / run["detector_summary_file"]).read_bytes()).hexdigest()
            == (detector_hashes[f"{name}_{seed}"])
        )
        if name == "CACC":
            assert run["controller_diagnostics"] == old["controller_diagnostics"]
    fleet = {
        t["id"]: (
            t["vType"],
            t["speedFactor"],
            round(float(t["depart"]) - float(t["departDelay"]), 2),
        )
        for t in trips
    }
    print(f"Audited {name} seed {seed}: all {len(values)} raw metrics", flush=True)
    return {
        "scenario": name,
        "seed": seed,
        "raw_metric_checks": len(values),
        "exact_m5_replay": name != "CENTRAL",
        "policy": policy,
    }, fleet


def audit(root, report_path, config_path):
    report = json.loads(report_path.read_text())
    old = json.loads((root / "reports/m5/report.json").read_text())
    assert report["accepted"] and len(report["runs"]) == 9
    assert report["source_sha256"] == {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((root / "src/bay_area_traffic_sim").glob("*.py"))
    }
    assert (
        report["experiment_config_sha256"] == hashlib.sha256(config_path.read_bytes()).hexdigest()
    )
    old_index = {(r["scenario"], r["seed"]): r for r in old["runs"]}
    jobs = [
        (root, r, old_index[(r["scenario"] if r["scenario"] != "CENTRAL" else "H0", r["seed"])])
        for r in report["runs"]
    ]
    with ProcessPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(audit_run, jobs))
    fleets = {(r["scenario"], r["seed"]): fleet for r, fleet in results}
    for seed in report["experiment"]["seeds"]:
        assert fleets["H0", seed] == fleets["CACC", seed] == fleets["CENTRAL", seed]
    pairs = []
    for before, after in [("H0", "CACC"), ("H0", "CENTRAL"), ("CACC", "CENTRAL")]:
        metrics = {}
        for metric in report["metric_contract"]:
            reference = [r["metrics"][metric] for r in report["runs"] if r["scenario"] == before]
            treatment = [r["metrics"][metric] for r in report["runs"] if r["scenario"] == after]
            delta = [b - a for a, b in zip(reference, treatment, strict=True)]
            stats = {
                "mean_difference": mean(delta),
                "sample_standard_deviation": stdev(delta),
                "percent_of_reference_mean": 100 * mean(delta) / mean(reference)
                if mean(reference)
                else None,
                "pairs": [
                    {"seed": seed, "difference": v}
                    for seed, v in zip(report["experiment"]["seeds"], delta, strict=True)
                ],
            }
            if before == "H0":
                saved = next(c for c in report["paired_comparisons"] if c["treatment"] == after)
                for key in stats:
                    if key == "pairs":
                        assert saved["metrics"][metric][key] == stats[key]
                    else:
                        equal(saved["metrics"][metric][key], stats[key])
            metrics[metric] = stats
        pairs.append({"reference": before, "treatment": after, "metrics": metrics})
    for group in report["groups"]:
        assert group["accepted"]
        for metric, stats in group["metric_summary"].items():
            values = [
                r["metrics"][metric]
                for r in report["runs"]
                if r["scenario"] == group["scenario"] and r["date"] == group["date"]
            ]
            assert stats["valid_seed_count"] == 3
            equal(stats["mean"], mean(values))
            equal(stats["sample_standard_deviation"], stdev(values))
    return {
        "accepted": True,
        "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
        "runs": [r for r, _ in results],
        "matched_exported_fleets_and_schedules": True,
        "raw_metric_checks": 270,
        "paired_metric_checks": 90,
        "paired_comparisons": pairs,
        "limitations": [
            "Policy observations are audited from the recorded interval totals; "
            "they are not an independent live sensor feed. FCD uses 1 s/0.01 precision."
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("reports/m6/independent_audit.json"))
    parser.add_argument("--config", type=Path, default=Path("configs/us101_m6_experiment.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = audit(root, root / args.report, root / args.config)
    (root / args.output).write_text(json.dumps(result, indent=2) + "\n")
    print("M6 independent audit accepted: 270 raw metrics, 90 paired metrics.")
