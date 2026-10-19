# Traffic Coordination Experiments on US-101

An independent engineering and simulation study exploring cooperative vehicle
following and centralized speed control on a modeled Bay Area freeway corridor.

## TL;DR

- **The experiment:** Reconstruct a northbound US-101 corridor from SR-237 to
  the Oregon Expressway/Page Mill Road connection, build a human-like traffic
  baseline using observed traffic data, and compare two fixed coordination
  policies under matched network, demand, fleet and random seeds.
- **What we measured:** Vehicle throughput, travel time including delays
  entering the network, stopped-vehicle queue proxies, insertion backlog,
  speed variability and longitudinal acceleration smoothness.
- **What we found:** Neither tested policy established a consistent overall
  traffic benefit. Cooperative following slightly reduced RMS acceleration
  but increased mean total travel time. Centralized speed control had small
  favorable base mean effects that varied across seeds and did not persist
  at higher demand.
- **What we used:** Python, Eclipse SUMO/libsumo, TraCI, NumPy, pyproj,
  Matplotlib, OpenStreetMap and Caltrans PeMS observations, with pytest and
  Ruff for verification.
- **How far the results reach:** The baseline missed its held-out speed
  target, cooperative commands engaged during roughly 2% of passenger
  timesteps, and the policy sensitivity campaign covered one date.
  These are conditional simulation findings.

Start with the [final analysis](docs/final-research-report.md),
[generated result tables](reports/m8/results.md) or
[reproduction guide](docs/reproduction.md).

## What was built

The project follows a traffic-control question through the engineering needed
to test it: road-network reconstruction and manual audits, detector-data
processing, baseline calibration and validation, controller implementation,
matched simulation runs, and independent checks of saved results.

Three policies share the modeled corridor and physical inputs:

| Policy | Behavior |
| --- | --- |
| **H0: human-like baseline** | SUMO's native following and lane changing, with passenger cars and a generic 4% truck proxy. |
| **CACC: supervised cooperative following** | A deterministic passenger-car acceleration overlay using local gap/speed and ideal leader acceleration messages. It yields to native maneuver requests and retains SUMO safety constraints. |
| **CENTRAL: variable speed limits** | A fixed rule observes downstream mean speed and adjusts upstream speed limits. It runs independently of CACC on human-like traffic. |

The final sensitivity campaign contains **54 runs**: five seeds per base policy
and three per sensitivity treatment. It varies demand, equipment share,
message range/delay/loss, requested following headway and the centralized speed
target. The comparison uses a two-hour morning observation window on
October 8, 2025, with warmup and subsequent clearance.

See the [experiment design and limits](docs/m7-sensitivity-uncertainty-spec.md)
and [controller definitions](docs/final-research-report.md#policy-definitions).

## What the experiments found

The five-seed base comparison gives the following mean changes relative to H0:

| Policy | All-exit throughput | Scheduled total travel time | RMS acceleration |
| --- | ---: | ---: | ---: |
| Supervised cooperative following | −0.212% | +0.709% | −0.775% |
| Centralized variable speed limits | +0.523% | −1.146% | +0.487% |

Lower travel time and RMS acceleration are favorable for their respective
measures. Acceleration smoothness does not measure fuel use or energy.
All-exit throughput includes ramp completions and is not mainline capacity.
Scheduled total travel time includes insertion delay for vehicles intended
to depart during the observation window.

The centralized policy's base paired effects were **+43.20 ± 91.50 vehicles/hour**
and **−17.65 ± 38.24 seconds** of scheduled total time, expressed as mean ±
sample standard deviation across seeds. Seed spread exceeded the mean effects.
At 0.8× demand the policy never activated and exactly matched H0; at 1.2× demand
its small favorable base mean effects did not persist.

Cooperative following reduced base RMS acceleration on all five seeds, but its
throughput and travel-time effects were mixed. Taken together, the experiments
establish no consistent overall traffic benefit from either tested policy.

![Paired policy effects across sensitivity cases](reports/m7/paired_sensitivity.png)

Read the [full interpretation](docs/final-research-report.md),
[paired effects and controller activity](reports/m7/README.md), and
[machine-readable headline results](reports/m8/headline_results.json).
The [complete campaign report](reports/m7/report.json) retains all 30 metrics
and individual run records.

## Baseline validation and limitations

The baseline was calibrated on five October 2025 weekdays and evaluated on two
reserved weekdays, with three seeds per day. The combined held-out speed
error missed the project's target:

| Evaluation | Mean flow error (MAPE) | Mean speed error (MAE) |
| --- | ---: | ---: |
| Calibration: 15 runs | 8.32% | 8.15 mph |
| Held-out validation: 6 runs | 19.37% | 14.90 mph |
| Project targets | ≤20% | ≤10 mph |

One validation day missed both targets. This limits inference about real
US-101 traffic, even though the final runs completed cleanly.

Other limits matter when interpreting the controller comparisons:

- Cooperative control was active during roughly **2% of all-run passenger
  timesteps**. Equipment share does not imply continuous cooperative control.
- The sensitivity screen varies one factor at a time on **one calibration
  date**. It does not estimate factor interactions or total uncertainty.
- Communication and centralized sensing/actuation are simplified. The tested
  policies do not establish real-vehicle safety or deployment readiness.
- Exact full simulation replay requires archived derived-input snapshots that
  are not distributed by Git. Portable reconstruction of their frozen bytes
  from raw data has not been demonstrated.

The [baseline results and figures](reports/m3/README.md),
[validation closeout](docs/m3-human-baseline-report.md), and
[final limitations](docs/final-research-report.md) document these boundaries.

## Data, reports and analysis

| Resource | What it contains |
| --- | --- |
| [Final analysis](docs/final-research-report.md) | Question, methods, policy definitions, findings and limitations. |
| [Generated result tables](reports/m8/results.md) · [JSON](reports/m8/headline_results.json) | Recomputed baseline scores and 52 paired headline metric records. |
| [Sensitivity results](reports/m7/README.md) · [full JSON](reports/m7/report.json) | Policy comparisons, seed spread, controller activity and factor effects. |
| [Baseline results](reports/m3/README.md) · [five-minute series](reports/m3/profile_series.json) | Calibration, validation and observed/modeled traffic profiles. |
| [Independent campaign audit](reports/m7/independent_audit.json) | Recorded checks of native outputs, metrics, matched inputs and null controls. |
| [Measurement specification](docs/m4-experiment-harness-spec.md) | Metric populations, observation windows, units and missing-value handling. |
| [Demand ledger](docs/m3-demand-ledger.md) · [sensor audit](docs/us101-sensor-audit.md) | Traffic-data selection, missing movements and detector assumptions. |
| [Accepted network provenance](network/us101_corridor/accepted_m2.provenance.json) · [network audit](docs/us101-m2-acceptance.md) | OSM-derived geometry, correction history and practical acceptance checks. |
| [Methods background](docs/research-lab-methods.md) · [methodology sources](research/m7-methodology.md) | Source-backed rationale and explicit experimental assumptions. |

**Data sources:** [Caltrans PeMS](https://pems.dot.ca.gov/) Station 5-Minute
and Station Metadata exports supply flow and speed observations.
[Caltrans traffic census](https://dot.ca.gov/programs/traffic-operations/census)
supplies annual ramp/truck context; the saved spreadsheets and source links are
listed in [their provenance record](data/caltrans/provenance.json).
Road geometry comes from [OpenStreetMap](https://www.openstreetmap.org/copyright),
with [extract provenance](data/osm/us101_corridor.osm.provenance.json),
versioned corrections and an accepted compressed network snapshot.

The repository includes compact reports, figures, configs and observed/modeled
profile series. PeMS raw exports, archived derived profiles and large native
simulation outputs remain local. The [reproduction guide](docs/reproduction.md)
distinguishes saved-evidence verification from full simulation replay.
OSM-derived data retain their source attribution and ODbL obligations.

## Verify the saved results

With Python 3.11 or newer and Git, run from the repository root:

```sh
python3 scripts/build_m8_package.py --check
```

This check writes nothing and needs no SUMO installation or private/local data.
It recomputes the headline tables from saved reports and checks content hashes
and frozen simulator bindings. It verifies saved evidence and package integrity;
it does not rerun the simulations or establish field validity.

## Run locally

The recorded simulation environment is **SUMO/libsumo 1.27.1 on Apple Silicon
macOS**. Install dependencies inside the project-local virtual environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install '.[dev,reports]'
.venv/bin/python -m pip install 'eclipse-sumo==1.27.1' 'libsumo==1.27.1' 'traci==1.27.1' 'sumolib==1.27.1'
```

A small synthetic freeway/on-ramp example exercises the tools without PeMS
inputs. Its traffic values are illustrative:

```sh
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim build-toy-network
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim compare-toy --seeds 41 42 43
```

Run the regression suite and lint against current source:

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q
.venv/bin/ruff check src tests scripts
```

For full corridor replay, follow the [reproduction guide](docs/reproduction.md),
including the archived-input checks and fresh experiment IDs. Runtime outputs
belong under ignored `outputs/`; preserve accepted reports when repeating runs.

## Repository guide

| Directory | Contents |
| --- | --- |
| `src/` · `scripts/` · `tests/` | Simulation/controller code, analysis and verification. |
| `configs/` | Scenario definitions and frozen experiment settings. |
| `network/` · `routes/` | Network snapshots, corrections and toy routes. |
| `data/` | Versioned source/provenance subset and ignored local observations. |
| `reports/` | Saved results, figures and audit records. |
| `docs/` · `research/` | Methods, detailed reports, specifications and supporting sources. |

The completed scope and future directions are recorded in the
[roadmap](docs/project-roadmap.md). The [domain glossary](CONTEXT.md),
[project memory](docs/project-memory.md) and
[review record](docs/m1-m8-adversarial-council.md) retain development context.
