"""Build M3 station tables and observed/model speed and flow figures from saved reports."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import fmean, stdev

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports/m3"


def station_summary(report: dict) -> dict[int, dict]:
    ids = sorted({p["station_id"] for run in report["runs"] for p in run["station_comparisons"]})
    result = {}
    for station in ids:
        by_day = []
        for day in report["dates"]:
            points = [
                p
                for run in report["runs"]
                if run["date"] == day
                for p in run["station_comparisons"]
                if p["station_id"] == station
            ]
            flows = [p["flow_mean_absolute_percentage_error"] for p in points]
            speeds = [p["speed_mean_absolute_error_mph"] for p in points]
            by_day.append(
                {
                    "date": day,
                    "flow_mape_percent": fmean(flows),
                    "speed_mae_mph": fmean(speeds),
                    "flow_seed_sd_percent": stdev(flows) if len(flows) > 1 else 0,
                    "speed_seed_sd_mph": stdev(speeds) if len(speeds) > 1 else 0,
                }
            )
        result[station] = {
            "flow_mape_percent": fmean(day["flow_mape_percent"] for day in by_day),
            "speed_mae_mph": fmean(day["speed_mae_mph"] for day in by_day),
            "days": by_day,
        }
    return result


def profiles(run: dict) -> tuple[dict, dict]:
    directory = (ROOT / run["manifest_file"]).parent
    if (directory / "observed.json").is_file():
        observed = json.loads((directory / "observed.json").read_text())
        detected = json.loads((directory / f"detectors_seed_{run['seed']}.json").read_text())
        seen = observed["summary"]["profiles"]
        intervals = [p for p in detected["intervals"] if 900 <= p["begin_seconds"] < 8100]
    else:
        saved = json.loads((REPORTS / "profile_series.json").read_text())[run["manifest_file"]]
        seen, intervals = saved["observed"], saved["simulated"]
    return (
        {p["station_id"]: p["time_profile"] for p in seen},
        {(p["station_id"], p["begin_seconds"]): p for p in intervals},
    )


def timing_rows(report: dict) -> list[dict]:
    """Describe first sub-45-mph interval and lowest-speed interval, without fitting."""
    rows = []
    for run in report["runs"]:
        observed, simulated = profiles(run)
        for point in run["station_comparisons"]:
            station = point["station_id"]
            paired = []
            for interval in observed[station]:
                time = interval["time"]
                second = 900 + (int(time[:2]) - 7) * 3600 + int(time[3:]) * 60
                modeled = simulated[(station, second)]["speed_mph"]
                seen = interval["mean_speed_mph"]
                if seen is not None and modeled is not None:
                    paired.append((time, seen, modeled))
            onset = [next((t for t, *v in paired if v[i] < 45), None) for i in range(2)]
            delta = None
            if all(onset):
                minutes = [int(t[:2]) * 60 + int(t[3:]) for t in onset]
                delta = minutes[1] - minutes[0]
            rows.append(
                {
                    "date": run["date"],
                    "seed": run["seed"],
                    "station_id": station,
                    "observed_first_below_45_mph": onset[0],
                    "modeled_first_below_45_mph": onset[1],
                    "onset_difference_minutes": delta,
                    "observed_minimum_speed_mph": min(p[1] for p in paired),
                    "modeled_minimum_speed_mph": min(p[2] for p in paired),
                    "observed_minimum_speed_time": min(paired, key=lambda p: p[1])[0],
                    "modeled_minimum_speed_time": min(paired, key=lambda p: p[2])[0],
                }
            )
    return rows


def main() -> None:
    plt.switch_backend("Agg")
    calibration = json.loads((REPORTS / "calibration_report.json").read_text())
    validation = json.loads((REPORTS / "validation_report.json").read_text())
    candidates = json.loads((REPORTS / "candidates_report.json").read_text())
    reference = json.loads((REPORTS / "reference_report.json").read_text())
    sensitivity = json.loads((REPORTS / "sensitivity_report.json").read_text())
    series = {}
    for report in [calibration, validation, reference, sensitivity]:
        for run in report["runs"]:
            seen, modeled = profiles(run)
            series[run["manifest_file"]] = {
                "observed": [{"station_id": s, "time_profile": p} for s, p in seen.items()],
                "simulated": list(modeled.values()),
            }
    (REPORTS / "profile_series.json").write_text(json.dumps(series, indent=2) + "\n")
    timing = {
        "threshold_mph": 45,
        "resolution_minutes": 5,
        "limitation": "Descriptive onset threshold, not a calibration parameter. "
        "First interval may already be congested; a null onset means no paired "
        "interval below the threshold in the analysis window.",
        "calibration": timing_rows(calibration),
        "validation": timing_rows(validation),
    }
    (REPORTS / "timing_summary.json").write_text(json.dumps(timing, indent=2) + "\n")
    experiment = json.loads((ROOT / "configs/us101_m3_experiment.json").read_text())
    day = experiment["representative_calibration_date"]
    cal = station_summary(calibration)
    val = station_summary(validation)
    selected_runs = [run for run in calibration["runs"] if run["date"] == day]
    observed, _ = profiles(selected_runs[0])
    simulated = [profiles(run)[1] for run in selected_runs]
    _, original = profiles(reference["runs"][0])
    stations = [402370, 401534, 401507, 402377]
    for measure, observed_key, simulated_key, ylabel in [
        ("speed", "mean_speed_mph", "speed_mph", "Speed (mph)"),
        ("flow", "mean_flow_vehicles_per_5_minutes", "flow_vehicles_per_hour", "Flow (veh/h)"),
    ]:
        fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
        for ax, station in zip(axes.flat, stations, strict=True):
            times = [p["time"] for p in observed[station]]
            seconds = [900 + (int(t[:2]) - 7) * 3600 + int(t[3:]) * 60 for t in times]
            seen = [p[observed_key] * (12 if measure == "flow" else 1) for p in observed[station]]
            draws = [[p[(station, second)][simulated_key] for second in seconds] for p in simulated]
            values = [[draw[i] for draw in draws if draw[i] is not None] for i in range(len(times))]
            mean = [fmean(v) if v else float("nan") for v in values]
            low = [min(v) if v else float("nan") for v in values]
            high = [max(v) if v else float("nan") for v in values]
            old = [original[(station, second)][simulated_key] for second in seconds]
            ax.plot(times, seen, color="black", label="Observed")
            ax.plot(times, old, color="#d97706", linestyle="--", label="Original draft (seed 42)")
            ax.plot(times, mean, color="#2563eb", label="Selected H0 (3-seed mean)")
            ax.fill_between(
                times, low, high, color="#2563eb", alpha=0.16, label="Selected seed range"
            )
            ax.set_title(
                f"Station {station}" + (" (provisional 4 of 5 lanes)" if station == 402377 else "")
            )
            ax.set_ylabel(ylabel)
            ax.set_xticks(times[::4])
            ax.grid(alpha=0.2)
        axes[0, 0].legend(fontsize=8)
        fig.suptitle(f"M3 {measure} profiles, {day}; fixed calibration assumptions")
        fig.tight_layout()
        fig.savefig(REPORTS / f"{measure}_profiles.png", dpi=160)
        plt.close(fig)

    ordered_stations = [402370, 401996, 401998, 402372, 401534, 401507, 402377]
    times = [p["time"] for p in observed[402370]]
    seconds = [900 + (int(t[:2]) - 7) * 3600 + int(t[3:]) * 60 for t in times]
    observed_matrix = [[p["mean_speed_mph"] for p in observed[s]] for s in ordered_stations]
    original_matrix = [[original[(s, t)]["speed_mph"] for t in seconds] for s in ordered_stations]
    selected_matrix = [
        [fmean(p[(s, t)]["speed_mph"] for p in simulated) for t in seconds]
        for s in ordered_stations
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True, layout="constrained")
    for ax, matrix, label in zip(
        axes,
        [observed_matrix, original_matrix, selected_matrix],
        ["Observed", "Original draft", "Selected H0 (3 seeds)"],
        strict=True,
    ):
        plot = ax.imshow(matrix, aspect="auto", vmin=0, vmax=65, cmap="RdYlGn")
        ax.set_title(label)
        ax.set_xticks(range(0, len(times), 4), times[::4], rotation=45)
        ax.set_yticks(
            range(len(ordered_stations)),
            [f"{s}" + ("*" if s == 402377 else "") for s in ordered_stations],
        )
        ax.set_xlabel("Start of five-minute interval")
    axes[0].set_ylabel("Stations in downstream order (* partial subset)")
    fig.colorbar(plot, ax=axes, label="Speed (mph)", shrink=0.85)
    fig.suptitle(f"M3 congestion pattern, calibration day {day}")
    fig.savefig(REPORTS / "congestion_pattern.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey=True)
    for column, validation_day in enumerate(validation["dates"]):
        draws = [run for run in validation["runs"] if run["date"] == validation_day]
        seen, _ = profiles(draws[0])
        modeled = [profiles(run)[1] for run in draws]
        for row, station in enumerate([402370, 402372]):
            ax = axes[row, column]
            times = [p["time"] for p in seen[station]]
            seconds = [900 + (int(t[:2]) - 7) * 3600 + int(t[3:]) * 60 for t in times]
            values = [[p[(station, t)]["speed_mph"] for p in modeled] for t in seconds]
            ax.plot(
                times, [p["mean_speed_mph"] for p in seen[station]], color="black", label="Observed"
            )
            ax.plot(
                times, [fmean(v) for v in values], color="#2563eb", label="Frozen H0 (3-seed mean)"
            )
            ax.fill_between(
                times,
                [min(v) for v in values],
                [max(v) for v in values],
                color="#2563eb",
                alpha=0.16,
                label="Seed range",
            )
            ax.set_title(f"{validation_day}, station {station}")
            ax.set_ylabel("Speed (mph)")
            ax.set_xticks(times[::4])
            ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("M3 held-out upstream speeds: frozen settings, no validation tuning")
    fig.tight_layout()
    fig.savefig(REPORTS / "validation_speed_profiles.png", dpi=160)
    plt.close(fig)

    text = [
        "# M3 calibration and separate-day validation results",
        "",
        "Generated by `scripts/summarize_m3_baseline.py` from saved JSON reports.",
        "The versioned `profile_series.json` preserves five-minute observed/modeled "
        "series so these figures can be regenerated without the ignored SUMO runtime files.",
        "",
        "## Outcome",
        "",
        "M3's evaluation is complete. H0 remains provisional: the combined held-out "
        "speed target was missed, and October 15 missed both fidelity targets. "
        "Clean simulation health does not establish traffic fidelity. "
        "Settings were frozen before validation and were not retuned afterward. "
        "See [the closeout decision](../../docs/m3-human-baseline-report.md).",
        "",
        "Targets: mean full-cross-section flow MAPE ≤20%, speed MAE ≤10 mph.",
        "",
        "| Phase | Mean flow MAPE (%) | Mean speed MAE (mph) |",
        "| --- | ---: | ---: |",
        f"| Calibration (15 runs) | "
        f"{calibration['summary'][0]['mean_station_flow_mape_percent']:.2f} | "
        f"{calibration['summary'][0]['mean_station_speed_mae_mph']:.2f} |",
        f"| Held-out validation (6 runs) | "
        f"{validation['summary'][0]['mean_station_flow_mape_percent']:.2f} | "
        f"{validation['summary'][0]['mean_station_speed_mae_mph']:.2f} |",
        "",
        "## Fixed settings",
        "",
        f"Selected case: **{experiment['selected_candidate']}**. Three seeds (41–43) "
        "on each of five calibration weekdays and two reserved validation weekdays. "
        "Station summaries weight days equally and average seeds within each day. "
        "Station 402377 is a provisional four-lane subset and is excluded from candidate scoring.",
        "Station 400790 supplies the 80%-coverage inlet proxy upstream of the analysis reach; "
        "it is not scored. The six full-cross-section targets retain 90% coverage and their "
        "flow and speed are model outcomes. Validation conditions on each day's measured "
        "upstream and reporting-ramp counts.",
        "",
        "## Station errors",
        "",
        "| Station | Calibration flow MAPE (%) | Calibration speed MAE (mph) | "
        "Validation flow MAPE (%) | Validation speed MAE (mph) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for station in sorted(cal):
        text.append(
            f"| {station}{' (partial)' if station == 402377 else ''} | "
            f"{cal[station]['flow_mape_percent']:.2f} | {cal[station]['speed_mae_mph']:.2f} | "
            f"{val[station]['flow_mape_percent']:.2f} | {val[station]['speed_mae_mph']:.2f} |"
        )
    text += [
        "",
        "## Validation by day",
        "",
        "| Date | Mean full-lane flow MAPE (%) | Mean full-lane speed MAE (mph) | "
        "Runs clean and cleared |",
        "| --- | ---: | ---: | ---: |",
    ]
    excluded = set(experiment["scoring_excluded_station_ids"])
    for date in validation["dates"]:
        runs = [run for run in validation["runs"] if run["date"] == date]
        points = [
            p for run in runs for p in run["station_comparisons"] if p["station_id"] not in excluded
        ]
        text.append(
            f"| {date} | {fmean(p['flow_mean_absolute_percentage_error'] for p in points):.2f} | "
            f"{fmean(p['speed_mean_absolute_error_mph'] for p in points):.2f} | "
            f"{sum(run['clean_and_cleared'] for run in runs)}/{len(runs)} |"
        )
    text += [
        "",
        "## Congestion timing",
        "",
        "The congestion-pattern figure compares stations in downstream order on the "
        "preselected calibration day. `timing_summary.json` records, for every final "
        "run and reporting station, the first paired interval below 45 mph and the "
        "lowest-speed interval. This descriptive threshold was not used for fitting. "
        "Five-minute sampling and a first interval already below the threshold limit "
        "onset precision; missing crossings remain null.",
    ]
    text += [
        "",
        "## Calibration candidate ledger",
        "",
        "| Candidate | Mean flow MAPE (%) | Mean speed MAE (mph) | SUMO warning lines | "
        "Vehicles still running/waiting at recorded end |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in candidates["summary"]:
        run = next(run for run in candidates["runs"] if run["case"] == item["case"])
        final = run["health"]["final_summary"]
        unfinished = int(final["running"]) + int(final["waiting"])
        text.append(
            f"| {item['case']} | {item['mean_station_flow_mape_percent']:.2f} | "
            f"{item['mean_station_speed_mae_mph']:.2f} | "
            f"{len(run['health']['warning_lines'])} | {unfinished} |"
        )
    text += [
        "",
        "Initial/intermediate candidates used 30-minute clearance; the final split cases "
        "and frozen calibration/validation use two hours. Failed trials remain in the ledger.",
        "",
        "## Sensitivities",
        "",
        "| Case | Mean full-lane flow MAPE (%) | Mean full-lane speed MAE (mph) | "
        "Clean and cleared |",
        "| --- | ---: | ---: | --- |",
    ]
    for item in sensitivity["summary"]:
        text.append(
            f"| {item['case']} | {item['mean_station_flow_mape_percent']:.2f} | "
            f"{item['mean_station_speed_mae_mph']:.2f} | {item['all_clean_and_cleared']} |"
        )
    baseline_lane = next(
        p
        for run in calibration["runs"]
        if run["date"] == day and run["seed"] == 42
        for p in run["station_comparisons"]
        if p["station_id"] == 402377
    )
    alternative_lane = next(
        p
        for run in sensitivity["runs"]
        if run["case"] == "lane_402377_0_3"
        for p in run["station_comparisons"]
        if p["station_id"] == 402377
    )
    text += [
        "",
        "## Station 402377 lane sensitivity",
        "",
        f"Calibration day {day}, seed 42. All five physical SUMO lanes are recorded; "
        "the two four-lane subsets are compared to the same four reporting PeMS channels. "
        "SUMO numbers lanes from the right, starting at zero. This is a fit sensitivity, "
        "not proof of field wiring.",
        "",
        "| SUMO subset | Flow MAPE (%) | Speed MAE (mph) |",
        "| --- | ---: | ---: |",
        f"| 1–4 (omit rightmost; working mapping) | "
        f"{baseline_lane['flow_mean_absolute_percentage_error']:.2f} | "
        f"{baseline_lane['speed_mean_absolute_error_mph']:.2f} |",
        f"| 0–3 (omit leftmost; alternative) | "
        f"{alternative_lane['flow_mean_absolute_percentage_error']:.2f} | "
        f"{alternative_lane['speed_mean_absolute_error_mph']:.2f} |",
        "",
        "## Run health and provenance",
        "",
    ]
    for label, report in [("Calibration", calibration), ("Validation", validation)]:
        text.append(
            f"{label}: {sum(run['clean_and_cleared'] for run in report['runs'])}/"
            f"{len(report['runs'])} runs clean and cleared. Treatment hash: "
            f"`{report['runs'][0]['treatment_sha256']}`."
        )
    text += [
        "",
        "Trip metrics cover all generated trips, including warmup and clearance. "
        "Three-seed spread covers stochastic driving only. Unknown OD allocation, "
        "missing downstream ramp movements, fleet share, meter behavior, and detector mapping "
        "remain additional uncertainty. See [the demand ledger](../../docs/m3-demand-ledger.md).",
        "",
        "![Speed profiles](speed_profiles.png)",
        "",
        "![Flow profiles](flow_profiles.png)",
        "",
        "![Congestion pattern](congestion_pattern.png)",
        "",
        "![Held-out upstream speed profiles](validation_speed_profiles.png)",
    ]
    (REPORTS / "README.md").write_text("\n".join(text) + "\n")
    (REPORTS / "station_summary.json").write_text(
        json.dumps({"calibration": cal, "validation": val}, indent=2) + "\n"
    )
    print(f"Wrote M3 tables and figures to {REPORTS}")


if __name__ == "__main__":
    main()
