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
  ten mainline locations are provisionally accepted, eight need follow-up, and
  one Shoreline collector detector is excluded.
- M2 is active. The imported network now reaches the Oregon Expressway/Page
  Mill connection. The H0 route is constrained through detector-matched
  mainline checkpoints and never falls below four lanes.
- M3 has a runnable ramp-aware draft. Seeds 41, 42, and 43 each completed
  12,457 vehicles without SUMO route, teleport, or emergency-braking warnings.
  Mean trip speed is 59.59 mph with a 0.16 mph sample standard deviation, so
  the remaining speed bias is systematic rather than seed noise. Ten
  PeMS-aligned virtual stations report 43 lane loops in five-minute intervals.
  At the entry station, simulated mean flow is 4,656.5 vehicles/hour versus
  4,645.9 observed, with mean interval MAPE of 0.38%. Across the six comparable
  stations, mean flow MAPE ranges from 0.38% to 32.11%, and mean speed MAE from
  7.06 to 13.59 mph.
- Observed flow conservation is now explicit. Seven reporting stations are
  placed in route order and six adjacent residuals are calculated. Three are
  usable. One same-edge pair is classified as detector disagreement rather
  than demand, and two segments are quarantined because PeMS station 401948
  reports five lanes while mapped OSM/SUMO edge `617335302` has four. Those
  final segments contain mean changes of +330 and +1,529 vehicles/hour, so
  resolving this network/data discrepancy is the next M2/M3 task before
  missing flow is injected.
- Thirteen ramp sensors were identified and five have qualifying October
  morning profiles. Four were visually and topologically audited: one measured
  Mathilda exit is split from upstream demand, and the Mathilda, Moffett, and
  San Antonio entries are injected. The reporting Embarcadero entry lies past
  the endpoint. Vehicle mix, eight missing-ramp estimates, driver calibration,
  remaining network review, and held-out validation are still required. See
  the [ramp detector audit](us101-ramp-audit.md).
- M4 is active. One command now runs the real baseline across multiple seeds
  and writes per-run results plus sample mean and standard deviation for trip
  metrics and station calibration errors. Queue, stability, and smoothness
  metrics still need to be added before M4 is complete.

## Guardrails

- Do not add per-vehicle MAPPO until the M3 baseline and the rule-based M5/M6
  comparisons are validated.
- Do not use all-pairs vehicle-neighbor scans; use SUMO context subscriptions
  or leader/follower queries.
- Label acceleration-squared as a smoothness measure, not energy use, unless a
  validated energy model is added.
- Treat ideal V2V communication, short headways, and full AV penetration as
  explicit sensitivity assumptions.
