# M4 experiment harness closeout

**Status: complete. Closed 2026-10-16.**

The plan was saved first, followed by the specification, implementation,
automated checks, and real-run acceptance. The frozen M3 treatment is preserved.
M4 acceptance establishes a reproducible measurement harness; M3's held-out
traffic-fidelity limitation still applies.

## Deliverables and reproduction

- [Plan](m4-experiment-harness-plan.md)
- [Specification](m4-experiment-harness-spec.md)
- [Explicit experiment config](../configs/us101_m4_experiment.json)
- [Versioned JSON report](../reports/m4/report.json)
- [Readable full metric summary](../reports/m4/summary.md)
- [M3 replay comparison](../reports/m4/m3_replay_comparison.json)

With the frozen M3 inputs available:

```bash
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim run-us101-experiment
```

The command finished with exit code 0. The shipped configuration selects H0 on
October 8, 2025, seeds 41–43, a 1 s measurement period, and a 0.1 m/s stopped
threshold. Each seed has isolated routes, manifest, trip records, detector
outputs, health, compressed FCD, and results in
`outputs/us101_corridor/m4/m4_h0_2025_10_08/`. Reports carry source, configuration,
network, input and route hashes plus the SUMO version. No new dependency was added.
Existing run directories are preserved; repeat with a copied config and a new
experiment ID using `--config`.

## Acceptance evidence

| Criterion | Evidence |
| --- | --- |
| AC1: specification precedes implementation | The plan and specification were written before the new source files and runner changes. This closeout maps each criterion to evidence. |
| AC2: metric formulas and windows | Hand-calculated fixtures in `tests/test_experiment_harness.py` cover threshold equality, empty/missing samples, arrival/departure boundaries, unfinished trips, p95, ramp filtering, speed variability, and acceleration squares. |
| AC3: configuration and aggregation | Acceptance checks reject invalid dates/seeds/periods/thresholds, unsafe outputs, incompatible comparisons, and incomplete metric aggregates. |
| AC4: orchestration and failures | Controlled runs check isolated paths, sorted results, failure retention, JSON/Markdown output, overwrite refusal, and CLI nonzero failure. Actual source/provenance hashes are checked in the replay evidence. |
| AC5: actual multi-seed command | 3/3 runs accepted with all metric families; 7,200 measured timesteps per run. Every run loaded, inserted, and ended 22,951 vehicles with zero final waiting/running/discarded/collisions/teleports and no SUMO warnings. |
| AC6: frozen traffic replay | For all three seeds, all legacy trip metrics exactly match M3. Generated routes and detector-summary files match M3 byte for byte. Network, driver, fleet, and source provenance match the freeze. |
| AC7: regression checks | Focused checks: 31 passed. Full suite: 67 passed. Repository lint and whitespace checks passed. |

Commands used for automated checks:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_experiment_harness.py tests/test_metrics.py tests/test_experiments.py tests/test_real_corridor.py tests/test_cli.py
PYTHONPATH=src .venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
git diff --check
```

The full suite completed in 71.91 s. SUMO was `Eclipse SUMO sumo 1.27.1`.
The optional `rtree` module is absent, so sumolib used its existing detector
lookup fallback. This Python lookup notice is separate from SUMO run warnings.
There were no specification deviations.

## Results

These are means and sample standard deviations across three seeds on one
calibration day. They describe the frozen human baseline, with no controller
comparison or new fit to observed data.

| Metric | Seed mean | Sample SD | Unit |
| --- | ---: | ---: | --- |
| Network exit throughput | 8274.5000 | 29.4449 | veh/h |
| Departure-cohort mean travel time | 917.5052 | 8.8885 | s |
| Departure-cohort p95 travel time | 2472.7750 | 39.0675 | s |
| Mean stopped vehicles | 88.9196 | 1.2976 | vehicles |
| Peak stopped vehicles | 211.0000 | 29.2062 | vehicles |
| Mean entrance-approach stopped vehicles | 10.1361 | 0.1717 | vehicles |
| Temporal variability of domain mean speed | 6.0551 | 0.2184 | mph |
| Mean squared acceleration | 0.6636 | 0.0015 | m²/s⁴ |
| RMS acceleration | 0.8146 | 0.0009 | m/s² |

The complete 20-metric table and individual seed values are in the result files.
Travel-time metrics follow actual departures during 07:00–09:00 through clearance.
Exit throughput counts completions during that window, including modeled exits.

## Interpretation and remaining limits

- M3 missed the October 15 held-out bottleneck and the combined held-out speed
  target (14.90 mph MAE). M4 adds instrumentation without changing that result.
- Domain metrics include the upstream buffer, ramps, and internal junction links.
  Trip averages combine routes of different lengths. Exit throughput is not a
  mainline bottleneck capacity estimate.
- Queue proxies count on-road stopped vehicles and exclude vehicles waiting to
  insert. The runs have substantial temporary insertion backlogs in their raw
  SUMO summaries. Actual-departure travel times also exclude insertion delay;
  interpret these populations explicitly in later comparisons.
- Entrance queue counts exclude shared mainline and internal junction links.
  Native speed and acceleration output is rounded to two decimal places.
- Speed variability is the temporal standard deviation of the domain mean speed;
  it does not establish wave stability or response to a controlled disturbance.
- Squared acceleration and RMS acceleration describe smoothness, not energy use.
- Three seeds on one calibration day measure stochastic spread only. Demand,
  unknown ramp movements, truck share, network assumptions, and the failed
  held-out day require separate sensitivity and uncertainty work.

M0–M4 are complete at their documented practical standards. M5–M8 remain.
