# M6 centralized variable speed limit closeout

Status as of 2026-10-17: implementation verified; full acceptance pending.

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
| SC1 geography and native authority | Exact edge/lane resolution; 14 control and 9 observation lanes | Verified in probe; final audit pending |
| SC2 weighting, boundaries, timing, recovery | Hand calculations, injected runtime and real SUMO replay | Tests pass |
| SC3 validation, failure and restoration evidence | Invalid inputs, cleanup, engine mismatch and no-actuation gates | Tests pass |
| SC4 fair complete matrix | H0/CACC/CENTRAL, October 8, 2025, seeds 41-43 | Running; H0 accepted and exactly replays M5 |
| SC5 independent audit/publication | All 30 raw metrics, 3 paired comparisons, VSL ledger, context and Obsidian | Final evidence pending |

All 125 tests pass without skips; lint passes. Negative harness cases prove
that zero commands, zero limited-lane exposure, failed restoration and wrong
runtime versions cannot qualify. The 3000 s seed-41 [preflight](../reports/m6/preflight_seed41.json)
completed with zero SUMO warnings but failed its actuation requirement: minimum
interval speed was 18.3452 m/s and the frozen trigger was not crossed. Preserve
this result; no trigger, geography or gain retuning followed it.

## Results

Pending the complete matrix and independent audit. A traffic benefit is not an
acceptance condition. Report the complete [result matrix](../reports/m6/README.md),
including scheduled-cohort total time, insertion delay/backlog and all proxy
metrics, with paired seed spread. An on-road queue reduction alone cannot show
an overall benefit if delay moves into vehicles waiting to enter.

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
M7 sensitivity and M8 final research packaging remain after M6 acceptance.
