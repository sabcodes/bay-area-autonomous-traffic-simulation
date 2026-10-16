# M5 cooperative CACC specification

Version 1. Written 2026-10-16 after the plan and before source implementation.

## Treatment and reproducible command

Run `PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim
run-us101-experiment --config configs/us101_m5_experiment.json`.
Declare H0 and CACC scenarios, October 8, 2025, seeds 41–43, 1 s measurement
samples, 0.1 m/s stop threshold, and an unused directory under outputs/.
Both reference the frozen M3 baseline. Optional scenario `controller` is absent
for H0; CACC declares all parameters below. Reject unknown policies, keys,
nonfinite/out-of-range values, or a headway below the frozen safety headway
before launching SUMO. Do not modify frozen route XML or driver/fleet settings.

All passenger vehicles (96% expected fleet share) receive the overlay after
insertion, on every modeled route, including ramps and the upstream buffer.
Trucks retain H0 behavior. Passenger leaders broadcast actual previous-step
acceleration without packet loss or additional latency, within 250 m. Trucks
do not broadcast: their followers use ACC without acceleration feedforward.
This is a deterministic command law given state, not a noise-free traffic
model: the unchanged Krauss safety layer and fleet remain seed dependent.
This is a conservative custom CACC overlay, not SUMO's native CACC model or a
validated real-vehicle controller. No platoon formation or lane-change commands.

## Command law and timing

Simulation and control step dt = 0.5 s. After each simulation step, subscribe
new departures to speed, acceleration, allowed speed, vehicle type, and leader
ID/gap with 250 m lookahead. Read one complete subscription snapshot. Calculate
commands from that snapshot in sorted vehicle-ID order; apply to the next step.
Never scan vehicle pairs. A missing ego/leader subscription is a recorded native
fallback (`setSpeed(-1)`); an empty leader ID or an out-of-range leader uses
free cruise. Treat negative leader gap as a close leader, not a missing one.

Let v be ego speed, V the allowed speed (including the sampled speed factor),
r the TraCI gap (bumper gap minus ego minGap), u leader speed, and b the leader
acceleration from the previous step. The minGap offset cancels explicitly:
desired bumper gap = minGap + h*v, so spacing error e = r - h*v.

- Cruise request: a_cruise = k_c*(V-v).
- With a leader: a_follow = k_p*e + k_v*(u-v) + k_a*b.
- Use k_a only for a passenger leader; use zero for a human truck leader.
- a = clamp(min(a_cruise, a_follow), -D, A) with a leader; otherwise
  a = clamp(a_cruise, -D, A).
- Request `setSpeed(max(0, min(V, v + dt*a)))`.

Defaults: h = 1.5 s, k_c = 0.4 /s, k_p = 0.2 /s²,
k_v = 0.8 /s, k_a = 0.5, A = 2.6 m/s², D = 4.5 m/s²,
range = 250 m. Values must be finite; gains nonnegative; h >= baseline tau
and 0.5 s; A/D positive and no larger than frozen passenger accel/decel;
range positive; k_a in [0,1]. No parameter tuning after viewing comparison.

Maintain speedMode 31 (safe speed, acceleration/deceleration, right of way,
red lights, speed limits) and the native lane-change mode. SUMO may override a
request for safety; commanded and realized acceleration are different. Record
command count, cooperative/ACC/cruise/fallback counts, controlled vehicle count,
minimum queried bumper gap, and realized acceleration extrema. Diagnostics are
simulation observations, not safety certification or string-stability proof.
Always close the TraCI connection on success or failure. H0 keeps subprocess
execution; CACC uses the same SUMO flags through a dedicated TraCI connection.

## Comparison, measurement, provenance, and failures

Keep M4's measurement contract, failure retention, safe output validation,
seed spread and source hashes. Carry controller config into each resolved run
and report with a controller diagnostics file. The harness records policy
settings separately from frozen physical treatment. M3 input hashes and route
XML must match across scenarios and M4; the controller cannot rewrite them.
Run acceptance additionally requires commands and cooperative interactions,
no missing-state fallback, and controller diagnostics when a policy is enabled.
All health gates remain: no SUMO warnings, collisions, emergency braking,
teleports, missing measurements, or uncleared demand.

Add window departure count, scheduled-departure cohort count/completions and
mean departDelay (including unfinished insertion where reported), plus whole-run
mean/max departDelay and peak insertion backlog from summary output. These
complement actual-departure metrics and expose selection effects; do not mix
scheduled and actual cohorts. Null unavailable means rather than invent zero.
For each date, report paired CACC-minus-H0 differences for each seed, their mean,
sample SD, and percent of H0 mean when nonzero. Failed/incomplete pairs yield
null aggregates. Describe metric direction and tradeoffs without assuming CACC
must improve outcomes. Preserve M3's held-out fidelity caveat.

## Acceptance criteria

| ID | Required evidence |
| --- | --- |
| AC1 | Plan then specification committed before source changes. |
| AC2 | Hand-calculated law tests: equilibrium, free cruise, closing/braking, feedforward on/off, clipping, minGap convention, missing leader, parameter rejection. |
| AC3 | Actual SUMO small-network integration: passenger control, human-truck fallback, leader changes, finite bounded requests, retained safety/lane-change modes, clean clearing, and deterministic replay of numeric trip/diagnostic results. |
| AC4 | Harness checks: policy validation before simulation, mismatched physical treatments rejected, controller settings/provenance retained, explicit failure handling and paired summaries including null propagation. |
| AC5 | Full H0/CACC matrix: 6/6 runs clean and cleared, all metrics/diagnostics present, matched route/network/input hashes and fleet settings. Replay H0 against M4 exactly. |
| AC6 | Independent audit of saved trips/summary: departure cohorts, insertion delays/backlogs, paired metric arithmetic; report all outcomes and scientific limits without post-result tuning. |
| AC7 | Full regression suite, lint, diff review against spec, synchronized context/Obsidian, GitHub publication verified. |

## Primary references (checked 2026-10-16)

- TraCI leader distance excludes ego minGap; leaders follow current best lanes
  and can change after a lane change:
  https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html
- Speed requests remain subject to mode 31 safety and physical constraints;
  `setSpeed(-1)` returns native control:
  https://sumo.dlr.de/docs/TraCI/Change_Vehicle_State.html
- Parameterized subscriptions support leader queries:
  https://sumo.dlr.de/docs/TraCI/Object_Variable_Subscription.html
- Installed SUMO/TraCI 1.27.1 `_vehicle.py` and `domain.py` confirm subscribe
  parameters and gap semantics. The native CACC model is a separate policy:
  https://sumo.dlr.de/docs/Car-Following-Models/CACC.html
