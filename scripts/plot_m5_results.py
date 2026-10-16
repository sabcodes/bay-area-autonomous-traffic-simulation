"""Plot paired seed differences for the accepted supervised M5 comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot(report_path: Path, output: Path) -> None:
    report = json.loads(report_path.read_text())
    if not report["accepted"]:
        raise ValueError("Refuse to plot performance from a rejected experiment.")
    comparison = report["paired_comparisons"][0]["metrics"]
    panels = [
        ("network_exit_throughput_vehicles_per_hour", "Network exit throughput", "veh/h"),
        ("scheduled_cohort_mean_total_time_seconds", "Scheduled-cohort total time", "s"),
        ("mean_stopped_vehicles", "Mean stopped-vehicle proxy", "vehicles"),
        ("mean_ramp_stopped_vehicles", "Entrance-approach stopped proxy", "vehicles"),
        ("temporal_mean_speed_stddev_mph", "Temporal mean-speed variability", "mph"),
        ("rms_acceleration_m_per_s2", "RMS acceleration", "m/s²"),
    ]
    figure, axes = plt.subplots(3, 2, figsize=(11, 10.5), layout="constrained")
    for axis, (metric, title, unit) in zip(axes.flat, panels, strict=True):
        stats = comparison[metric]
        differences = [pair["difference"] for pair in stats["pairs"]]
        axis.axvline(0, color="#7a7a7a", linewidth=1)
        axis.scatter(differences, [1, 2, 3], color="#176ba0", s=45, zorder=3)
        axis.errorbar(
            stats["mean_difference"],
            0,
            xerr=stats["sample_standard_deviation"],
            fmt="D",
            color="#222222",
            capsize=4,
            markersize=6,
        )
        axis.set_yticks([0, 1, 2, 3], ["Mean ± SD", "Seed 41", "Seed 42", "Seed 43"])
        axis.set_ylim(3.6, -0.6)
        axis.set_title(title)
        axis.set_xlabel(f"CACC − H0 ({unit})")
        axis.grid(axis="x", alpha=0.2)
        axis.spines[["top", "right", "left"]].set_visible(False)
    shares = []
    for run in report["runs"]:
        if run["scenario"] == "CACC":
            diagnostics = run["controller_diagnostics"]
            shares.append(
                100
                * diagnostics["commands"]
                / (diagnostics["commands"] + diagnostics["supervised_native_samples"])
            )
    figure.suptitle("Supervised CACC: paired changes on October 8, 2025", fontsize=15)
    figure.supxlabel(
        f"Three seeds; SD is seed spread, not a confidence interval. "
        f"All-run passenger active-command share: {min(shares):.2f}–{max(shares):.2f}%.\n"
        "Queue, speed and smoothness are proxies. M3 field-fidelity limits remain.",
        fontsize=9,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180)
    plt.close(figure)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("reports/m5/report.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/m5/paired_changes.png"))
    args = parser.parse_args()
    plot(args.report, args.output)
