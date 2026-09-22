# Bay Area Autonomous Traffic Simulation

An open, local research testbed for asking a narrow question:

> Under clearly stated assumptions, how do different autonomous-vehicle coordination strategies change traffic on a small stretch of US-101?

This is a simulation research project, not a prediction system or a safety-critical driving controller. Results will only be meaningful after the model has been calibrated against observed traffic data.

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
then create an auditable summary of the weekday morning peak:

```bash
.venv/bin/python -m bay_area_traffic_sim summarize-pems
```

It reads 07:00–08:59 local time from District 4, northbound US-101 mainline
detectors, rejects observations below 90% coverage, and writes its filter and
results to `outputs/pems_calibration/us101_northbound_d4_morning_peak.json`.
The downloaded files alone still span all of District 4's US-101. Download
**Station Metadata** next; we will use it to identify only the detector IDs
between SR-237 and Page Mill Road before using the data to tune the corridor.

After placing the matching Station Metadata text files in `data/pems/metadata/`,
produce the first automatic detector list with:

```bash
.venv/bin/python -m bay_area_traffic_sim select-us101-stations
```

The command keeps only District 4, northbound US-101 **mainline** detector
locations inside the configured corridor boundary. It writes the station IDs,
coordinates, and source metadata files to
`outputs/pems_calibration/us101_corridor_station_selection.json`. The list
still needs the short visual map audit described above.

The current candidate IDs and a smaller, provisional reviewed subset are stored
in `configs/us101_corridor_station_ids.json`. Use the provisional subset for
the first corridor-specific morning-peak summary. It excludes the two Moffett
locations still marked unsure and eight northern locations added when the map
boundary was corrected:

```bash
.venv/bin/python -m bay_area_traffic_sim summarize-pems \
  --station-ids-file configs/us101_corridor_station_ids.json \
  --station-ids-key provisionally_reviewed_station_ids \
  --output outputs/pems_calibration/us101_corridor_provisional_morning_peak.json
```

This report gives the “traffic rhythm” used to build the first human-traffic
scenario: observed flow and speed for each five-minute slice, averaged across
the selected days and sensors. Use the [PeMS sensor audit sheet](docs/us101-sensor-audit.md)
to resolve the remaining locations before treating this as a final calibration target.

## Draft real-corridor human baseline

The first H0 scenario converts that provisional five-minute PeMS profile into
mainline passenger-car demand on the corrected SR-237-to-Oregon-Expressway
network. Prepare the generated route and its assumption manifest with:

```bash
.venv/bin/python -m bay_area_traffic_sim prepare-us101-human-baseline
```

Then run the two-hour morning profile plus warmup and network-clearance time:

```bash
.venv/bin/python -m bay_area_traffic_sim run-us101-human-baseline --seed 42
```

The route is forced through ordered, detector-matched freeway checkpoints so
SUMO cannot choose a one-lane ramp as a geometric shortcut. This is a runnable
calibration draft, not the finished human baseline. It has human-like
stochastic following, but currently has only mainline passenger-car demand.
Ramp demand, vehicle mix, held-out-day validation, and manual network
corrections still belong to M3.

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
