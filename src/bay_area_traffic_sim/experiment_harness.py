"""Explicit, isolated multi-seed experiments for the audited real corridor."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from statistics import fmean, stdev

from bay_area_traffic_sim.cooperative import validate_controller
from bay_area_traffic_sim.experiment_metrics import (
    clean_and_cleared,
    entrance_queue_edges,
    read_insertion_metrics,
    read_trajectory_metrics,
    read_window_trip_metrics,
)
from bay_area_traffic_sim.real_corridor import _load_baseline_config, run_human_baseline
from bay_area_traffic_sim.toy_corridor import repository_root

LIMITATIONS = [
    "M3 held-out fidelity remains limited: October 15 missed both flow and speed targets; "
    "combined held-out speed MAE was 14.90 mph. M4 instrumentation does not revalidate H0.",
    "Seed spread describes stochastic simulation variation, not total model uncertainty.",
    "Trajectory scope includes modeled ramps, upstream buffer, and internal junction links.",
    "Queues are stopped-vehicle count proxies, not contiguous queue lengths in meters. "
    "Entrance counts omit internal junction links and vehicles waiting to insert.",
    "Temporal variability of domain mean speed depends on demand and spatial composition; "
    "it does not establish wave stability or disturbance recovery.",
    "Acceleration squared is a smoothness proxy, not energy or fuel use. "
    "FCD speed and acceleration use SUMO's default two-decimal output precision.",
    "CACC is a conservative passenger overlay with ideal acceleration messages and native "
    "Krauss safety constraints; 1.5 s headway is retained. Trucks are human driven. "
    "Policy comparisons do not establish real-world safety or string stability.",
    "Unknown gross ramp movements and the annual truck proxy remain M3 assumptions.",
]
METRIC_CONTRACT = {
    "window_exit_vehicles": ["vehicles", "arrivals in window, all modeled exits"],
    "network_exit_throughput_vehicles_per_hour": ["veh/h", "window arrivals / window hours"],
    "cohort_completed_vehicles": ["vehicles", "window departures completed by run end"],
    "cohort_unfinished_vehicles": ["vehicles", "window departures unfinished at run end"],
    "cohort_mean_travel_time_seconds": ["s", "completed departure cohort, arithmetic mean"],
    "cohort_p95_travel_time_seconds": ["s", "completed departure cohort, linear p95"],
    "cohort_mean_waiting_time_seconds": ["s", "completed departure cohort, mean waitingTime"],
    "cohort_mean_time_loss_seconds": ["s", "completed departure cohort, mean SUMO timeLoss"],
    "trajectory_timesteps": ["samples", "all expected window timesteps including empty"],
    "populated_timesteps": ["samples", "window timesteps with vehicles"],
    "vehicle_samples": ["samples", "all vehicle observations in window"],
    "mean_stopped_vehicles": ["vehicles", "time mean, speed < stop threshold"],
    "peak_stopped_vehicles": ["vehicles", "time maximum, speed < stop threshold"],
    "stopped_vehicle_seconds": ["vehicle s", "sum stopped counts times sample period"],
    "mean_ramp_stopped_vehicles": ["vehicles", "time mean on entrance approach edges"],
    "peak_ramp_stopped_vehicles": ["vehicles", "time maximum on entrance approach edges"],
    "mean_timestep_speed_mph": ["mph", "mean of nonempty timestep mean speeds"],
    "temporal_mean_speed_stddev_mph": ["mph", "population stddev of timestep mean speeds"],
    "mean_squared_acceleration_m2_per_s4": ["m^2/s^4", "mean a squared over vehicle samples"],
    "rms_acceleration_m_per_s2": ["m/s^2", "square root of mean squared acceleration"],
    "window_actual_departures": ["vehicles", "actual departures in window"],
    "unreconstructed_scheduled_departures": ["vehicles", "trips lacking reconstructable schedule"],
    "scheduled_cohort_vehicles": ["vehicles", "scheduled departures in window"],
    "scheduled_cohort_completed_vehicles": ["vehicles", "completed scheduled-window cohort"],
    "scheduled_cohort_mean_depart_delay_seconds": ["s", "scheduled-window cohort insertion delay"],
    "scheduled_cohort_mean_total_time_seconds": [
        "s",
        "completed scheduled cohort duration + delay",
    ],
    "whole_run_mean_depart_delay_seconds": ["s", "all inserted trips mean insertion delay"],
    "whole_run_max_depart_delay_seconds": ["s", "all inserted trips maximum insertion delay"],
    "peak_insertion_backlog_vehicles": ["vehicles", "maximum waiting to insert, whole run"],
    "window_peak_insertion_backlog_vehicles": ["vehicles", "maximum waiting to insert in window"],
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def validate_experiment(config: dict, root: Path) -> tuple[Path, dict[str, dict]]:
    """Reject invalid matrices and incompatible comparisons before launching SUMO."""

    def identifier(value: object) -> bool:
        return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]+", value) is not None

    if not identifier(config.get("experiment_id")):
        raise ValueError("experiment_id must contain only letters, digits, underscores or dashes.")
    workers = config.get("workers", 1)
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError("workers must be an integer from 1 through 8.")
    scenarios = config.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("Declare at least one named scenario.")
    ids = [scenario.get("id") for scenario in scenarios]
    if not all(identifier(name) for name in ids) or len(set(ids)) != len(ids):
        raise ValueError("Scenario IDs must be safe and unique.")
    dates = config.get("observation_dates")
    if not isinstance(dates, list) or not dates:
        raise ValueError("Declare at least one observation date.")
    if any(not isinstance(day, str) or date.fromisoformat(day).isoformat() != day for day in dates):
        raise ValueError("Observation dates must be ISO dates.")
    if len(dates) != len(set(dates)):
        raise ValueError("Observation dates must be unique.")
    seeds = config.get("seeds")
    if (
        not isinstance(seeds, list)
        or len(seeds) < 2
        or any(type(seed) is not int or not 0 <= seed <= 2147483647 for seed in seeds)
        or len(seeds) != len(set(seeds))
    ):
        raise ValueError("Declare at least two unique nonnegative integer SUMO seeds.")
    measurement = config.get("measurement", {})
    period = measurement.get("period_seconds")
    threshold = measurement.get("stop_speed_m_per_s")
    if (
        type(period) not in (int, float)
        or not math.isfinite(period)
        or period <= 0
        or not math.isclose(period / 0.5, round(period / 0.5))
    ):
        raise ValueError("Sampling period must be a positive multiple of the 0.5 s step.")
    if type(threshold) not in (int, float) or not math.isfinite(threshold) or threshold < 0:
        raise ValueError("Stop threshold must be finite and nonnegative.")
    output = (root / config["output_directory"] / config["experiment_id"]).resolve()
    if not output.is_relative_to((root / "outputs").resolve()) or output.exists():
        raise ValueError(
            "Use a new experiment directory under outputs/; existing runs are preserved."
        )
    bases = {
        scenario["id"]: _load_baseline_config(Path(scenario["baseline_config"]), root)
        for scenario in scenarios
    }
    reference = config.get("reference_scenario")
    if reference is not None and reference not in ids:
        raise ValueError("Reference scenario must identify a declared scenario.")
    controlled = any("controller" in scenario for scenario in scenarios)
    for scenario in scenarios:
        if "controller" in scenario:
            validate_controller(scenario["controller"], bases[scenario["id"]]["human_parameters"])
    # Compare all input settings except labels, output locations, and driver parameters.
    ignored = {
        "scenario",
        "assumptions",
        "additional_assumptions",
        "freeze_note",
        "human_parameters",
        "route_file",
        "manifest_file",
        "aligned_pems_report_file",
        "detector_file_template",
        "detector_output_template",
        "detector_summary_template",
    }
    if controlled:
        ignored.remove("human_parameters")
    comparison = None
    for base in bases.values():
        comparable = {key: value for key, value in base.items() if key not in ignored}
        if comparison is not None and comparable != comparison:
            raise ValueError(
                "Scenarios differ in network, demand, fleet, windows, or data settings."
            )
        comparison = comparable
    return output, bases


def summarize_seed_metrics(runs: list[dict]) -> dict:
    """Require every planned run for each mean; retain numeric seed counts."""
    summary = {}
    accepted = all(run["accepted"] for run in runs)
    for name in METRIC_CONTRACT:
        values = [run.get("metrics", {}).get(name) for run in runs]
        numeric = [value for value in values if value is not None]
        complete = accepted and len(numeric) == len(runs)
        summary[name] = {
            "valid_seed_count": len(numeric),
            "mean": fmean(numeric) if complete else None,
            "sample_standard_deviation": stdev(numeric) if complete and len(numeric) > 1 else None,
        }
    return summary


def _markdown(report: dict) -> str:
    lines = [
        f"# {report['experiment']['experiment_id']}",
        "",
        f"Accepted: {report['accepted']}. Seeds: {report['experiment']['seeds']}.",
        "",
        "Means and sample standard deviations are across seeds within each scenario/date.",
        "",
        "| Scenario | Date | Metric | Mean | Sample SD | Valid seeds |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for group in report["groups"]:
        for metric, stats in group["metric_summary"].items():
            mean, spread = stats["mean"], stats["sample_standard_deviation"]
            lines.append(
                f"| {group['scenario']} | {group['date']} | {metric} | "
                f"{mean if mean is None else round(mean, 6)} | "
                f"{spread if spread is None else round(spread, 6)} | {stats['valid_seed_count']} |"
            )
    if "paired_comparisons" in report:
        lines += [
            "",
            "## Paired treatment minus reference",
            "",
            "| Treatment | Date | Metric | Mean difference | Sample SD | Percent of H0 |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
        for comparison in report["paired_comparisons"]:
            for metric, stats in comparison["metrics"].items():
                lines.append(
                    f"| {comparison['treatment']} | {comparison['date']} | {metric} | "
                    f"{stats['mean_difference']} | {stats['sample_standard_deviation']} | "
                    f"{stats['percent_of_reference_mean']} |"
                )
    lines += ["", "## Runs", ""]
    for run in report["runs"]:
        lines.append(
            f"- {run['scenario']} {run['date']} seed {run['seed']}: "
            f"accepted={run['accepted']}; {run.get('error', 'measured')}."
        )
    lines += ["", "## Metric contract", ""]
    for name, (unit, population) in METRIC_CONTRACT.items():
        lines.append(f"- `{name}` ({unit}): {population}.")
    lines += ["", "## Limitations", "", *[f"- {note}" for note in LIMITATIONS]]
    return "\n".join(lines) + "\n"


def paired_comparisons(report: dict) -> list[dict]:
    """Pair by scenario/date/seed; never reduce the planned seed population silently."""
    config = report["experiment"]
    reference = config["reference_scenario"]
    index = {(run["scenario"], run["date"], run["seed"]): run for run in report["runs"]}
    comparisons = []
    for treatment in sorted(item["id"] for item in config["scenarios"] if item["id"] != reference):
        for day in sorted(config["observation_dates"]):
            metrics = {}
            for metric in METRIC_CONTRACT:
                pairs, references = [], []
                for seed in sorted(config["seeds"]):
                    baseline = index.get((reference, day, seed), {})
                    changed = index.get((treatment, day, seed), {})
                    before = baseline.get("metrics", {}).get(metric)
                    after = changed.get("metrics", {}).get(metric)
                    valid = (
                        baseline.get("accepted")
                        and changed.get("accepted")
                        and before is not None
                        and after is not None
                    )
                    pairs.append({"seed": seed, "difference": after - before if valid else None})
                    if valid:
                        references.append(before)
                differences = [
                    pair["difference"] for pair in pairs if pair["difference"] is not None
                ]
                complete = len(differences) == len(config["seeds"])
                mean = fmean(differences) if complete else None
                reference_mean = fmean(references) if complete else None
                metrics[metric] = {
                    "pairs": pairs,
                    "mean_difference": mean,
                    "sample_standard_deviation": stdev(differences) if complete else None,
                    "percent_of_reference_mean": (
                        100 * mean / reference_mean if reference_mean else None
                    ),
                }
            comparisons.append(
                {"reference": reference, "treatment": treatment, "date": day, "metrics": metrics}
            )
    return comparisons


def _run_job(job: tuple) -> dict:
    """Run one isolated matrix job; safe for separate libsumo worker processes."""
    root, config, output, name, base, day, seed = job
    period = config["measurement"]["period_seconds"]
    threshold = config["measurement"]["stop_speed_m_per_s"]
    directory = output / name / day / f"seed_{seed}"
    directory.mkdir(parents=True)
    run = {
        "scenario": name,
        "date": day,
        "seed": seed,
        "accepted": False,
        "directory": str(directory.relative_to(root)),
    }
    try:
        scenario = {
            **base,
            "scenario": f"{config['experiment_id']} {name} {day}",
            "observation_dates": [day],
            "route_file": str(directory / "h0.rou.xml"),
            "manifest_file": str(directory / "manifest.json"),
            "aligned_pems_report_file": str(directory / "observed.json"),
            "detector_file_template": str(directory / "detectors_seed_{seed}.add.xml"),
            "detector_output_template": str(directory / "detectors_seed_{seed}.xml"),
            "detector_summary_template": str(directory / "detectors_seed_{seed}.json"),
        }
        policy = next(item.get("controller") for item in config["scenarios"] if item["id"] == name)
        if policy is not None:
            scenario["controller"] = policy
        scenario_file = directory / "scenario.json"
        scenario_file.write_text(json.dumps(scenario, indent=2) + "\n")
        trajectory = directory / "trajectory.fcd.xml.gz"
        prepared, legacy_metrics, detector_file = run_human_baseline(
            scenario_file,
            seed,
            trajectory_output=trajectory,
            trajectory_period_seconds=period,
            **({"controller": policy} if policy is not None else {}),
        )
        health = json.loads((directory / f"h0_run_health_seed_{seed}.json").read_text())
        run["health"] = health
        begin = float(base["warmup_seconds"])
        end = float(prepared.demand_profile[-1].end_seconds)
        trip_file = directory / f"h0_human_baseline_seed_{seed}.tripinfo.xml"
        ramp_edges = entrance_queue_edges(Path(prepared.route_file))
        run.update(
            {
                "measurement": {
                    "begin_seconds": begin,
                    "end_seconds_exclusive": end,
                    **config["measurement"],
                    "ramp_approach_edge_ids": sorted(ramp_edges),
                },
                "resolved_scenario_sha256": _json_hash(scenario),
                "route_sha256": _sha256(Path(prepared.route_file)),
                "network_sha256": prepared.network_sha256,
                "provenance": prepared.provenance,
                "manifest_file": str(Path(prepared.manifest_file).relative_to(root)),
                "detector_summary_file": str(detector_file.relative_to(root)),
                "legacy_whole_run_metrics": asdict(legacy_metrics),
                "metrics": {
                    **read_window_trip_metrics(trip_file, begin, end),
                    **read_insertion_metrics(
                        trip_file, directory / f"h0_summary_seed_{seed}.xml", begin, end
                    ),
                    **read_trajectory_metrics(
                        trajectory,
                        begin,
                        end,
                        period,
                        threshold,
                        ramp_edges,
                    ),
                },
                "accepted": clean_and_cleared(health),
            }
        )
        run["controller"] = policy
        if policy is not None:
            diagnostics_file = directory / "controller_diagnostics.json"
            diagnostics = json.loads(diagnostics_file.read_text())
            run["controller_diagnostics"] = diagnostics
            run["accepted"] = run["accepted"] and (
                diagnostics["completed"]
                and diagnostics["commands"] > 0
                and diagnostics["cooperative_commands"] > 0
                and diagnostics["native_fallbacks"] == 0
                and diagnostics["engine_version"].split()[-1]
                == prepared.provenance["sumo_version"].split()[-1]
            )
        if not run["accepted"]:
            run["error"] = "Run health failed the clean-and-cleared requirement."
    except Exception as error:
        run["accepted"] = False
        run["error"] = f"{type(error).__name__}: {error}"
        for filename, key in [
            (f"h0_run_health_seed_{seed}.json", "health"),
            ("controller_diagnostics.json", "controller_diagnostics"),
        ]:
            evidence = directory / filename
            if evidence.exists():
                run[key] = json.loads(evidence.read_text())
    (directory / "result.json").write_text(json.dumps(run, indent=2) + "\n")
    print(
        f"{name} {day} seed {seed}: accepted={run['accepted']} {run.get('error', '')}",
        flush=True,
    )
    return run


def run_experiment(config_path: Path) -> dict:
    """Execute a declared matrix, retain failures, and write JSON/Markdown reports."""
    root = repository_root()
    config_path = root / config_path
    config = json.loads(config_path.read_text())
    output, bases = validate_experiment(config, root)
    output.mkdir(parents=True, exist_ok=False)
    (output / "experiment.json").write_text(json.dumps(config, indent=2) + "\n")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    source_hashes = {
        str(path.relative_to(root)): _sha256(path)
        for path in sorted((root / "src/bay_area_traffic_sim").glob("*.py"))
    }
    jobs = [
        (root, config, output, name, base, day, seed)
        for name, base in bases.items()
        for day in sorted(config["observation_dates"])
        for seed in sorted(config["seeds"])
    ]
    workers = config.get("workers", 1)
    if workers == 1:
        runs = [_run_job(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            runs = list(executor.map(_run_job, jobs))
    runs.sort(key=lambda run: (run["scenario"], run["date"], run["seed"]))
    groups = []
    for name in sorted(bases):
        for day in sorted(config["observation_dates"]):
            matching = [run for run in runs if run["scenario"] == name and run["date"] == day]
            groups.append(
                {
                    "scenario": name,
                    "date": day,
                    "planned_seeds": sorted(config["seeds"]),
                    "accepted": all(run["accepted"] for run in matching),
                    "metric_summary": summarize_seed_metrics(matching),
                }
            )
    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "accepted": all(run["accepted"] for run in runs),
        "experiment": config,
        "experiment_config_sha256": _sha256(config_path),
        "source_revision": revision.stdout.strip() if revision.returncode == 0 else None,
        "source_sha256": source_hashes,
        "resolved_baseline_configs": bases,
        "resolved_baseline_sha256": {name: _json_hash(base) for name, base in bases.items()},
        "metric_contract": METRIC_CONTRACT,
        "limitations": LIMITATIONS,
        "groups": groups,
        "runs": runs,
        "report_file": str((output / "report.json").relative_to(root)),
    }
    if config.get("reference_scenario") is not None:
        report["paired_comparisons"] = paired_comparisons(report)
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (output / "summary.md").write_text(_markdown(report))
    print(f"Report: {output / 'report.json'}", flush=True)
    return report
