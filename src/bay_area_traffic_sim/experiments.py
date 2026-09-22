"""Repeat toy experiments and report uncertainty across random seeds."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import asdict
from statistics import fmean, stdev

from bay_area_traffic_sim.metrics import RunMetrics


def summarize_runs(runs: Sequence[RunMetrics]) -> dict[str, dict[str, float | None]]:
    """Return mean and sample spread for each metric across completed runs."""

    if not runs:
        raise ValueError("At least one simulation run is required.")

    metric_names = asdict(runs[0]).keys()
    summary: dict[str, dict[str, float | None]] = {}
    for name in metric_names:
        values = [getattr(run, name) for run in runs]
        if any(value is None for value in values):
            summary[name] = {"mean": None, "sample_standard_deviation": None}
            continue

        numeric_values = [float(value) for value in values if value is not None]
        summary[name] = {
            "mean": fmean(numeric_values),
            "sample_standard_deviation": stdev(numeric_values) if len(numeric_values) > 1 else 0.0,
        }
    return summary


def repeat(
    run_scenario: Callable[[int], RunMetrics], seeds: Sequence[int]
) -> tuple[list[RunMetrics], dict[str, dict[str, float | None]]]:
    """Run one scenario for every seed and return individual and summary results."""

    runs = [run_scenario(seed) for seed in seeds]
    return runs, summarize_runs(runs)
