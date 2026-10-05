# Bay Area Autonomous Traffic Simulation

An open, local research testbed for asking a narrow question:

> Under clearly stated assumptions, how do different autonomous-vehicle coordination strategies change traffic on a small stretch of US-101?

This is a simulation research project, not a prediction system or a safety-critical driving controller. Results will only be meaningful after the model has been calibrated against observed traffic data.

For the current milestone state and handoff context, see the
[project memory](docs/project-memory.md), [roadmap](docs/project-roadmap.md),
and [domain glossary](CONTEXT.md). M0–M2 are complete; M3 calibration is active.

## What we will build first

We will begin with a small, reproducible corridor simulation rather than the entire Bay Area:

1. Build a SUMO road network for US-101 northbound between SR-237 and Page Mill Road.
2. Calibrate a human-driver baseline against selected Caltrans PeMS measurements.
3. Compare it with a deterministic cooperative following controller.
4. Add a centralized speed-advisory or ramp-control experiment.
5. Consider constrained reinforcement learning only after the earlier experiments are trustworthy.

## Project principles

- **Reality before cleverness:** a human-driver baseline must resemble observed traffic before comparing controllers.
- **One change at a time:** hold demand, road geometry, and vehicle assumptions fixed when evaluating a controller.
- **Reproducible runs:** every result records the scenario, random seed, parameters, and software versions.
- **Honest labels:** acceleration smoothness is not fuel use; ideal V2V communication is not a deployed radio system.
- **Safe scope:** this repository does not control real vehicles or infrastructure.

## Planned layout

```text
configs/       Reproducible scenario and experiment settings
data/          Local, untracked source and processed data
docs/          Design notes and experiment records
network/       SUMO network sources and manual corrections
routes/        Demand and route definitions
src/           Python simulation/controller code
tests/         Automated checks
outputs/       Untracked generated results
research/      Source-backed feasibility notes
```

## Local prerequisites

- Apple-Silicon macOS is supported as the intended development environment.
- [Eclipse SUMO](https://sumo.dlr.de/docs/index.html), including `sumo`, `netconvert`, and Python TraCI bindings.
- Python 3.11 or newer.
- Later phases may add PyTorch. Reinforcement learning is deliberately not a prerequisite for the first experiment.

The project ships with a first tested SUMO setup in its virtual environment.

## Python environment

All Python packages for this project belong in the project-local `.venv` folder.
Never install simulation dependencies into the system Python.

Create or refresh the environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install '.[dev]'
```

After changing project source code or dependencies, rerun the install command.
Use the environment without activating it:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
```

Or activate it for an interactive terminal:

```bash
source .venv/bin/activate
```

The official `eclipse-sumo`, `traci`, and `sumolib` packages are installed into
`.venv`; this project does not depend on a machine-wide SUMO installation.

## First runnable experiment

The first runnable experiment is a tiny two-lane freeway with one on-ramp. It
exists only to prove that the tools, metrics, and workflow work together. Its
traffic values are illustrative and are **not** a model of US-101.

```bash
.venv/bin/python -m bay_area_traffic_sim build-toy-network
.venv/bin/python -m bay_area_traffic_sim run-toy-baseline --seed 42
.venv/bin/python -m bay_area_traffic_sim run-toy-cacc --seed 42
.venv/bin/python -m bay_area_traffic_sim compare-toy --seeds 41 42 43
```

The second command prints completed-trip count, average travel time, waiting
time, and SUMO time loss. The CACC command changes only the vehicle-following
model. It is not an RL policy or a real V2V radio model. Generated network
files and reports stay under
`outputs/` and are intentionally not committed.

`compare-toy` prints the individual results plus their mean and sample spread.
That is the beginning of reporting uncertainty: we do not rely on only one run.

## Real-corridor network import

The US-101 boundary is saved in [configs/us101_corridor.json](configs/us101_corridor.json).
Put a timestamped OSM XML extract at `data/osm/us101_corridor.osm.xml`, then run:

```bash
.venv/bin/python -m bay_area_traffic_sim download-us101-osm
.venv/bin/python -m bay_area_traffic_sim import-us101-osm
```

The downloader uses the public Overpass API and writes a provenance record next
to the ignored map extract. The imported network appears under
`outputs/us101_corridor/`. It is only a draft until every interchange, ramp,
lane count, and allowed movement is manually audited.
Use the [US-101 network audit checklist](docs/us101-network-audit.md) to make
that review repeatable.

### Playwright map audit

For close Google Maps satellite screenshots used in the manual lane audit,
install the optional browser tool **inside this project's venv**:

```bash
.venv/bin/python -m pip install '.[visual-audit]'
.venv/bin/python scripts/capture_google_maps.py \
  --latitude 37.409514 --longitude -122.071728 --zoom 20 \
  --output outputs/map_audit/401948_moffett_nb.png
```

The script uses a local Chrome installation and writes a PNG plus a JSON file
with the URL and capture time. `outputs/` is ignored by Git, so third-party
imagery stays local. Aerial views can locate ramps and markings but are not a
survey of current lane counts or legal movements.

After downloading Station Metadata, generate a local detector-to-network
matching report to guide the visual audit:

```bash
.venv/bin/python -m bay_area_traffic_sim audit-us101-network
```

It measures each candidate detector's nearest non-internal SUMO road edge.
This catches mapping gaps but does not replace review around ramps and
interchanges.

## First PeMS calibration target

Put the PeMS `d04_text_station_5min_*.txt.gz` downloads under `data/pems/`,
then create an auditable summary of the morning peak:

```bash
.venv/bin/python -m bay_area_traffic_sim summarize-pems
```

It reads 07:00–08:59 local time from District 4, northbound US-101 mainline
detectors, rejects observations below 90% coverage, and writes its filter and
results to `outputs/pems_calibration/us101_northbound_d4_morning_peak.json`.
The corridor-specific metadata selection and manual decisions are in
`configs/us101_corridor_station_ids.json` and the [sensor audit](docs/us101-sensor-audit.md).

After placing the matching Station Metadata text files in `data/pems/metadata/`,
produce the first automatic detector list with:

```bash
.venv/bin/python -m bay_area_traffic_sim select-us101-stations
```

The command keeps only District 4, northbound US-101 **mainline** detector
locations inside the configured boundary. It writes station IDs, coordinates,
and source metadata to `outputs/pems_calibration/us101_corridor_station_selection.json`.
The reviewed inventory contains 13 accepted corridor cross-sections, five
excluded candidates, and one conservative holdout; review decisions and
caveats are recorded in the sensor audit.

The full reviewed inventory and the smaller subset used by the existing draft
baseline are stored in `configs/us101_corridor_station_ids.json`. Reproduce the
full M1 station-by-station report with:

```bash
.venv/bin/python -m bay_area_traffic_sim summarize-pems-stations \
  --station-ids-file configs/us101_corridor_station_ids.json \
  --station-ids-key accepted_corridor_station_ids \
  --lane-types ML \
  --output outputs/pems_calibration/us101_corridor_m1_station_profiles.json
```

The aggregate M1 report is generated with:

```bash
.venv/bin/python -m bay_area_traffic_sim summarize-pems \
  --station-ids-file configs/us101_corridor_station_ids.json \
  --station-ids-key accepted_corridor_station_ids \
  --output outputs/pems_calibration/us101_corridor_final_morning_peak.json
```

This report gives the “traffic rhythm” used to build the first human-traffic
scenario: observed flow and speed for each five-minute slice, averaged across
the selected days and sensors. Use the [PeMS sensor audit sheet](docs/us101-sensor-audit.md)
to resolve the remaining locations before treating this as a final calibration target.

## Draft real-corridor human baseline

The first H0 scenario converts five-minute PeMS station profiles into
passenger-car demand on the corrected SR-237-to-Oregon-Expressway network.
Station 402370 supplies the upstream flow, the measured Mathilda exit is split
from it, and the audited Mathilda, Moffett, and San Antonio on-ramp profiles are
injected at their mapped SUMO edges. Prepare the generated routes and their
assumption manifest with:

```bash
.venv/bin/python -m bay_area_traffic_sim prepare-us101-human-baseline
```

Then run the two-hour morning profile plus warmup and network-clearance time:

```bash
.venv/bin/python -m bay_area_traffic_sim run-us101-human-baseline --seed 42
```

For research comparisons, repeat the exact scenario across random seeds and
report both trip-metric and virtual-detector uncertainty:

```bash
.venv/bin/python -m bay_area_traffic_sim run-us101-human-baseline-multi \
  --seeds 41 42 43
```

This writes `outputs/us101_corridor/h0_multiseed_report.json`. Random-seed
spread captures stochastic driving variation only; it does not represent all
uncertainty in demand, detector data, network geometry, or model parameters.

The route is forced through ordered, detector-matched freeway checkpoints so
SUMO cannot choose a one-lane ramp as a geometric shortcut. This is a runnable
calibration draft, not the finished human baseline. It has human-like
stochastic following and the four measured, audited ramp movements currently
inside the study boundary. Eight missing ramp profiles, vehicle mix,
held-out-day validation, driver calibration, and remaining manual network
review still belong to M3.

Generate separate observed profiles for the six on-ramp and seven off-ramp
PeMS candidates with:

```bash
.venv/bin/python -m bay_area_traffic_sim summarize-pems-stations
```

Only mappings accepted in the [ramp audit](docs/us101-ramp-audit.md) become
SUMO demand; missing observations are not interpreted as zero. Human-baseline
runs also install lane-level virtual induction loops at the ten provisionally
reviewed mainline PeMS locations and write a five-minute station summary beside
the other run outputs. A station is automatically excluded from calibration
scoring when its PeMS lane count does not match the mapped SUMO edge.

After generating the observed mainline station profiles and running seed 42,
create the direct five-minute comparison with:

```bash
.venv/bin/python -m bay_area_traffic_sim summarize-pems-stations \
  --station-ids-file configs/us101_corridor_station_ids.json \
  --station-ids-key provisionally_reviewed_station_ids \
  --lane-types ML \
  --output outputs/pems_calibration/us101_mainline_station_profiles.json
.venv/bin/python -m bay_area_traffic_sim compare-us101-detectors
```

This reports flow percentage error and speed error separately for each matched
station rather than hiding spatial mismatches inside one corridor average.

Before estimating missing ramps, build the observed flow-conservation
diagnostic:

```bash
.venv/bin/python -m bay_area_traffic_sim analyze-us101-flow-balance
```

It orders reporting detectors along the SUMO route and measures how much flow
appears or disappears between neighbors. Comparisons involving a changed lane
count or a ramp/collector/diagonal station label are marked for review and are
not automatically treated as missing-ramp demand. It matches the same actual
dates and five-minute slots at both stations; older comparisons that averaged
different day sets are superseded. Explicit decisions live in
`configs/us101_flow_balance_audit.json`. Station 401948 is accepted as an
observed five-lane mainline cross-section: the October data show five active
lane measurements, and Caltrans documents a buffered managed/HOT lane in the
Moffett Boulevard–Old Middlefield Way area. The adjacent +330 and +1,529
vehicles/hour values were produced from unmatched days. On the same 12 dates
(288 five-minute slots), the net changes are about +238 and +1,622 vehicles per
hour, respectively. These are still *net* changes—not counts of individual
ramps—and remain blocked from missing-ramp demand until the movements and
detector mappings are reconciled. The mapped OSM/SUMO edge still has four lanes,
so its geometry mismatch remains visible in the report notes. See
[the Moffett-to-Shoreline pair audit](docs/us101-ramp-pair-audit.md).

To profile a detector on another freeway or direction, pass `--freeway` and
`--direction` (for example `--freeway 85 --direction S`). This was used to
inspect SR-85 station 402920 (about 129 vehicles/hour over the 12-day profile
window). PeMS identifies it as a southbound SR-85 on-ramp, and the nearest
generated network feature feeds southbound CA-85. It is likely outside the
northbound US-101 study path. Existing configs that inject its profile on the
NB HOV connector are counterfactual experiments only, not observed NB ramp
demand. See the [SR-85 sensitivity audit](docs/sr85-lane-sensitivity.md).

Human-baseline preparation now requires complete common observation dates
across its mainline entry and active ramp detectors. Its manifest records the
selected dates, and detector validation uses a matching-date copy of the
mainline profile. To reproduce the southbound 402920 station profile used in
the counterfactual sensitivity audit (without adding it to the accepted H0
baseline), run:

```bash
.venv/bin/python -m bay_area_traffic_sim summarize-pems-stations \
  --station-ids-file configs/us101_sr85_connector_station_ids.json \
  --freeway 85 \
  --direction S \
  --lane-types OR \
  --start-hour 7 \
  --end-hour 9 \
  --minimum-observed-percent 90 \
  --output outputs/pems_calibration/us101_sr85_connector_station_profiles.json
.venv/bin/python -m bay_area_traffic_sim run-us101-human-baseline-multi \
  --config configs/us101_human_baseline.json \
  --seeds 41 42 43 \
  --output outputs/us101_corridor/h0_date_aligned_multiseed_report.json
.venv/bin/python -m bay_area_traffic_sim run-us101-human-baseline-multi \
  --config configs/us101_human_baseline_sr85_candidate.json \
  --seeds 41 42 43 \
  --output outputs/us101_corridor/sr85_candidate/h0_sr85_candidate_multiseed_report.json
```

This is a demand-and-network sensitivity, not evidence that a traffic-control
policy works. The candidate config keeps the one-lane SUMO connector and
records the PeMS two-lane mismatch; do not use its flow as finalized demand
until the lane geometry is reconciled. Compare it with the regular baseline
using the same seed list.

The separate two-lane geometry hypothesis can be built and prepared with:

```bash
.venv/bin/python -m bay_area_traffic_sim build-sr85-two-lane-variant
.venv/bin/python -m bay_area_traffic_sim prepare-us101-human-baseline \
  --config configs/us101_human_baseline_sr85_two_lane.json
.venv/bin/python -m bay_area_traffic_sim run-us101-human-baseline-multi \
  --config configs/us101_human_baseline_sr85_two_lane.json \
  --seeds 41 42 43 \
  --output outputs/us101_corridor/sr85_two_lane/h0_sr85_two_lane_multiseed_report.json
```

The current variant maps both connector lanes to US-101 lane 5, representing a
possible two-to-one merge. A split mapping to US-101 lanes 4 and 5 caused
unrealistically long ramp queues in a diagnostic run. The current three-seed
variant completed all vehicles with no teleport or safety warnings, but its
traffic metrics are nearly identical to the one-lane candidate. This is only a
geometry sensitivity, not evidence that two lanes improve traffic or that the
lane-level merge has been confirmed. See the [SR-85 lane sensitivity notes](docs/sr85-lane-sensitivity.md).

## Status

**Phase 1 - runnable toy corridor.** The human-like and CACC sensitivity
scenarios run locally and report multi-seed metrics. They are deliberately
small, uncalibrated tool checks. In particular, record and investigate SUMO
emergency-braking warnings before treating any CACC result as a safety or
performance claim.

The full sequence of work and completion criteria live in the
[project roadmap](docs/project-roadmap.md).

## Research background

See [local feasibility research](research/local-feasibility.md) for the source-backed feasibility assessment and constraints that guide the initial scope.
