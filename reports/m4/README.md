# M4 experiment harness evidence

The [plan](../../docs/m4-experiment-harness-plan.md) and
[specification](../../docs/m4-experiment-harness-spec.md) preceded implementation.
Acceptance uses the frozen H0 scenario on October 8, 2025, with seeds 41–43.
**Acceptance complete: 3/3 runs passed.** All legacy trip metrics, route files,
and detector summaries match M3. See the
[closeout](../../docs/m4-experiment-harness-report.md),
[JSON report](report.json), [metric summary](summary.md), and
[replay comparison](m3_replay_comparison.json).

The default command is:

```bash
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim run-us101-experiment
```

`configs/us101_m4_experiment.json` declares scenarios, dates, seeds, measurement
settings, and output location. The runtime JSON and Markdown reports are saved
under `outputs/us101_corridor/m4/m4_h0_2025_10_08/`, beside isolated run folders.
Raw trajectory traces are compressed and remain in ignored runtime outputs.
Existing experiment directories are preserved; use a copied config with a new
experiment ID to repeat the run.

Metrics use the observation window after warmup. Departure-cohort trip metrics
follow actual departures through clearance; network exit throughput counts
arrivals during the window. Stopped-vehicle queue proxies exclude vehicles
waiting to insert. Speed variation measures changes in the domain mean speed;
acceleration squared measures smoothness. Neither establishes real-world
controller performance. M3's held-out fidelity limitation remains in force.
