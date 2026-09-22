# Experiment charter

## Research question

For a calibrated US-101 northbound corridor, how do selected idealized
autonomous-vehicle coordination policies affect throughput, travel time,
speed stability, and queue formation compared with a human-like baseline?

## Initial scenarios

| ID | Scenario | Purpose |
| --- | --- | --- |
| H0 | Human-like SUMO traffic | Calibration and comparison baseline |
| A1 | Autonomous vehicles without cooperation | Isolate the effect of shorter, deterministic following behavior |
| C1 | Rule-based cooperative following | Test local coordination without training an AI policy |
| S1 | Centralized speed advisory or ramp control | Test a small, explainable system-level intervention |

## Rules for a fair comparison

- Use the same road network, demand window, random-seed set, and vehicle mix for every scenario in an experiment.
- Calibrate H0 on one set of observed days and evaluate it on separate days.
- Record all controller parameters, SUMO version, network source date, and data-extraction rules.
- Run multiple seeds and publish an interval or spread, not only a single best result.
- Treat 100% AV penetration, perfect V2V, and very short headways as explicit sensitivity assumptions.

## Measures

- Completed vehicles and bottleneck throughput.
- Travel time and delay relative to free-flow travel time.
- Speed variability and recovery after a defined disturbance.
- Queue length and ramp waiting time.
- Acceleration smoothness as a proxy only; add an energy model before reporting energy or fuel use.

## Not in the first milestone

- Full Bay Area simulation.
- Per-vehicle multi-agent reinforcement learning.
- Claims about real-world safety, deployment readiness, or exact regional benefits.
