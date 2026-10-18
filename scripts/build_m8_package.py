"""Build/check the final research package from frozen, audited saved evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
METRICS = {
    "network_exit_throughput_vehicles_per_hour": "Throughput (veh/h)",
    "scheduled_cohort_mean_total_time_seconds": "Scheduled total time (s)",
    "rms_acceleration_m_per_s2": "RMS acceleration (m/s^2)",
    "peak_insertion_backlog_vehicles": "Peak insertion backlog (vehicles)",
}
SCORES = {
    "flow_mean_absolute_percentage_error": "mean_station_flow_mape_percent",
    "speed_mean_absolute_error_mph": "mean_station_speed_mae_mph",
}
CALIBRATION_DATES = ["2025-10-07", "2025-10-08", "2025-10-09", "2025-10-10", "2025-10-14"]
VALIDATION_DATES = ["2025-10-15", "2025-10-16"]
STATIONS = {401507, 401534, 401996, 401998, 402370, 402372}
OUTPUTS = ("reports/m8/headline_results.json", "reports/m8/results.md")
EXCLUDED = {"reports/m8/manifest.json", "reports/m8/verification.json"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(root, path):
    return json.loads((root / path).read_text())


def finite(value):
    require(type(value) in (int, float) and math.isfinite(value), f"Nonfinite metric: {value!r}")
    return value


def same(actual, expected):
    require(
        math.isclose(finite(actual), finite(expected), rel_tol=1e-10, abs_tol=1e-10),
        f"Statistic mismatch: {actual} != {expected}",
    )


def headline_results(root):
    report = read(root, "reports/m7/report.json")
    audit = read(root, "reports/m7/independent_audit.json")
    config = read(root, "configs/us101_m7_sensitivity.json")
    require(audit["accepted"] is True and report["complete"] is True, "Unaccepted M7 evidence")
    require(report["all_runs_accepted"] is True, "Rejected M7 outcome")
    require(audit["report_sha256"] == sha(root / "reports/m7/report.json"), "Audit/report mismatch")
    require(report["campaign"] == config, "Campaign/config mismatch")
    config_sha = sha(root / "configs/us101_m7_sensitivity.json")
    require(
        config_sha == audit["campaign_config_sha256"] == report["campaign_config_sha256"],
        "Campaign hash mismatch",
    )
    for path, digest in audit["source_sha256"].items():
        require(sha(root / path) == digest, f"Frozen simulator changed: {path}")
    expected = {
        (c["id"], policy, seed)
        for c in config["cases"]
        for policy in c["policies"]
        for seed in c["seeds"]
    }
    runs = report["runs"]
    index = {(r["case"], r["scenario"], r["seed"]): r for r in runs}
    require(
        len(runs) == len(index) == len(expected) == 54 and set(index) == expected,
        "Missing, duplicate or extra M7 outcome",
    )
    require(
        all(r["accepted"] is True and r["date"] == "2025-10-08" for r in runs),
        "Rejected run or wrong date",
    )
    groups = {(g["case"], g["scenario"]): g for g in report["groups"]}
    expected_groups = {(c["id"], p) for c in config["cases"] for p in c["policies"]}
    require(
        len(groups) == len(report["groups"]) and set(groups) == expected_groups,
        "Missing, duplicate or extra M7 group",
    )
    records = []
    for case in config["cases"]:
        reference = case["id"] if "H0" in case["policies"] else "base"
        for policy in case["policies"]:
            if policy == "H0":
                continue
            group = groups[case["id"], policy]
            require(
                group["accepted"] is True
                and group["planned_seeds"] == case["seeds"]
                and group["reference_case"] == reference,
                "Wrong group population/reference",
            )
            for metric in METRICS:
                before = [
                    finite(index[reference, "H0", s]["metrics"][metric]) for s in case["seeds"]
                ]
                after = [
                    finite(index[case["id"], policy, s]["metrics"][metric]) for s in case["seeds"]
                ]
                delta = [finite(a - b) for a, b in zip(after, before, strict=True)]
                denominator = finite(mean(before))
                require(denominator > 0, "Nonpositive H0 denominator")
                stats = {
                    "valid_seed_count": len(delta),
                    "mean": finite(mean(delta)),
                    "sample_standard_deviation": finite(stdev(delta)),
                    "minimum": min(delta),
                    "maximum": max(delta),
                    "positive_count": sum(d > 0 for d in delta),
                    "negative_count": sum(d < 0 for d in delta),
                    "zero_count": delta.count(0),
                    "percent_of_reference_mean": finite(100 * mean(delta) / denominator),
                }
                saved = group["paired_metrics"][metric]
                for key, value in stats.items():
                    same(value, saved[key])
                pairs = [
                    {"seed": s, "difference": d} for s, d in zip(case["seeds"], delta, strict=True)
                ]
                require(saved["pairs"] == pairs, "Individual paired values mismatch")
                records.append(
                    {
                        "case": case["id"],
                        "scenario": policy,
                        "metric": metric,
                        "reference_case": reference,
                        "h0_mean": denominator,
                        "pairs": pairs,
                        **stats,
                    }
                )
    baseline = []
    treatment = read(root, "reports/m3/freeze.json")["treatment_sha256"]
    for phase, dates in (("calibration", CALIBRATION_DATES), ("validation", VALIDATION_DATES)):
        data = read(root, f"reports/m3/{phase}_report.json")
        rows = data["runs"]
        keys = {(r["date"], r["seed"]) for r in rows}
        require(
            len(rows) == len(keys) and keys == {(d, s) for d in dates for s in (41, 42, 43)},
            f"Wrong M3 {phase} population",
        )
        require(
            all(
                r["clean_and_cleared"] is True and r["treatment_sha256"] == treatment for r in rows
            ),
            "Unclean or changed M3 treatment",
        )
        values = {}
        for row in rows:
            stations = [s for s in row["station_comparisons"] if s["station_id"] in STATIONS]
            require(
                len(stations) == 6 and {s["station_id"] for s in stations} == STATIONS,
                "Missing/duplicate M3 scoring station",
            )
            values[row["date"], row["seed"]] = {
                target: mean(finite(s[source]) for s in stations)
                for source, target in SCORES.items()
            }
        for target in SCORES.values():
            same(mean(v[target] for v in values.values()), data["summary"][0][target])
        for date in [*dates, "combined"]:
            selected = [v for (d, _), v in values.items() if date == "combined" or d == date]
            baseline.append(
                {
                    "phase": phase,
                    "date": date,
                    "runs": len(selected),
                    **{t: mean(v[t] for v in selected) for t in SCORES.values()},
                }
            )
    require(len(records) == 52, "Wrong headline record count")
    return {
        "schema_version": 1,
        "m3_scores": baseline,
        "m7_paired_metrics": records,
        "scope": "Saved-evidence packaging check; no fresh raw-trajectory audit or simulation.",
    }


def markdown(data):
    lines = [
        "# Final research result tables",
        "",
        "Generated from saved per-run evidence. "
        "Differences are policy minus matching-demand, matching-seed H0. "
        "SD is sample seed spread, not a confidence interval.",
        "",
        "## M3 fidelity",
        "",
        "| Phase / date | Runs | Flow MAPE (%) | Speed MAE (mph) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for r in data["m3_scores"]:
        lines.append(
            f"| {r['phase']} / {r['date']} | {r['runs']} | "
            f"{r['mean_station_flow_mape_percent']:.2f} | "
            f"{r['mean_station_speed_mae_mph']:.2f} |"
        )
    lines += [
        "",
        "## M7 paired effects",
        "",
        "All 13 comparisons and four headline metrics. "
        "Percent = 100 * mean paired difference / mean of the exact H0 seed subset.",
        "",
        "| Case / policy | Metric | n | Difference +/- SD | Range | % of H0 | + / - / 0 |",
        "| --- | --- | ---: | ---: | --- | ---: | --- |",
    ]
    for r in data["m7_paired_metrics"]:
        lines.append(
            f"| {r['case']} / {r['scenario']} | {METRICS[r['metric']]} | "
            f"{r['valid_seed_count']} | {r['mean']:.4f} +/- "
            f"{r['sample_standard_deviation']:.4f} | "
            f"{r['minimum']:.4f}..{r['maximum']:.4f} | "
            f"{r['percent_of_reference_mean']:+.4f} | "
            f"{r['positive_count']}/{r['negative_count']}/{r['zero_count']} |"
        )
    return "\n".join(lines) + "\n"


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def package(root, check=False):
    data = headline_results(root)  # Validate everything before writing any output.
    generated = {OUTPUTS[0]: encoded(data), OUTPUTS[1]: markdown(data).encode()}
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    prefixes = (
        "docs/",
        "research/",
        "configs/",
        "src/",
        "scripts/",
        "tests/",
        "network/",
        "reports/m3/",
        "reports/m4/",
        "reports/m5/",
        "reports/m6/",
        "reports/m7/",
    )
    paths = {
        p
        for p in tracked
        if p
        and (
            p.startswith(prefixes)
            or p in {"README.md", "CONTEXT.md", "pyproject.toml", ".gitignore"}
        )
    }
    paths.update(OUTPUTS)
    manifest = {
        p: hashlib.sha256(generated[p]).hexdigest() if p in generated else sha(root / p)
        for p in sorted(paths - EXCLUDED)
    }
    generated["reports/m8/manifest.json"] = encoded({"schema_version": 1, "sha256": manifest})
    if check:
        for path, content in generated.items():
            require((root / path).read_bytes() == content, f"Stale package artifact: {path}")
    else:
        (root / "reports/m8").mkdir(parents=True, exist_ok=True)
        for path, content in generated.items():
            (root / path).write_bytes(content)
    return len(manifest)


def local_inputs(root):
    expected = read(root, "configs/us101_human_baseline_m3_frozen.json")["expected_input_sha256"]
    errors = []
    for path, digest in expected.items():
        if not (root / path).is_file():
            errors.append(f"Missing: {path}")
        elif sha(root / path) != digest:
            errors.append(f"Hash mismatch: {path}")
    require(not errors, "\n".join(errors))
    return len(expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without writing")
    parser.add_argument(
        "--check-local-inputs",
        action="store_true",
        help="Check frozen runtime input hashes only; no simulation",
    )
    args = parser.parse_args()
    try:
        if args.check_local_inputs:
            print(f"Local prerequisites: {local_inputs(ROOT)} matching input hashes")
        else:
            print(
                f"M8 package {'verified' if args.check else 'built'}: {package(ROOT, args.check)} "
                "content hashes, 52 paired records and M3 station-score recalculation"
            )
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, f"M8 verification failed: {error}\n")
