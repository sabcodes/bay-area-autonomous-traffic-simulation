"""Independently audit M5 saved output; avoid reusing measurement implementations."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, stdev
from xml.etree import ElementTree as ET


def audit(report_path: Path, root: Path) -> dict:
    report = json.loads(report_path.read_text())
    m4 = json.loads((root / "reports/m4/report.json").read_text())
    runs = report["runs"]
    assert len(runs) == 6 and report["accepted"]
    checks = []
    fleets = {}
    for run in runs:
        seed, scenario = run["seed"], run["scenario"]
        folder = root / run["directory"]
        records = ET.parse(folder / f"h0_human_baseline_seed_{seed}.tripinfo.xml").getroot()
        trips = [trip.attrib for trip in records.findall("tripinfo")]
        assert len(trips) == 22951
        assert all(float(trip["arrival"]) >= 0 and float(trip["depart"]) >= 0 for trip in trips)
        begin, end = 900, 8100
        actual = [trip for trip in trips if begin <= float(trip["depart"]) < end]
        scheduled = [
            trip
            for trip in trips
            if begin <= round(float(trip["depart"]) - float(trip["departDelay"]), 2) < end
        ]
        metrics = run["metrics"]
        independently_computed = {
            "window_actual_departures": len(actual),
            "cohort_completed_vehicles": len(actual),
            "cohort_mean_travel_time_seconds": mean(float(trip["duration"]) for trip in actual),
            "scheduled_cohort_vehicles": len(scheduled),
            "scheduled_cohort_completed_vehicles": len(scheduled),
            "scheduled_cohort_mean_depart_delay_seconds": mean(
                float(trip["departDelay"]) for trip in scheduled
            ),
            "scheduled_cohort_mean_total_time_seconds": mean(
                float(trip["duration"]) + float(trip["departDelay"]) for trip in scheduled
            ),
            "whole_run_mean_depart_delay_seconds": mean(
                float(trip["departDelay"]) for trip in trips
            ),
            "whole_run_max_depart_delay_seconds": max(float(trip["departDelay"]) for trip in trips),
            "network_exit_throughput_vehicles_per_hour": sum(
                begin <= float(trip["arrival"]) < end for trip in trips
            )
            / 2,
        }
        steps = ET.parse(folder / f"h0_summary_seed_{seed}.xml").getroot().findall("step")
        independently_computed["peak_insertion_backlog_vehicles"] = max(
            int(step.attrib["waiting"]) for step in steps
        )
        independently_computed["window_peak_insertion_backlog_vehicles"] = max(
            int(step.attrib["waiting"])
            for step in steps
            if begin <= float(step.attrib["time"]) < end
        )
        for metric, value in independently_computed.items():
            assert math.isclose(metrics[metric], value, abs_tol=1e-9), (scenario, seed, metric)
        final = run["health"]["final_summary"]
        assert int(final["loaded"]) == int(final["inserted"]) == int(final["ended"]) == len(trips)
        assert not run["health"]["warning_lines"]
        assert all(
            int(final[key]) == 0
            for key in ["running", "waiting", "discarded", "collisions", "teleports"]
        )
        route = folder / "h0.rou.xml"
        assert hashlib.sha256(route.read_bytes()).hexdigest() == run["route_sha256"]
        matching_m4 = next(previous for previous in m4["runs"] if previous["seed"] == seed)
        assert run["route_sha256"] == matching_m4["route_sha256"]
        assert run["network_sha256"] == matching_m4["network_sha256"]
        assert run["provenance"] == matching_m4["provenance"]
        replay = None
        if scenario == "H0":
            assert run["legacy_whole_run_metrics"] == matching_m4["legacy_whole_run_metrics"]
            assert all(metrics[key] == value for key, value in matching_m4["metrics"].items())
            old_detector = root / matching_m4["detector_summary_file"]
            new_detector = root / run["detector_summary_file"]
            assert new_detector.read_bytes() == old_detector.read_bytes()
            replay = (
                "all M4 metrics and legacy trip metrics equal; detector summaries byte-identical"
            )
        else:
            diagnostics = run["controller_diagnostics"]
            assert diagnostics["completed"] and diagnostics["native_fallbacks"] == 0
            assert diagnostics["cooperative_commands"] > 0 and diagnostics["acc_commands"] > 0
            assert diagnostics["commands"] == sum(
                diagnostics[key]
                for key in ["cooperative_commands", "acc_commands", "cruise_commands"]
            )
            assert diagnostics["speed_mode"] == 31 and diagnostics["lane_change_mode"] == 1621
        fleets[(scenario, seed)] = {
            trip["id"]: (trip["vType"], trip["speedFactor"]) for trip in trips
        }
        checks.append(
            {
                "scenario": scenario,
                "seed": seed,
                "accepted": True,
                "independent_metrics": independently_computed,
                "m4_replay": replay,
            }
        )
    fleet_checks = []
    for seed in report["experiment"]["seeds"]:
        before, after = fleets[("H0", seed)], fleets[("CACC", seed)]
        assert before.keys() == after.keys()
        differences = sum(before[key] != after[key] for key in before)
        fleet_checks.append(
            {
                "seed": seed,
                "same_vehicle_ids": True,
                "type_or_speed_factor_differences": differences,
            }
        )
        assert differences == 0, (
            "The realized fleet differs; investigate before accepting comparison."
        )
    paired_checks = 0
    comparison = report["paired_comparisons"][0]
    for metric, stats in comparison["metrics"].items():
        by_scenario = {
            name: {run["seed"]: run["metrics"][metric] for run in runs if run["scenario"] == name}
            for name in ["H0", "CACC"]
        }
        deltas = [
            by_scenario["CACC"][seed] - by_scenario["H0"][seed]
            for seed in sorted(report["experiment"]["seeds"])
        ]
        assert math.isclose(stats["mean_difference"], mean(deltas), abs_tol=1e-9)
        assert math.isclose(stats["sample_standard_deviation"], stdev(deltas), abs_tol=1e-9)
        assert [pair["difference"] for pair in stats["pairs"]] == deltas
        reference_mean = mean(by_scenario["H0"].values())
        if reference_mean:
            assert math.isclose(
                stats["percent_of_reference_mean"],
                100 * mean(deltas) / reference_mean,
                abs_tol=1e-9,
            )
        else:
            assert stats["percent_of_reference_mean"] is None
        paired_checks += 1
    for group in report["groups"]:
        matching = [run for run in runs if run["scenario"] == group["scenario"]]
        for metric, stats in group["metric_summary"].items():
            values = [run["metrics"][metric] for run in matching]
            assert math.isclose(stats["mean"], mean(values), abs_tol=1e-9)
            assert math.isclose(stats["sample_standard_deviation"], stdev(values), abs_tol=1e-9)
    return {
        "accepted": True,
        "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
        "runs": checks,
        "fleet_checks": fleet_checks,
        "paired_metric_checks": paired_checks,
        "limitations": [
            "Independent trip and summary audit; controller formula and trajectories "
            "are covered separately by tests and the M4 measurement checks."
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = audit(root / args.report, root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"Audit accepted: {len(result['runs'])} runs, "
        f"{result['paired_metric_checks']} paired metrics"
    )
