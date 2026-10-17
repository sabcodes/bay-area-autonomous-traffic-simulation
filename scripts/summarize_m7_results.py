"""Render audited M7 seed spread, activity, failures and OFAT factor effects."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean, stdev

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

METRICS = {
    "network_exit_throughput_vehicles_per_hour": ("All-exit throughput", "veh/h"),
    "scheduled_cohort_mean_total_time_seconds": ("Scheduled-cohort total time", "s"),
    "rms_acceleration_m_per_s2": ("RMS acceleration", "m/s²"),
    "peak_insertion_backlog_vehicles": ("Peak insertion backlog", "vehicles"),
}


def render(report_path, audit_path, output):
    report, audit = json.loads(report_path.read_text()), json.loads(audit_path.read_text())
    assert (
        audit["accepted"]
        and audit["report_sha256"] == hashlib.sha256(report_path.read_bytes()).hexdigest()
    )
    output.mkdir(parents=True, exist_ok=True)
    groups = [g for g in report["groups"] if g["scenario"] != "H0"]
    labels = [f"{g['case']} / {g['scenario']}" for g in groups]
    fig, axes = plt.subplots(2, 2, figsize=(14, 12), layout="constrained")
    for ax, (metric, (title, _)) in zip(axes.flat, METRICS.items(), strict=True):
        for y, group in enumerate(groups):
            stats = group["paired_metrics"][metric]
            color = "#2563eb" if group["scenario"] == "CACC" else "#c75b12"
            if stats["mean"] is None:
                ax.text(0, y, "incomplete - aggregate suppressed", color="#b91c1c", fontsize=8)
                continue
            reference = next(
                g
                for g in report["groups"]
                if g["case"] == group["reference_case"] and g["scenario"] == "H0"
            )
            # Denominator must use the same subset of H0 seeds as the treatment.
            ref_rows = [
                r
                for r in report["runs"]
                if r["case"] == reference["case"]
                and r["scenario"] == "H0"
                and r["seed"] in group["planned_seeds"]
            ]
            reference_mean = mean(r["metrics"][metric] for r in ref_rows)
            scale = 100 / reference_mean if reference_mean else 1
            ax.errorbar(
                stats["mean"] * scale,
                y,
                xerr=stats["sample_standard_deviation"] * scale,
                fmt="o",
                color=color,
                capsize=3,
                markersize=5,
            )
            offsets = np.linspace(-0.12, 0.12, len(stats["pairs"]))
            ax.scatter(
                [p["difference"] * scale for p in stats["pairs"]],
                y + offsets,
                s=17,
                alpha=0.6,
                color=color,
            )
        ax.axvline(0, color="#64748b", linewidth=0.8)
        ax.set_yticks(range(len(labels)), labels, fontsize=8)
        ax.invert_yaxis()
        ax.set_title(title)
        ax.set_xlabel("Treatment − matching-demand H0 (% of paired H0 mean)")
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle(
        "M7 conditional sensitivity: individual seeds and mean ± sample SD\n"
        "Base n=5; sensitivities n=3. Descriptive spread, not confidence intervals.",
        fontsize=14,
    )
    fig.savefig(output / "paired_sensitivity.png", dpi=160)
    plt.close(fig)
    lines = [
        "# M7 sensitivity and uncertainty results",
        "",
        f"Complete campaign: {report['complete']}. "
        f"Valid runs: {sum(r['accepted'] for r in report['runs'])}/{len(report['runs'])}.",
        "",
        "Frozen OFAT screen on 2025-10-08. Base seeds 41-45; sensitivities 41-43.",
        "All differences below pair against H0 at matching demand, date and seed.",
        "Means +/- sample SD describe simulation seed spread, not confidence intervals.",
        "",
        "![Paired sensitivity](paired_sensitivity.png)",
        "",
        "| Case/policy | Metric | Mean difference +/- SD | Min..max | % H0 | +/-/zero seeds |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]

    def fmt(x):
        return "null" if x is None else f"{x:.4f}"

    for group in groups:
        for metric, (title, unit) in METRICS.items():
            s = group["paired_metrics"][metric]
            lines.append(
                f"| {group['case']}/{group['scenario']} | {title} ({unit}) | "
                f"{fmt(s['mean'])} +/- {fmt(s['sample_standard_deviation'])} | "
                f"{fmt(s['minimum'])}..{fmt(s['maximum'])} | "
                f"{fmt(s['percent_of_reference_mean'])} | "
                f"{s['positive_count']}/{s['negative_count']}/{s['zero_count']} |"
            )
    lines += [
        "",
        "## Run validity and activity",
        "",
        "Zero-equipment and nonactivating controls remain valid if healthy and complete.",
        "Active share uses all-run passenger timesteps, including native supervision.",
        "",
        "| Case | Policy | Seed | Valid | Equipped/eligible | Active passenger % | "
        "Message lost/opportunities | VSL lane-s | Warnings | Reason |",
        "| --- | --- | ---: | --- | --- | ---: | --- | ---: | ---: | --- |",
    ]
    for r in report["runs"]:
        d = r.get("controller_diagnostics", {})
        share = (
            100 * d.get("commands", 0) / d["passenger_samples"]
            if d.get("passenger_samples")
            else None
        )
        equipment = (
            f"{d['controlled_vehicles']}/{d['eligible_vehicles']}"
            if "eligible_vehicles" in d
            else "n/a"
        )
        messages = (
            f"{d['messages_lost']}/{d['message_opportunities']}"
            if "message_opportunities" in d
            else "n/a"
        )
        lines.append(
            f"| {r['case']} | {r['scenario']} | {r['seed']} | {r['accepted']} | "
            f"{equipment} | {fmt(share)} | {messages} | {fmt(d.get('limited_lane_seconds'))} | "
            f"{len(r.get('health', {}).get('warning_lines', []))} | {r.get('error', '')} |"
        )
    effects = []
    index = {(r["case"], r["scenario"], r["seed"]): r for r in report["runs"]}
    lines += [
        "",
        "## Factor minus base policy (same seeds)",
        "",
        "These isolate each non-demand factor against the base CACC or CENTRAL "
        "treatment on seeds 41-43.",
        "Demand cases change the operating condition and are interpreted against their own H0.",
        "",
        "| Case/policy | Metric | Factor minus base mean +/- SD |",
        "| --- | --- | ---: |",
    ]
    for group in groups:
        if group["case"] == "base" or group["case"].startswith("demand_"):
            continue
        for metric, (title, _) in METRICS.items():
            pairs = []
            for seed in group["planned_seeds"]:
                after, before = (
                    index[group["case"], group["scenario"], seed],
                    index["base", group["scenario"], seed],
                )
                pairs.append(
                    {
                        "seed": seed,
                        "difference": after["metrics"][metric] - before["metrics"][metric]
                        if after["accepted"] and before["accepted"]
                        else None,
                    }
                )
            complete = all(p["difference"] is not None for p in pairs)
            values = [p["difference"] for p in pairs]
            item = {
                "case": group["case"],
                "scenario": group["scenario"],
                "metric": metric,
                "pairs": pairs,
                "mean": mean(values) if complete else None,
                "sample_standard_deviation": stdev(values) if complete else None,
            }
            effects.append(item)
            lines.append(
                f"| {group['case']}/{group['scenario']} | {title} | "
                f"{fmt(item['mean'])} +/- {fmt(item['sample_standard_deviation'])} |"
            )
    lines += [
        "",
        "## Audit and limitations",
        "",
        f"Independent audit: {audit['raw_metric_checks']} raw metrics; "
        f"{audit['aggregate_and_paired_metric_checks']} group/paired metric records; "
        f"{len(audit['exact_replays'])} exact M6/null-control replays.",
        "",
        "M3 failed held-out fidelity remains (combined speed MAE 14.90 mph). "
        "M5 remains low-engagement supervised control. This single-date OFAT screen "
        "cannot estimate interactions or total uncertainty. Communication degradation "
        "affects acceleration feedforward; current local sensing remains. The range "
        "case also changes sensed-leader following. VSL sensing/actuation remain ideal.",
        "",
        "All-exit throughput is not mainline capacity; stopped counts are queue proxies; "
        "temporal speed variability is not wave stability; acceleration is not energy. "
        "No field safety or deployment inference follows.",
        "",
        "See the closeout and specification in docs/ for acceptance traceability, "
        "commands and interpretation.",
        "",
    ]
    (output / "README.md").write_text("\n".join(lines))
    (output / "factor_effects.json").write_text(json.dumps(effects, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("outputs/us101_corridor/m7/m7_ofat_2025_10_08/report.json"),
    )
    parser.add_argument("--audit", type=Path, default=Path("reports/m7/independent_audit.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/m7"))
    args = parser.parse_args()
    render(args.report, args.audit, args.output)
