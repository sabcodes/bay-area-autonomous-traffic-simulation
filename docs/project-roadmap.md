# Project roadmap

## Definition of done

This project is complete when someone can reproduce a local, evidence-backed
comparison of human-like traffic, deterministic cooperative following, and one
centralized traffic-control policy on the audited US-101 northbound corridor
from SR-237 to the Oregon Expressway/Page Mill Road connection. The result must
report uncertainty, assumptions,
and limitations. It is not a real-vehicle controller or a deployment claim.

## Milestones

| ID | Milestone | Work | Evidence to finish |
| --- | --- | --- | --- |
| M0 | Local foundation | Project-local Python environment, SUMO installation, toy corridor, tests, and basic multi-seed reporting. | Runnable commands and passing tests. |
| M1 | Observed-data foundation | Obtain PeMS Station 5-Minute and Station Metadata exports; retain only detector stations inside the named corridor; document selected days and missing observations. | Reproducible detector list and saved data-summary report. |
| M2 | Network audit | Inspect OSM-derived US-101 geometry, lanes, ramps, merges, exits, and legal movements; manually correct any defects. | Completed audit checklist and versioned corrected network. |
| M3 | Human-like baseline | Build demand, routes, vehicle mix, and driver behavior; tune them against held-out observed speed and flow. | Calibration report and separate-day validation report. |
| M4 | Experiment harness | Make scenario settings explicit; run repeated seeds; produce throughput, travel time, queue, speed-stability, and smoothness results. | One command creates a comparable multi-seed report. |
| M5 | Cooperative CACC | Add a deterministic cooperative-following policy using SUMO leader/follower or context queries. Check safety-related simulation warnings before using results. | Human versus CACC comparison under matching assumptions. |
| M6 | Centralized control | Add one explainable intervention, such as ramp metering or a speed advisory, then compare it fairly with M3 and M5. | Human, CACC, and central-control result matrix. |
| M7 | Sensitivity and uncertainty | Vary demand, AV penetration, communication assumptions, controller settings, and random seeds. | Plots/tables showing spread and failure cases. |
| M8 | Research package | Write methods, results, caveats, sources, commands, and a plain-language conclusion. | A reproducible final report. |

## Current position

- M0 is complete.
- M1 is active. District 4 Station 5-Minute and Station Metadata exports are
  available locally. The corrected boundary selects 19 candidate detectors;
  nine are in the provisional reviewed subset and ten need follow-up.
- M2 is active. The imported network now reaches the Oregon Expressway/Page
  Mill connection. The H0 route is constrained through detector-matched
  mainline checkpoints and never falls below four lanes.
- M3 has a runnable draft. Seed 42 completed 11,372 vehicles without teleport
  warnings, but its 59.7 mph average trip speed is substantially above the
  provisional 48.7 mph observed detector target. Nine PeMS-aligned virtual
  stations now report 40 lane loops in five-minute intervals. Six reporting
  stations have direct flow/speed comparisons: flow error ranges from 3.8% to
  22.9%, and speed error ranges from 6.3 to 12.4 mph.
- Ramp-demand preparation is active. Thirteen ramp sensors were identified;
  five have qualifying October morning profiles. Injection remains gated on
  the [ramp detector audit](us101-ramp-audit.md). Vehicle mix, missing-ramp
  estimation, network corrections, and held-out validation are still required.

## Guardrails

- Do not add per-vehicle MAPPO until the M3 baseline and the rule-based M5/M6
  comparisons are validated.
- Do not use all-pairs vehicle-neighbor scans; use SUMO context subscriptions
  or leader/follower queries.
- Label acceleration-squared as a smoothness measure, not energy use, unless a
  validated energy model is added.
- Treat ideal V2V communication, short headways, and full AV penetration as
  explicit sensitivity assumptions.
