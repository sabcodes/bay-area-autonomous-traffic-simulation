# M3: human-like US-101 baseline plan

**Started:** 2026-10-05

**Status:** Complete at the practical experiment standard; held-out fidelity target missed

**Last updated:** 2026-10-12

## Stage checklist and resume point

| Stage | Status | Deliverable / evidence |
| --- | --- | --- |
| M3.1 — Inputs and date split | Complete | Five calibration weekdays, two reserved validation weekdays; explicit dates in H0; source hashes; Saturdays excluded |
| M3.2 — Demand and routes | Complete | Measured ramps, three net-movement group assumptions, 80%-coverage inlet proxy, and every NB branch disposition in [the demand ledger](m3-demand-ledger.md) |
| M3.3 — Vehicle mix | Complete | 4% annual truck proxy, physical type attributes, and 2%/6% sensitivity cases; public Caltrans snapshots in `data/caltrans/` |
| M3.4 — Human calibration and alignment | Complete | Twelve recorded candidates; 15/15 final runs clean and cleared; 8.32% flow MAPE / 8.15 mph speed MAE; all five 402377 lane outputs and dual four-lane audit |
| M3.5 — Freeze and separate-day validation | Complete | 6/6 clean runs; frozen treatment unchanged; October 15 missed both fidelity targets, October 16 met both; combined 19.37% flow / 14.90 mph speed |
| M3.6 — Report and handoff | Complete | Final tables/figures and versioned five-minute series; acceptance decision and limits; repository/context/Obsidian handoff |

**Resume here: stop. M3 is closed.** Final case `buffer_exit_tau15` is frozen in
`configs/us101_m3_experiment.json` and
`configs/us101_human_baseline_m3_frozen.json`. Five-day calibration is complete:
15/15 clean runs, mean flow MAPE 8.32%, speed MAE 8.15 mph. Sensitivities are
complete; the high-demand case has an uncleared queue and stays a limitation.
Validation is complete under `outputs/us101_corridor/m3/experiment/validation/`.
`reports/m3/validation_report.json` matches the frozen treatment hash. All six
runs cleared cleanly, but the combined speed target was missed: 14.90 mph MAE.
The [closeout record](m3-human-baseline-report.md) records the failed October 15
fit. Do not repeat completed runs or tune against validation errors. Results,
figures, timing rows, and context handoff are saved. Starting M4 requires a new
user instruction; this task performs no M4 implementation or policy runs.

The original no-buffer `tau15` model completed all 15 calibration runs cleanly;
its preserved report is `reports/m3/calibration_no_buffer_report.json` (mean
flow MAPE 7.67%, speed MAE 12.51 mph). The final inlet-buffer case adds an
explicitly assumed 1,500 veh/h downstream net-exit group. All 12 bounded
candidate results remain in `reports/m3/candidates_report.json`; the original
search configuration is `configs/us101_m3_calibration_search.json`.

**Stop after M3.6. Do not start M4 or later experiments in this task.**

## Experiment contract

- Fixed analysis corridor and network: the accepted M2 US-101 NB network. An
  inlet buffer, if selected, uses existing upstream motorway edges and does
  not change the scored analysis reach.
- Primary observations: 07:00–09:00, five-minute speed/flow, at least 90%
  reported coverage. A separately labeled 80%-coverage upstream count may
  condition the inlet; it is never a scored target.
- Fixed split below; representative October 8 was selected by median
  study-start flow before candidate fitting. Validation errors never select
  parameters or exclude poor-fit days.
- Up to 12 recorded calibration candidates; preserve failed cases. Three
  fixed seeds per day for the final calibration/validation.
- Zero unexplained SUMO route/collision/teleport/emergency-braking warnings,
  and every loaded trip inserted and ended within the documented clearance
  horizon, are run-health requirements.
- Report station errors, bottleneck/timing mismatch, seed variation, omitted
  movements, and detector-subset uncertainty. Performance targets are mean
  flow MAPE at or below 20% and speed MAE at or below 10 mph on the full-lane
  stations; report each held-out day against those targets. A miss is recorded
  as a model limitation and is not a reason to tune on validation data or to
  claim successful field validation.
- Completion evidence: reproducible frozen scenario, calibration report,
  separate-day validation report, sensitivity/health ledger, and updated
  research context. The closeout must state whether fidelity targets were met.

**Scope:** Northbound US-101, SR-237 to the Oregon Expressway/Page Mill Road connection, 07:00–09:00 observed morning period.

## Starting point

M2's corrected network is the fixed geometry for M3. H0 already has an upstream PeMS flow profile, the measured Mathilda exit, three measured northbound entrances, five explicit routes, virtual mainline detectors, and three-seed reports. It has one passenger-car type and uncalibrated Krauss/default lane-change behavior. The present nine-date average mixes weekdays with Saturdays, so it is a diagnostic draft, **not** calibration or independent validation. At station 401507 (Shoreline), the draft's mean flow MAPE is 32.96% and speed MAE is 10.45 mph; other comparable station speed MAEs are roughly 10.5–17.9 mph. See `outputs/us101_corridor/h0_multiseed_report.json` and `docs/project-roadmap.md`.

## Fixed observation split

The nine dates complete across the current mainline entry and four active ramp sensors are 2025-10-07, 08, 09, 10, 11, 14, 15, 16, and 18. October 11 and 18 are Saturdays and are excluded from this **weekday morning** experiment, not treated as zero demand.

| Use | Dates | Rule |
| --- | --- | --- |
| Calibration | 2025-10-07, 08, 09, 10, 14 | Fit demand assumptions, vehicle mix, and human behavior only here. |
| Validation | 2025-10-15, 16 | Freeze choices before running either day; report each day separately and the combined result. |

Choose any representative calibration day from the five by a documented median-flow/coverage rule, rather than by its simulated fit. Check incident and detector-quality evidence if available; record any unavoidable unknowns. Do not replace missing five-minute observations with zero. If a validation date proves unusable for a documented data-quality reason, record the exclusion before looking at simulation error and select another previously untouched weekday if one exists. Never move a poor-fit day into calibration to improve the score.

## Execution order and deliverables

1. **Separate days in the H0 runner.** Add explicit date selection to profile preparation and detector comparison. Preserve the current nine-date draft as an archived reference. Produce one manifest per calibration/validation day or group with source dates, network hash, selected PeMS files, config, seed, and output paths. The present runner automatically intersects complete dates and averages them; this must change before fitting. First deliverable: a date-split inventory and reproducible per-day H0 commands.
2. **Close the demand ledger.** Map each in-boundary on/off movement to an audited M2 edge. Keep measured ramp profiles at their real locations. For missing ramp observations, use mainline conservation only where detector pairs are comparable, and bound remaining flows using documented nearby counts or demand information. Treat a residual as a *net* change, never a count for one ramp. Exclude movements outside the analysis endpoint. Save a table of measured, estimated, and unknown flows plus low/base/high demand cases. Do not manufacture point estimates from missing PeMS rows.
3. **Add a documented vehicle mix.** Use an available local classification source if it covers the study dates/corridor; otherwise declare a bounded passenger/heavy-vehicle mix and run sensitivity cases. Record class shares, lengths, speed factors, acceleration/braking settings, and provenance. Keep the current passenger-only case as a comparison.
4. **Diagnose before tuning.** Compare 5-minute observed and virtual-detector flow and speed by station and date, including lane-alignment choices documented in M2. Plot the space-time speed pattern and check whether congestion onset and bottleneck position are reproduced. Check upstream insertion, route exits, warmup, and unserved demand. Fix demand/route accounting before changing driver parameters. PeMS speed is an outcome, not a SUMO speed command.
5. **Calibrate a small human model.** On calibration dates only, tune bounded headway/imperfection, desired-speed spread, and selected lane-change parameters in a recorded sequence. Keep geometry fixed unless a clear M2 defect is discovered and logged. Use a bounded search (initially no more than 12 candidate settings); retain every candidate's config and report. Prefer the simplest candidate that improves flow and speed profiles without creating teleports, collisions, emergency-braking warnings, or large unserved queues.
6. **Freeze and validate.** Freeze network, demand-estimation method, class mix, behavior parameters, analysis window, and seeds. Run the two untouched weekdays separately with at least three fixed seeds each. Publish station-by-station five-minute flow and speed errors, observed versus modeled congestion timing, trip/clearance results, warnings, and seed spread. State where the model still fails. Use the same frozen H0 assumptions when M5/M6 comparisons begin.

## Practical M3 completion rule

M3 is complete when a versioned calibration report and **separate-day** validation report can be reproduced from saved commands and inputs, all relevant in-boundary ramps are represented or explicitly bounded, vehicle mix and human parameters are documented, and simulation health is reported. The report must show whether the baseline materially improves the current 32.96% Shoreline flow MAPE and 10.5–17.9 mph speed MAE and whether its bottleneck pattern resembles observed data. Do not claim the model is field-validated where it misses; label those stations and carry the limitations into later policy comparisons. This is a credible local experiment gate, not a claim of field wiring or laboratory precision.

## First execution record

The date-selection option and three separate M3 scenario configs are versioned in
`src/bay_area_traffic_sim/real_corridor.py` and `configs/`. The first
calibration preparation selected **only** the five declared calibration dates;
the aligned observed profile lists five dates for each of seven reporting
stations. The seed-42 draft then completed 15,080 vehicles with no SUMO
warning, teleport, collision, or emergency-braking line in its log. Its
Shoreline 401507 flow MAPE is **33.00%** and speed MAE is **13.22 mph**; across
the six comparable stations, speed MAE spans **13.22–21.77 mph**. This is a
diagnostic result, not a tuned or validated baseline. Outputs are in
`outputs/us101_corridor/m3/calibration/`.

Run from the repository source so an older installed package cannot ignore
the new date-selection setting:

```bash
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim prepare-us101-human-baseline \
  --config configs/us101_human_baseline_m3_calibration.json
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim run-us101-human-baseline \
  --config configs/us101_human_baseline_m3_calibration.json --seed 42
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim compare-us101-detectors \
  --observed outputs/us101_corridor/m3/calibration/observed.json \
  --simulated outputs/us101_corridor/m3/calibration/detectors_seed_42.json \
  --output outputs/us101_corridor/m3/calibration/comparison_seed_42.json
```

The early held-out configs `configs/us101_human_baseline_m3_validation_2025_10_15.json`
and `configs/us101_human_baseline_m3_validation_2025_10_16.json` are retained as
historical setup. The final validation uses `configs/us101_m3_experiment.json`
and `configs/us101_human_baseline_m3_frozen.json` through
`scripts/run_m3_baseline.py`; the early configs do not contain the selected model.

## Historical first action

The first implementation action was to build the demand ledger and diagnose
the Shoreline flow gap and speed bias before adding fleet and behavior cases.
The stage checklist above is the current resume point. The nine-date average
remains a diagnostic reference, never a validation target.

## References

- [Roadmap](project-roadmap.md), [project memory](project-memory.md), [experiment charter](experiment-charter.md)
- [PeMS sensor audit](us101-sensor-audit.md), [ramp detector audit](us101-ramp-audit.md), [M2 acceptance](us101-m2-acceptance.md)
- [Baseline methodology](../research/human-baseline-methodology.md) and [research-method comparison](research-lab-methods.md)
