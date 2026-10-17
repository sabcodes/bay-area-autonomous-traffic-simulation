# Project memory and handoff

**Updated:** 2026-10-16
**Repository:** `sabcodes/bay-area-autonomous-traffic-simulation`
**Local Obsidian vault:** `Auto-Car Traffic Research`

## Purpose and current position

This project compares human-like traffic with explainable autonomous-vehicle
coordination policies on a US-101 corridor. The
[experiment charter](experiment-charter.md) defines the research question and
fair-comparison rules. The [roadmap](project-roadmap.md) is the milestone source
of truth: **M0–M5 practical experiment work is complete. M3 retains its fidelity limit; M5 is a supervised comparison.**
M4 is complete; the [harness closeout](m4-experiment-harness-report.md) records
its acceptance evidence.

## M2 decision to preserve

M2 is complete at the project's practical accuracy standard. Both directed
US-101 through routes and all 40 adjacent branch junctions were reviewed.
Four branch movements carry fixed H0 demand and 36 do not. Mathilda NB and
Rengstorff SB lane-count defects were corrected in versioned network patches.
The Shoreline NB and CA-85 SB exits each take the two rightmost lanes while
four continue. Three importer warnings remain visible and are accepted as
documented modeling approximations; West Maude/SR-237 is outside the US-101
mainline acceptance area. This decision does not assert exact as-built paint,
PeMS loop wiring, or calibrated managed-lane demand.

The accepted generated network SHA-256 is
`13103c0b31d22dff15159b56e5ba03f0becd9594868c4cdfeac60497e86b9bc6`.
The exact public OSM input snapshot and its provenance are versioned in
`data/osm/`, alongside the correction patch in `network/us101_corridor/patches/`.
The 40 branch paths have passenger-legal connections and terminate without
graph-boundary, depth-limit, or cycle outcomes. H0 seeds 41, 42, and 43 each
completed 13,482 vehicles without route, teleport, collision,
emergency-braking, or SUMO warning entries. These are network/run checks,
not calibration claims.

Read the [M2 acceptance record](us101-m2-acceptance.md),
[40-row checklist](us101-ramp-review-checklist.md),
[warning decisions](us101-importer-warning-review.md), and
[network audit](us101-network-audit.md) before changing the network.

## M3 closeout and stopping point

M3 execution now uses `scripts/run_m3_baseline.py` and
`configs/us101_m3_experiment.json`. Twelve bounded calibration cases are saved in
`reports/m3/candidates_report.json`. The final selection is `buffer_exit_tau15`
(1.5 s headway, 4% truck proxy, 700/2,000 veh/h net-entry and 1,500 veh/h
net-exit group assumptions). The 1,007.33 m upstream buffer uses the unchanged
M2 network and station 400790's separately labeled 80%-coverage inlet proxy;
comparison targets retain 90% coverage. Final calibration and sensitivities
are complete: 15/15 calibration runs cleared cleanly, 8.32% flow MAPE and
8.15 mph speed MAE. The frozen scenario is
`configs/us101_human_baseline_m3_frozen.json`; `reports/m3/freeze.json` records
the pre-validation treatment and source hashes. All six held-out validation
runs cleared cleanly and matched the frozen treatment. Combined errors were
19.37% flow MAPE and 14.90 mph speed MAE: the speed target was missed.
October 15 missed both targets (29.95%, 21.50 mph); October 16 met both
(8.79%, 8.30 mph). The October 15 upstream bottleneck was not reproduced.
This closes the practical M3 experiment, not a successful field-validation
claim. See the [closeout record](m3-human-baseline-report.md) and
[results](../reports/m3/README.md). Do not tune against these held-out errors.
The [staged plan](m3-human-baseline-plan.md) records the exact resume point.
M4 was authorized by a new user instruction on October 16, 2026. Its
[plan](m4-experiment-harness-plan.md) and [spec](m4-experiment-harness-spec.md)
preceded implementation; M3 settings and validation results remain frozen.
The [demand ledger](m3-demand-ledger.md) distinguishes measured
flows, group estimates, and omitted movements. Public 2024 Caltrans annual
truck/ramp inputs and their hashes are saved in `data/caltrans/`.

The split GP/express allocation cases with longer headways produced
teleports and are rejected. The final representative-day full-lane mean
errors are 8.38% flow MAPE and 5.93 mph speed MAE. The earlier no-buffer
15-run calibration is preserved separately (7.67% flow, 12.51 mph speed).
These calibration figures are separate from held-out validation. The reserved
dates were October 15–16, 2025; choices were frozen before running them. PeMS speeds are never
commands. The old nine-date average includes two Saturdays and is diagnostic
only. Provisional lane mappings remain modeling choices, not field-wiring
proof. See the [sensor audit](us101-sensor-audit.md) and
[ramp detector audit](us101-ramp-audit.md).

## M4 closeout and resume point

The spec-driven M4 sequence is complete: plan, specification, implementation,
checks, and real-run acceptance. Run `PYTHONPATH=src .venv/bin/python -m
bay_area_traffic_sim run-us101-experiment` with
`configs/us101_m4_experiment.json`. This declares H0 on October 8, 2025, seeds
41–43, 1 s samples, and a 0.1 m/s stop threshold. The report includes windowed
exit throughput, actual-departure travel times through clearance, stopped-queue
proxies, temporal variability of domain mean speed, and acceleration smoothness.

All three runs cleared 22,951 vehicles without SUMO warnings. Their legacy trip
metrics match M3 exactly; route files and detector summaries are byte-identical.
All 67 tests and lint passed. The [closeout](m4-experiment-harness-report.md) and
[versioned evidence](../reports/m4/README.md) record the exact acceptance checks.
Runtime traces stay under `outputs/us101_corridor/m4/m4_h0_2025_10_08/`; existing
experiment directories are preserved, so repeat with a new experiment ID.

Queue proxies exclude temporary insertion backlogs, travel-time cohorts use
actual departures, temporal speed variability is not a wave-stability test,
and acceleration smoothness is not energy use. M3's held-out failure remains
unchanged. At the M4 checkpoint, M5–M8 remained. The later M5 closeout below is the current resume point.

## M5 closeout and current resume point, 2026-10-16

M5 is complete for the [supervised comparison](m5-cooperative-cacc-report.md).
The original plan/spec commits c276d1f/9fe5c69 preceded source. The final
[revision-4 spec](m5-supervised-cacc-spec.md) at 75d4ad4 preceded runtime source
643d0da. All six runs accepted and each cleared 22,951 vehicles without SUMO
warnings. All 102 tests passed; the independent audit checked six raw outputs,
30 paired metrics, every aggregate, matching exported fleets/schedules and
unchanged source/route/network/input hashes. All H0 metrics and detector
summaries exactly replay M4. See [versioned results](../reports/m5/README.md).

This is a low-engagement supervisor: retain frozen physical treatment and
original gains, yield to all native maneuver/cooperation flags, and engage only
after 2 s of quiet state. Active requests cover 1.99–2.06% of all-run passenger
timesteps. Throughput changes -0.30%, scheduled total time +0.68%, RMS
acceleration -0.80%. These mixed changes do not demonstrate a traffic benefit.
Continuous CACC remains unresolved. The rejected overlay matrix had 2/1/2
teleports; a native-CACC probe had 40 emergency-braking warnings. All failures
and their correctly suppressed aggregates are preserved under reports/m5/.

Reproduce with configs/us101_m5_experiment.json and a new experiment ID. Final
raw outputs are under outputs/us101_corridor/m5/m5_h0_supervised_cacc_2025_10_08/.
libsumo 1.27.1 is project-local; three workers isolate engine state. The accepted
package is published in [PR #1](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/1)
and was merged into main at `0a56d5afe54d9b04f0a6326ebec5977dabbec77f`
on 2026-10-17 at 07:28:49 UTC. The pre-merge publication commit is `70409b8`.
M6 centralized control is next. M3's failed held-out fit remains unchanged.

## Working rules

- Keep the repository documentation and versioned inputs authoritative for
  reproducibility. Obsidian is a navigable research notebook and handoff
  surface; link back to the relevant repository record when a finding changes.
- Rebuild the network and regenerate the branch ledger and routes after a
  topology change. Record the new network hash and rerun the relevant scenario.
- Preserve missing PeMS observations as missing, not zero.
- Compare later policies against H0 with the same network, demand window,
  vehicle mix, and seed set. Treat controller effects as unproven until M3
  calibration and separate-day evaluation are complete. M3's failed October 15
  fit remains a limitation of any later policy interpretation.

## Context synchronization

The M5 closeout, roadmap, README, and `CONTEXT.md` were synchronized on
2026-10-16. The matching Obsidian project area is
`Auto-Car Traffic Research/US-101 Traffic Simulation`; its project home,
milestones, source index, decisions, and M5 handoff point back to these
versioned records. GitHub's current branch remains the publication source of
truth; Obsidian publication checkpoints record the verified commit separately.


### M5 merge checkpoint

PR #1 was merged on explicit user request at 2026-10-17 07:28:49 UTC.
GitHub reported the PR mergeable with no configured status checks; the accepted
102-test and six-run evidence remains in the M5 closeout. Local main was
fast-forwarded to the merge commit. Obsidian publication records now distinguish
the historical PR checkpoint from the merged main state. M6 remains next.
