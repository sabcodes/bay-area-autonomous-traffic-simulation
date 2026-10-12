"""Run the predeclared M3 calibration and validation cases with isolated outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from statistics import fmean

from bay_area_traffic_sim.calibration import compare_detector_profiles
from bay_area_traffic_sim.real_corridor import _load_baseline_config, run_human_baseline
from bay_area_traffic_sim.toy_corridor import repository_root


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "phase", choices=["reference", "candidates", "calibration", "validation", "sensitivity"]
    )
    parser.add_argument("--config", default="configs/us101_m3_experiment.json")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--cases", nargs="+", help="Run a named subset of calibration candidates.")
    args = parser.parse_args()
    root = repository_root()
    experiment = json.loads((root / args.config).read_text())
    base = _load_baseline_config(Path(experiment["baseline_config"]), root)
    if args.phase == "reference" and experiment.get("reference_baseline_config"):
        base = _load_baseline_config(Path(experiment["reference_baseline_config"]), root)
    if set(experiment["calibration_dates"]) & set(experiment["validation_dates"]):
        raise ValueError("Calibration and validation dates must be disjoint.")
    selected = experiment["selected_candidate"]
    if args.phase not in {"candidates", "reference"} and selected not in experiment["candidates"]:
        raise ValueError("Record a selected calibration candidate before running this phase.")
    if args.phase == "reference":
        cases = [("reference", {"tau": 1.2}, 0.0, 0.0)]
        dates = [experiment["representative_calibration_date"]]
        seeds = [42]
    elif args.phase == "candidates":
        cases = [
            (name, params, experiment["truck_share"], 1.0)
            for name, params in experiment["candidates"].items()
        ]
        if args.cases:
            if set(args.cases) - experiment["candidates"].keys():
                raise ValueError("Unknown calibration candidate name.")
            cases = [case for case in cases if case[0] in args.cases]
        dates = [experiment["representative_calibration_date"]]
        seeds = [42]
    elif args.phase == "sensitivity":
        cases = [
            ("truck02", experiment["candidates"][selected], 0.02, 1.0),
            ("truck06", experiment["candidates"][selected], 0.06, 1.0),
            ("demand_low", experiment["candidates"][selected], experiment["truck_share"], 0.5),
            ("demand_high", experiment["candidates"][selected], experiment["truck_share"], 1.5),
            ("lane_402377_0_3", experiment["candidates"][selected], experiment["truck_share"], 1.0),
        ]
        dates = [experiment["representative_calibration_date"]]
        seeds = [42]
    else:
        cases = [(selected, experiment["candidates"][selected], experiment["truck_share"], 1.0)]
        dates = experiment[f"{args.phase}_dates"]
        seeds = experiment["seeds"]

    def run_case(case: tuple, day: str, seed: int) -> dict:
        name, parameters, truck_share, demand_scale = case
        directory = root / experiment["output_directory"] / args.phase / name / day / f"seed_{seed}"
        directory.mkdir(parents=True, exist_ok=True)
        config = {
            **base,
            "scenario": f"M3 {args.phase} {name} {day}",
            "observation_dates": [day],
            "human_parameters": parameters,
            "truck_share": truck_share,
            "clearance_seconds": experiment.get("clearance_seconds", base["clearance_seconds"]),
        }
        allocation_case = name if args.phase in {"candidates", "reference"} else selected
        allocation = experiment.get("candidate_entrance_mappings", {}).get(allocation_case)
        if allocation is None and allocation_case.endswith("_split"):
            allocation = experiment["candidate_entrance_mappings"]["tau15_split"]
        config.pop("estimated_entrance_mappings", None)
        config["estimated_ramp_mappings"] = [
            {**mapping, "vehicles_per_hour": mapping["vehicles_per_hour"] * demand_scale}
            for mapping in (
                allocation
                or base.get("estimated_ramp_mappings", base.get("estimated_entrance_mappings", []))
            )
            if demand_scale > 0
        ]
        if name == "lane_402377_0_3":
            config["detector_lane_indices"] = {"402377": [0, 1, 2, 3]}
        config["route_file"] = str(directory / "h0.rou.xml")
        config["manifest_file"] = str(directory / "manifest.json")
        config["aligned_pems_report_file"] = str(directory / "observed.json")
        for key, suffix in [
            ("detector_file_template", "add.xml"),
            ("detector_output_template", "xml"),
            ("detector_summary_template", "json"),
        ]:
            config[key] = str(directory / f"detectors_seed_{{seed}}.{suffix}")
        config["assumptions"] = [
            note for note in config["assumptions"] if "vehicle mix is not calibrated" not in note
        ]
        config["additional_assumptions"] = [
            "Unmeasured net-entry/exit groups use assumed constant flow; "
            "individual ramp counts are unknown.",
            f"{100 * truck_share:g}% truck proxy uses 2024 annual both-direction shares near "
            "SR-237/SR-85; morning directional share is unknown.",
            "One 12 m truck type approximates the heavy fleet; ramp meter timing is unknown.",
        ]
        config_file = directory / "scenario.json"
        config_file.write_text(json.dumps(config, indent=2) + "\n")
        prepared, metrics, detector_file = run_human_baseline(config_file, seed)
        comparison = compare_detector_profiles(
            Path(prepared.aligned_observed_profile_file), detector_file
        )
        health = json.loads((directory / f"h0_run_health_seed_{seed}.json").read_text())
        final = health["final_summary"]
        clean = (
            not health["warning_lines"]
            and all(
                float(final.get(key, 0)) == 0
                for key in ("running", "waiting", "collisions", "teleports", "discarded")
            )
            and float(final["loaded"]) == float(final["inserted"]) == float(final["ended"])
        )
        treatment = {
            "network_sha256": prepared.network_sha256,
            "human_parameters": prepared.human_parameters,
            "vehicle_types": prepared.vehicle_types,
            "truck_share": truck_share,
            "estimated_ramps": config["estimated_ramp_mappings"],
            "detector_lane_indices": config.get("detector_lane_indices", {}),
            "provenance": prepared.provenance,
            "warmup_seconds": config["warmup_seconds"],
            "clearance_seconds": config["clearance_seconds"],
            "mainline_entry_station_id": config["mainline_entry_station_id"],
            "active_ramp_mappings": config["active_ramp_mappings"],
            "checkpoint_edge_ids": config["checkpoint_edge_ids"],
            "step_length_seconds": 0.5,
        }
        treatment_hash = hashlib.sha256(json.dumps(treatment, sort_keys=True).encode()).hexdigest()
        return {
            "case": name,
            "date": day,
            "seed": seed,
            "clean_and_cleared": clean,
            "treatment_sha256": treatment_hash,
            "treatment": treatment,
            "manifest_file": str(Path(prepared.manifest_file).relative_to(root)),
            "metrics": asdict(metrics),
            "health": health,
            "station_comparisons": comparison["station_comparisons"],
            "excluded_lane_mismatch_station_ids": comparison["excluded_lane_mismatch_station_ids"],
        }

    runs = []
    jobs = [(case, day, seed) for case in cases for day in dates for seed in seeds]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_case, *job) for job in jobs]
        for future in as_completed(futures):
            result = future.result()
            runs.append(result)
            print(
                f"{len(runs)}/{len(jobs)} {result['case']} {result['date']} seed {result['seed']} "
                f"clean={result['clean_and_cleared']}",
                flush=True,
            )
    runs.sort(key=lambda run: (run["case"], run["date"], run["seed"]))
    summary = []
    for name, _, _, _ in cases:
        matching = [run for run in runs if run["case"] == name]
        points = [
            point
            for run in matching
            for point in run["station_comparisons"]
            if point["station_id"] not in experiment.get("scoring_excluded_station_ids", [])
        ]
        summary.append(
            {
                "case": name,
                "runs": len(matching),
                "all_clean_and_cleared": all(run["clean_and_cleared"] for run in matching),
                "mean_station_flow_mape_percent": fmean(
                    point["flow_mean_absolute_percentage_error"] for point in points
                ),
                "mean_station_speed_mae_mph": fmean(
                    point["speed_mean_absolute_error_mph"]
                    for point in points
                    if point["speed_mean_absolute_error_mph"] is not None
                ),
            }
        )
    report = {
        "phase": args.phase,
        "dates": dates,
        "seeds": seeds,
        "summary": summary,
        "runs": runs,
        "limitation": "Station means weight each station/date/seed equally. "
        "Trip metrics include warmup and clearance. "
        "Unknown ramp allocation and truck proxy are assumptions.",
    }
    if args.phase == "validation":
        calibration = json.loads(
            (root / experiment["report_directory"] / "calibration_report.json").read_text()
        )
        if {run["treatment_sha256"] for run in runs} != {
            run["treatment_sha256"] for run in calibration["runs"]
        }:
            raise ValueError("Validation treatment differs from the frozen calibration treatment.")
    report_file = root / experiment["report_directory"] / f"{args.phase}_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)
    print(f"Report: {report_file}", flush=True)


if __name__ == "__main__":
    main()
