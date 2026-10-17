# M6 centralized variable speed limit closeout

**Complete for the fixed centralized VSL comparison, 2026-10-17.**

Nine of nine runs accepted, each clearing 22,951 vehicles with zero SUMO warnings, collisions, teleports or final running/waiting/discarded vehicles. All 125 tests and lint pass. The independent audit verifies 270 raw metrics, 90 paired metrics, every VSL decision, matching exported fleets/schedules, and exact H0/CACC replay against M5. Every central run has nonzero actuation and restored native limits.

## Question and frozen intervention

Compare unchanged human-like H0, accepted supervised CACC, and one centralized
feedback lane-speed policy on the frozen US-101 northbound experiment. CENTRAL
is applied to human-like traffic independently of CACC. The [plan](m6-centralized-control-plan.md)
at f1550ca and [specification](m6-centralized-control-spec.md) at b50a22c preceded
runtime source 26a71d6. M5 merged during setup; an isolated worktree prevents
shared-checkout changes from disturbing the experiment.

Every 30 s, use the vehicle-timestep-weighted speed across nine lanes just
downstream of the existing 1007.33 m upstream buffer. Below 15 m/s, activate a
25 m/s target on all 14 buffer lane segments; above 20 m/s, release it. Preserve
mode at threshold equality/in the band, and release on empty observations.
Limit changes to 1 m/s per update and recover after 8100 s. Original lane
limits are restored before closing the runtime. Native following, maneuvers,
speed factors and safety constraints remain in force. The limits are ideal
simulated actuation, not guaranteed vehicle speeds or field compliance.

## Evidence and acceptance traceability

| Contract | Evidence | Status |
| --- | --- | --- |
| SC1 geography and native authority | Exact edge/lane resolution; 14 control and 9 observation lanes | Verified in probe and all three full runs |
| SC2 weighting, boundaries, timing, recovery | Hand calculations, injected runtime and real SUMO replay | Tests pass |
| SC3 validation, failure and restoration evidence | Invalid inputs, cleanup, engine mismatch and no-actuation gates | Tests pass |
| SC4 fair complete matrix | H0/CACC/CENTRAL, October 8, 2025, seeds 41-43 | 9/9 accepted; H0 and CACC exactly replay M5 |
| SC5 independent audit/publication | All 30 raw metrics, 3 paired comparisons, VSL ledger, context and Obsidian | 270 raw and 90 paired checks pass; publication synchronized |

All 125 tests pass without skips; lint passes. Negative harness cases prove
that zero commands, zero limited-lane exposure, failed restoration and wrong
runtime versions cannot qualify. The 3000 s seed-41 [preflight](../reports/m6/preflight_seed41.json)
completed with zero SUMO warnings but failed its actuation requirement: minimum
interval speed was 18.3452 m/s and the frozen trigger was not crossed. Preserve
this result; no trigger, geography or gain retuning followed it.

## Results

CENTRAL versus H0 changes mean all-exit throughput +0.36%, scheduled-cohort total time -0.98%, RMS acceleration +0.47%, and peak insertion backlog -1.63%.

Paired throughput change is +29.50 +/- 78.67 veh/h and scheduled total-time
change is -15.08 +/- 37.34 s (mean +/- sample SD). Both spreads exceed the
mean changes; these three seeds do not establish a consistent overall benefit.
Mean stopped vehicles also rises 0.79%, while peak insertion backlog falls
1.63%. Preserve these mixed tradeoffs rather than selecting a single proxy.
The first central activations occur at 3510, 3270 and 3300 s for seeds 41-43,
all after the 3000 s probe ended. The short-probe null and full-run actuation
are consistent; no settings changed between them.


The complete [result matrix](../reports/m6/README.md) reports all three policies
and paired seed spread. These results describe a fixed illustrative policy on
one calibration day; a positive numerical change does not establish a general
traffic benefit. Compare scheduled total time and insertion backlog alongside
on-road queues, since the intervention can relocate delay.


## Reproduce and audit

Local prerequisites are the project .venv with SUMO/libsumo 1.27.1, frozen M3
PeMS profiles/metadata, and the accepted M2 network. Never overwrite an existing
experiment directory. Copy configs/us101_m6_experiment.json, change only its
experiment_id for an exact treatment replay, then run from the checkout:

```sh
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim run-us101-experiment --config PATH_TO_NEW_CONFIG
.venv/bin/python scripts/audit_m6_results.py --config PATH_TO_NEW_CONFIG --report PATH_TO_NEW_REPORT --output reports/m6/replay_audit.json
.venv/bin/python scripts/summarize_m6_results.py --report PATH_TO_NEW_REPORT --audit reports/m6/replay_audit.json --output outputs/m6_replay_presentation
```

For the shipped experiment, the config is configs/us101_m6_experiment.json and
the report path is outputs/us101_corridor/m6/m6_h0_cacc_central_vsl_2025_10_08/report.json.
The independent auditor imports no production metric/controller functions. It
uses raw trips, summaries, trajectories and recorded interval totals; it does
not independently replay a live 0.5 s sensor feed. Compact M5 detector hashes
avoid duplicating the older generated detector summaries.

## Limits and next step

M3's held-out fit remains limited (combined speed MAE 14.90 mph; October 15
missed both targets). M5 engages on about 2% of passenger timesteps. This is
one calibration date and three seeds; seed SD is not total uncertainty or a
confidence interval. The VSL thresholds are illustrative, sensing is ideal,
and the inlet-adjacent geography can relocate queues into insertion backlog.
All-exit throughput is not mainline capacity, stopped counts are queue proxies,
temporal mean-speed variation is not wave stability, and acceleration squared
is not energy. No field safety, optimality or deployment claim follows.
Primary-source interpretation notes are saved in [M6 VSL methodology](../research/m6-vsl-methodology.md);
they support the general concept, not these numerical settings or a benefit claim.
M7 sensitivity and M8 final research packaging remain. M6 is accepted as a
reproducible comparison, not an optimized or field-validated control policy.

## Publication and raw evidence

Runtime source: 26a71d6; exact source and input hashes are in the report.
[PR #2](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/2)
merged into main at [ef8d20c](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/commit/ef8d20c196298de88509097c06e5a7c40782de3f) on 2026-10-17. Plan f1550ca and spec b50a22c precede implementation.
Raw native files remain under the ignored experiment directory in the attached
isolated worktree. Versioned results include the accepted report, full summary,
independent audit, figure and nonactivating preflight. Context and Obsidian
project/decision/research/result/handoff notes are synchronized.
