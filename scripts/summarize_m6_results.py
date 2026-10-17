"""Write an accepted three-policy comparison table and standalone result figure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

METRICS = [
    ("network_exit_throughput_vehicles_per_hour", "Network exit throughput", "veh/h"),
    ("cohort_mean_travel_time_seconds", "Actual-departure mean travel time", "s"),
    ("cohort_p95_travel_time_seconds", "Actual-departure p95 travel time", "s"),
    ("scheduled_cohort_mean_total_time_seconds", "Scheduled-cohort total time", "s"),
    ("whole_run_mean_depart_delay_seconds", "Whole-run insertion delay", "s"),
    ("peak_insertion_backlog_vehicles", "Peak insertion backlog", "vehicles"),
    ("mean_stopped_vehicles", "Mean stopped proxy", "vehicles"),
    ("mean_ramp_stopped_vehicles", "Entrance-approach stopped proxy", "vehicles"),
    ("temporal_mean_speed_stddev_mph", "Temporal mean-speed variability", "mph"),
    ("mean_squared_acceleration_m2_per_s4", "Mean squared acceleration", "m²/s⁴"),
    ("rms_acceleration_m_per_s2", "RMS acceleration", "m/s²"),
]


def summarize(report_path, audit_path, output):
    report, audit = json.loads(report_path.read_text()), json.loads(audit_path.read_text())
    if not report["accepted"] or not audit["accepted"]:
        raise ValueError("Refuse performance presentation from a rejected matrix or audit.")
    groups = {g["scenario"]: g["metric_summary"] for g in report["groups"]}
    lines = [
        "# M6 centralized VSL results",
        "",
        "Means ± sample SD across seeds 41–43 on October 8, 2025. "
        "Seed spread is not a confidence interval.",
        "",
        "| Metric | Unit | H0 | Supervised CACC | CENTRAL |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for key, label, unit in METRICS:
        cells = [
            f"{groups[s][key]['mean']:.4f} ± {groups[s][key]['sample_standard_deviation']:.4f}"
            for s in ["H0", "CACC", "CENTRAL"]
        ]
        lines.append("| " + " | ".join([label, unit, *cells]) + " |")
    lines += [
        "",
        "## Paired differences",
        "",
        "Treatment minus reference, with sample SD of seed differences.",
        "",
        "| Metric | CACC − H0 | CENTRAL − H0 | CENTRAL − CACC |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key, label, _ in METRICS:
        cells = []
        for comparison in audit["paired_comparisons"]:
            stats = comparison["metrics"][key]
            percent = stats["percent_of_reference_mean"]
            cells.append(
                f"{stats['mean_difference']:+.4f} ± "
                f"{stats['sample_standard_deviation']:.4f} ({percent:+.2f}%)"
            )
        lines.append("| " + " | ".join([label, *cells]) + " |")
    lines += [
        "",
        "## Central actuation",
        "",
        "| Seed | Congested decisions | Changed-lane commands | Limited-lane seconds |",
        "| --- | ---: | ---: | ---: |",
    ]
    for run in audit["runs"]:
        if run["scenario"] == "CENTRAL":
            d = run["policy"]
            lines.append(
                f"| {run['seed']} | {d['congested_decisions']} | "
                f"{d['lane_commands']} | {d['limited_lane_seconds']:.0f} |"
            )
    lines += [
        "",
        "Limited-lane seconds measure reduced-limit exposure, not vehicle compliance. "
        "The nonactivating 3000 s preflight is preserved separately. "
        "M3 held-out fidelity and M5 approximately 2% CACC engagement remain limitations.",
        "",
        "[Closeout and reproduction](../../docs/m6-centralized-control-report.md) · "
        "[Frozen specification](../../docs/m6-centralized-control-spec.md) · "
        "[Report](report.json) · [Independent audit](independent_audit.json) · "
        "[Preflight](preflight_seed41.json)",
        "",
        "![Three-policy seed results](comparison.png)",
        "",
    ]
    output.mkdir(parents=True, exist_ok=True)
    (output / "README.md").write_text("\n".join(lines))
    figure, axes = plt.subplots(3, 2, figsize=(11, 10), layout="constrained")
    for ax, (key, label, unit) in zip(
        axes.flat, [METRICS[i] for i in [0, 3, 4, 5, 6, 10]], strict=True
    ):
        for x, (name, color) in enumerate(
            [("H0", "#555555"), ("CACC", "#2878b5"), ("CENTRAL", "#ba5a22")]
        ):
            values = [r["metrics"][key] for r in report["runs"] if r["scenario"] == name]
            ax.scatter([x - 0.07, x, x + 0.07], values, color=color, s=25, alpha=0.7)
            stats = groups[name][key]
            ax.errorbar(
                x,
                stats["mean"],
                yerr=stats["sample_standard_deviation"],
                fmt="D",
                color=color,
                capsize=5,
                markersize=6,
            )
        ax.set_xticks([0, 1, 2], ["H0", "CACC", "CENTRAL"])
        ax.set_ylabel(unit)
        ax.set_title(label)
        ax.grid(axis="y", alpha=0.2)
        ax.spines[["top", "right"]].set_visible(False)
    figure.suptitle("M6: centralized VSL, supervised CACC and human baseline", fontsize=15)
    figure.supxlabel(
        "Dots: individual seeds. Diamonds: means ± sample SD. "
        "One calibration day; M3 fidelity limit remains.\n"
        "Queue/smoothness are proxies; insertion backlog is reported separately.",
        fontsize=10,
    )
    figure.savefig(output / "comparison.png", dpi=170)
    plt.close(figure)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", type=Path, default=Path("reports/m6/report.json"))
    p.add_argument("--audit", type=Path, default=Path("reports/m6/independent_audit.json"))
    p.add_argument("--output", type=Path, default=Path("reports/m6"))
    args = p.parse_args()
    summarize(args.report, args.audit, args.output)
