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
- M3 has a runnable ramp-aware draft. Demand profiles now use complete dates
  shared across the mainline entry and every active ramp, and the validation
  profile uses those same dates. On the current nine-day set, three seeds each
  completed 13,482 vehicles without route, teleport, collision, or
  emergency-braking warnings. Mean trip speed is 59.10 mph (sample SD 0.18).
  Across six comparable mainline stations, flow MAPE ranges from 0.31% to
  32.94% and speed MAE from 10.50 to 17.86 mph, so speed and downstream flow
  calibration remain active.
- Observed flow conservation is now explicit. Seven reporting stations are
  placed in route order and six adjacent residuals are calculated. Five are
  usable; one same-edge pair is classified as detector disagreement rather
  than demand. Station 401948 is accepted as a five-lane PeMS cross-section:
  its five lane measurements are active, its location is on northbound US-101,
  and Caltrans documents the managed/HOT lane buffered between Moffett
  Boulevard and Old Middlefield Way. Same-date comparisons replace the earlier
  unmatched-day values: +238 and +1,622 vehicles/hour across 12 days and 288
  morning intervals for the Moffett and Shoreline pairs. On the nine complete
  dates shared by all H0 demand sources, the Shoreline pair is +1,785 veh/h.
  The mapped OSM/SUMO
  edge `617335302` still represents only four lanes, so that model geometry gap
  remains visible as a note. Neither residual is a standalone ramp count; audit
  intervening entrances and exits before assigning demand to any one ramp.
  PeMS station 402920 averages 140.3 vehicles/hour over those nine dates. A
  close-up user-provided PeMS map and a valid SUMO route visually/topologically
  support its location on the SR-85-to-NB-101 connector. A separate three-seed
  sensitivity moves simulated flow at 401507 from 4,836.7 to 4,980.3 veh/h and
  reduces flow MAPE from 32.94% to 30.95%; this is not a controller benefit or
  final ramp-demand acceptance. The two PeMS lanes versus one SUMO lane and
  exact merge direction remain caveats.
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
