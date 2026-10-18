"""Bounded M7 OFAT campaign using the existing isolated experiment harness."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from statistics import fmean, stdev

from bay_area_traffic_sim.cooperative import validate_controller
from bay_area_traffic_sim.experiment_harness import METRIC_CONTRACT, run_experiment
from bay_area_traffic_sim.toy_corridor import repository_root


def distribution(values: list, planned: int) -> dict:
    valid = [x for x in values if type(x) in (int, float) and math.isfinite(x)]
    complete = len(valid) == planned and len(values) == planned
    return {
        "valid_seed_count": len(valid),
        "mean": fmean(valid) if complete else None,
        "sample_standard_deviation": stdev(valid) if complete and planned > 1 else None,
        "minimum": min(valid) if complete else None,
        "maximum": max(valid) if complete else None,
    }


def summarize(config: dict, runs: list[dict]) -> list[dict]:
    index = {(r["case"], r["scenario"], r["seed"]): r for r in runs}
    groups = []
    for case in config["cases"]:
        reference_case = case["id"] if "H0" in case["policies"] else "base"
        for name in case["policies"]:
            seeds = case["seeds"]
            rows = [index.get((case["id"], name, seed), {}) for seed in seeds]
            references = [index.get((reference_case, "H0", seed), {}) for seed in seeds]
            metrics, paired = {}, {}
            for metric in METRIC_CONTRACT:
                values = [
                    r.get("metrics", {}).get(metric) if r.get("accepted") else None for r in rows
                ]
                before = [
                    r.get("metrics", {}).get(metric) if r.get("accepted") else None
                    for r in references
                ]
                delta = [
                    a - b
                    if type(a) in (int, float)
                    and type(b) in (int, float)
                    and math.isfinite(a)
                    and math.isfinite(b)
                    else None
                    for a, b in zip(values, before, strict=True)
                ]
                stats = distribution(delta, len(seeds))
                valid = [x for x in delta if x is not None]
                complete = stats["mean"] is not None
                ref_mean = distribution(before, len(seeds))["mean"]
                paired[metric] = {
                    **stats,
                    "pairs": [
                        {"seed": seed, "difference": x}
                        for seed, x in zip(seeds, delta, strict=True)
                    ],
                    "positive_count": sum(x > 0 for x in valid) if complete else None,
                    "negative_count": sum(x < 0 for x in valid) if complete else None,
                    "zero_count": sum(x == 0 for x in valid) if complete else None,
                    "percent_of_reference_mean": 100 * stats["mean"] / ref_mean
                    if complete and ref_mean
                    else None,
                }
                metrics[metric] = distribution(values, len(seeds))
            groups.append(
                {
                    "case": case["id"],
                    "scenario": name,
                    "planned_seeds": seeds,
                    "reference_case": reference_case,
                    "reference_scenario": "H0",
                    "accepted": all(r.get("accepted", False) for r in rows),
                    "metrics": metrics,
                    "paired_metrics": paired,
                    "failures": [
                        {"seed": seed, "error": r.get("error", "missing run")}
                        for seed, r in zip(seeds, rows, strict=True)
                        if not r.get("accepted")
                    ],
                }
            )
    return groups


def validate_campaign(config: dict, root: Path) -> None:
    def identifier(x):
        return isinstance(x, str) and re.fullmatch(r"[A-Za-z0-9_-]+", x) is not None

    if not identifier(config.get("campaign_id")) or not config.get("cases"):
        raise ValueError("Campaign needs a safe ID and nonempty cases.")
    if type(config.get("workers")) is not int or not 1 <= config["workers"] <= 8:
        raise ValueError("Campaign workers must be from 1 through 8.")
    ids = [c["id"] for c in config["cases"]]
    if not all(identifier(x) for x in ids) or len(ids) != len(set(ids)) or "base" not in ids:
        raise ValueError("Campaign case IDs must be safe, unique and include base.")
    baseline = json.loads((root / config["baseline_config"]).read_text())
    base = next(c for c in config["cases"] if c["id"] == "base")
    if base["demand_scale"] != 1 or set(base["policies"]) != {"H0", "CACC", "CENTRAL"}:
        raise ValueError("Base requires demand 1 and all three policies.")
    for case in config["cases"]:
        if set(case) != {"id", "demand_scale", "seeds", "policies"}:
            raise ValueError("Unexpected case keys.")
        factor, seeds = case["demand_scale"], case["seeds"]
        if type(factor) not in (int, float) or not math.isfinite(factor) or factor <= 0:
            raise ValueError("Campaign demand scale must be finite and positive.")
        if (
            not isinstance(seeds, list)
            or len(seeds) < 2
            or len(set(seeds)) != len(seeds)
            or any(type(s) is not int or not 0 <= s <= 2147483647 for s in seeds)
        ):
            raise ValueError("Campaign seeds must be unique nonnegative integers.")
        if (
            not isinstance(case["policies"], dict)
            or not case["policies"]
            or set(case["policies"]) - {"H0", "CACC", "CENTRAL"}
        ):
            raise ValueError("Unsupported campaign policies.")
        for name, changes in case["policies"].items():
            if not isinstance(changes, dict) or (name == "H0" and changes):
                raise ValueError("Policy overrides must be dictionaries; H0 has none.")
            if name != "H0":
                validate_controller(
                    {**config["controllers"][name], **changes}, baseline["human_parameters"]
                )
        if "H0" not in case["policies"] and (factor != 1 or not set(seeds) <= set(base["seeds"])):
            raise ValueError("Treatment must have matching-demand H0 for every seed.")


def run_campaign(config_path: Path) -> dict:
    root = repository_root()
    config = json.loads((root / config_path).read_text())
    validate_campaign(config, root)
    output = root / "outputs/us101_corridor/m7" / config["campaign_id"]
    output.mkdir(parents=True, exist_ok=False)
    (output / "campaign.json").write_text(json.dumps(config, indent=2) + "\n")
    baseline = json.loads((root / config["baseline_config"]).read_text())
    runs, reports = [], []
    for case in config["cases"]:
        base_path = output / f"{case['id']}_baseline.json"
        base_path.write_text(
            json.dumps({**baseline, "demand_scale": case["demand_scale"]}, indent=2) + "\n"
        )
        experiment = {
            "experiment_id": case["id"],
            "allow_inactive_controllers": True,
            "scenarios": [
                {
                    "id": name,
                    "baseline_config": str(base_path.relative_to(root)),
                    **(
                        {"controller": {**config["controllers"][name], **changes}}
                        if name != "H0"
                        else {}
                    ),
                }
                for name, changes in case["policies"].items()
            ],
            "observation_dates": ["2025-10-08"],
            "seeds": case["seeds"],
            "measurement": {"period_seconds": 1.0, "stop_speed_m_per_s": 0.1},
            "output_directory": str(output.relative_to(root)),
            "workers": config["workers"],
        }
        if "H0" in case["policies"]:
            experiment["reference_scenario"] = "H0"
        path = output / f"{case['id']}_experiment.json"
        path.write_text(json.dumps(experiment, indent=2) + "\n")
        report = run_experiment(path)
        reports.append(report["report_file"])
        runs.extend(
            {**r, "case": case["id"], "demand_scale": case["demand_scale"]} for r in report["runs"]
        )
        result = {
            "campaign": config,
            "campaign_config_sha256": hashlib.sha256((root / config_path).read_bytes()).hexdigest(),
            "completed_cases": len(reports),
            "complete": len(reports) == len(config["cases"]),
            "all_runs_accepted": all(r["accepted"] for r in runs),
            "runs": runs,
            "groups": summarize(config, runs),
            "experiment_reports": reports,
        }
        (output / "report.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
