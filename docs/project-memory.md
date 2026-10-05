# Project memory and handoff

**Updated:** 2026-10-04
**Repository:** `sabcodes/bay-area-autonomous-traffic-simulation`
**Local Obsidian vault:** `Auto-Car Traffic Research`

## Purpose and current position

This project compares human-like traffic with explainable autonomous-vehicle
coordination policies on a US-101 corridor. The
[experiment charter](experiment-charter.md) defines the research question and
fair-comparison rules. The [roadmap](project-roadmap.md) is the milestone source
of truth: **M0, M1, and M2 are complete. M3 is the active scientific task.**
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

## Next work

M3 needs a calibrated vehicle mix, defensible treatment of missing ramp
demand, better downstream flow and speed fit, and validation on days separate
from calibration. The existing H0 draft runs, but Shoreline station 401507
still has about 33% flow MAPE and about 10.5 mph speed MAE. Provisional
detector-to-lane mappings at 401948, 401507, and 402377 are modeling choices,
not field-wiring proof. See the [sensor audit](us101-sensor-audit.md) and
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
  calibration and separate-day validation are complete.
