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

## Status

**Phase 1 - runnable toy corridor.** The human-like and CACC sensitivity
scenarios run locally and report multi-seed metrics. They are deliberately
small, uncalibrated tool checks. In particular, record and investigate SUMO
emergency-braking warnings before treating any CACC result as a safety or
performance claim.

## Research background

See [local feasibility research](research/local-feasibility.md) for the source-backed feasibility assessment and constraints that guide the initial scope.
