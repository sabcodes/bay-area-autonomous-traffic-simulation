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

We will add an installation script after agreeing on the first scenario definition so the setup is tested rather than merely documented.

## Python environment

All Python packages for this project belong in the project-local `.venv` folder.
Never install simulation dependencies into the system Python.

Create or refresh the environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
```

Use the environment without activating it:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
```

Or activate it for an interactive terminal:

```bash
source .venv/bin/activate
```

`SUMO` is a native simulator installed separately from Python. Its Python
bindings will be installed into `.venv` when we set up the first scenario.

## Status

**Phase 0 - repository foundation.** No scenario, traffic data, or controller has been validated yet.

## Research background

See [local feasibility research](research/local-feasibility.md) for the source-backed feasibility assessment and constraints that guide the initial scope.
