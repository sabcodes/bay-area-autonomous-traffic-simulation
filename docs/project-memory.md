# Project memory and handoff

**Updated:** 2026-10-12
**Repository:** `sabcodes/bay-area-autonomous-traffic-simulation`
**Local Obsidian vault:** `Auto-Car Traffic Research`

## Purpose and current position

This project compares human-like traffic with explainable autonomous-vehicle
coordination policies on a US-101 corridor. The
[experiment charter](experiment-charter.md) defines the research question and
fair-comparison rules. The [roadmap](project-roadmap.md) is the milestone source
of truth: **M0–M3 experiment work is complete. M3 has a held-out fidelity limit.**
M4 has a partial runnable multi-seed harness.

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
Stop after M3 closeout; do not start M4 without a new user instruction.
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
