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
- M1 is complete. District 4 Station 5-Minute and Station Metadata exports are
  available locally. The reproducible inventory contains 19 candidates: 13
  northbound mainline cross-sections inside the endpoint, five exclusions
  (beyond the endpoint or on collector roadways), and one conservative holdout
  (station 425545: PeMS marks it ML and the lane count matches the map, but the
  “rm-n-coll” name makes its full through-mainline coverage uncertain). The Caltrans Oregon
  Expressway exit is at county PM 52.17. Eight accepted stations have at least
  90% coverage on at least 12 of 13 selected dates; five (401997, 402376,
  402379, 404522, 425892) have no qualifying rows. Missing observations remain
  missing, never zero. The aggregate and station-level reports are saved as
  `outputs/pems_calibration/us101_corridor_final_morning_peak.json` and
  `outputs/pems_calibration/us101_corridor_m1_station_profiles.json`. The
  current M3 draft keeps its previously selected calibration subset separate
  from this full audited inventory. See the [sensor audit](us101-sensor-audit.md).
- M2 is complete for the versioned US-101 corridor network at the project's
  practical accuracy standard. Both through routes and all 40 adjacent branch
  junctions have been reviewed for movement location, ramp side, modeled lane
  count, passenger-legal links, and directed connectivity. Four side movements
  carry H0 demand; the other 36 are also reviewed but carry no H0 demand.
  The user's lane checks led to versioned corrections at Mathilda NB (one
  rightmost lane drops into a one-lane ramp that widens later) and Rengstorff
  SB (one entrance lane, a 21.52 m immediate-exit pocket, and five continuing
  lanes). Shoreline NB and CA-85 SB each send the two rightmost lanes off
  while four continue. The separate express connectors remain left-side
  movements. All 40 branch junctions have passenger-legal lane links and
  their traced paths terminate at a road endpoint; no contradictory ramp-side
  connection was found. The network was rebuilt from the saved OSM input
  with the versioned correction patch, its lane ledger regenerated, and H0
  seeds 41–43 completed 13,482 vehicles each without route, teleport,
  collision, emergency-braking, or SUMO warning entries. The three
  Shoreline/Mathilda importer warnings are retained as reviewed modeling
  approximations, not silently suppressed; West Maude/SR-237 lies outside
  US-101 mainline acceptance. Exact as-built paint, PeMS loop wiring, and
  managed-lane demand behavior are not certified by M2. See the
  [acceptance record](us101-m2-acceptance.md), [40-row checklist](us101-ramp-review-checklist.md),
  [warning review](us101-importer-warning-review.md), and
  [network audit](us101-network-audit.md).
- M3 is in progress under the [human-baseline execution plan](m3-human-baseline-plan.md).
  H0 has a runnable ramp-aware draft. Demand profiles now use complete dates
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
  The user's station-centered review identifies four Moffett through lanes and
  a short fifth weaving lane; compare the mainline total against the four
  through lanes and retain the five-lane version as a separate auxiliary-lane
  candidate. The baseline OSM/SUMO edge `617335302` still represents only four
  lanes. Neither residual is
  a standalone ramp count; audit
  intervening entrances and exits before assigning demand to any one ramp.
  PeMS station 402920 averages 140.3 vehicles/hour over those nine dates, but
  its metadata identifies a southbound SR-85 on-ramp. The nearest generated
  graph feature also feeds southbound CA-85 (~9.9 m from the detector location;
  the NB HOV connector is ~37.4 m away), so do not count this profile as NB
  US-101 demand. The earlier three-seed HOV mapping result (401507 flow
  4,836.7→4,980.3 veh/h; MAPE 32.94%→30.95%) is retained only as a
  counterfactual. A Playwright Google Maps view confirms the interchange area
  but not painted lanes. Check the NB SR-85 connector's detailed geometry if a
  later scenario adds demand to it.
- Thirteen ramp sensors were identified and five have qualifying October
  morning profiles. Four were visually and topologically audited: one measured
  Mathilda exit is split from upstream demand, and the Mathilda, Moffett, and
  San Antonio entries are injected. The reporting Embarcadero entry lies past
  the endpoint. Vehicle mix, eight missing-ramp estimates, driver calibration,
  and held-out validation are still required. See
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
