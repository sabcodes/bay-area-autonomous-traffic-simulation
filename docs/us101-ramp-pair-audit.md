# US-101 NB ramp and detector audit: Moffett to Shoreline

## Purpose and conclusion

This note audits the likely entrances and exits between the two mainline
station pairs with net flow increases of about **+330 veh/h** (401534→401948)
and **+1,529 veh/h** (401948→401507). A net increase between detectors is not
the count of any one ramp: it combines every entry, every exit, time/space
variation, and detector error in the interval.

The ramp map supports the idea that real vehicles enter in both intervals,
but does not yet reconcile either residual. The first interval has a measured
Moffett on-ramp of about 136 veh/h plus other possible movements. In the second,
the SUMO graph shows a one-lane HOV-designated connector joining the freeway,
and Caltrans identifies Shoreline loop/diagonal NB on-ramps; however, the
connector's SUMO topology does not agree with its geometry in the checked OSM
snapshot, and no current ramp flow profile is available for these entries.
Keep both values as **net mainline changes**, not ramp-demand targets.

## Evidence base

- PeMS station positions, types, and labels below come from the October 16,
  2025 metadata snapshot ([metadata](../data/pems/metadata/d04_text_meta_2025_10_16.txt));
  station-average flows come from the generated
  [mainline profiles](../outputs/pems_calibration/us101_mainline_station_profiles.json)
  and [flow-balance report](../outputs/pems_calibration/us101_flow_balance.json).
- The currently scanned ramp-detector inventory is
  [configs/us101_ramp_station_ids.json](../configs/us101_ramp_station_ids.json);
  its October profile is
  [us101_ramp_station_profiles.json](../outputs/pems_calibration/us101_ramp_station_profiles.json).
- Roadway tags and ways are from the local
  [OSM extract](../data/osm/us101_corridor.osm.xml), downloaded from Overpass
  on September 22, 2026 ([query and provenance](../data/osm/us101_corridor.osm.provenance.json)).
  Connectivity and virtual-loop placement are from the generated
  [SUMO network](../outputs/us101_corridor/us101_corridor.net.xml) and
  [seed-42 detector definitions](../outputs/us101_corridor/h0_virtual_detectors_seed_42.add.xml).
- Caltrans confirms NB US-101 metered entrance locations including Moffett,
  SR-85, and Shoreline (loop and diagonal) in its
  [NB US-101 ramp-meter announcement](https://dot.ca.gov/caltrans-near-me/district-4/d4-news/2021-06-04-on-ramp-meters-to-be-activated-on-northbound-interstate-101).
  Caltrans' [2024 US-101 exit-number table](https://dot.ca.gov/-/media/dot-media/programs/safety-programs/documents/exit/202412-calnexus-us-101-a11y.pdf)
  places NB Shoreline at county PM 48.60 and Old Middlefield Way at PM 48.97.
  VTA's [US 101/SR-85 interchange project record](https://www.vta.org/media/13276)
  documents the NB SR-85→NB US-101 HOV direct connector.

## Segment A: 401534→401948, about +330 veh/h

PeMS reports station 401534 at PM 47.83, four lanes, mean 4,756 veh/h; station
401948 at PM 48.21, five lanes, mean 5,086 veh/h. The station-flow difference
is +330 veh/h. In the simulation audit these map to edges `850032296` (4 lanes)
and `617335302` (4 represented lanes; PeMS reports 5 at 401948). The latter
lane mismatch remains a simulation-network gap even though the PeMS screenshot
and active lane measurements support using station 401948 as an observed
mainline cross-section.

| Candidate movement | PeMS / source evidence | Direction and interval assessment | Current status |
| --- | --- | --- | --- |
| Moffett Boulevard loop on-ramp | PeMS 402919 is `OR`, “Moffett Blvd on loop,” PM 47.78. Mean measured profile is 11.30 vehicles/5 min = **135.6 veh/h** across 12 days. | The named loop is a plausible NB entrance at the Moffett interchange, but its PeMS PM is just upstream of station 401534's PM and its detector coordinate is shared with the Moffett off-diagonal record. The ramp's merge, not its detector postmile, decides which cross-section interval receives it. | Visually/graph-audited and modeled on edge `847214392#0`, merging at `1047818462`, per [ramp audit](us101-ramp-audit.md) and [baseline config](../configs/us101_human_baseline.json). The observed amount alone is smaller than +330. |
| Moffett Boulevard diagonal off-ramp | PeMS 402917 is `FR`, “Moffett Blvd off diag,” PM 47.78. | Plausible NB exit to Moffett/NASA area if it branches from the NB carriageway. PeMS labels it NB, but no ramp profile is listed for this ID; detector position is shared with 402919, so confirm the physical ramp assignment before treating it as a paired count. | Not in the current ramp-profile station-ID list; not modeled. No measured exit quantity available in the current report. |
| SR-85 diagonal connector to NB US-101 | Caltrans lists an “SR-85 Diagonal Connector On-ramp”; VTA documents the NB SR-85→NB US-101 HOV direct connector. The local SUMO graph has HOV connector edge `11479095`. | Potentially a material NB entry in the Moffett/85 weaving area. Whether its actual merge is between these exact two PeMS cross-sections needs verification against the roadway geometry; the local OSM/net inconsistency discussed below prevents assigning its flow to this interval yet. | Not included in current PeMS ramp detector scan or H0 demand. Not visually audited as a ramp mapping. |

**Assessment:** A net +330 is physically plausible if entries across the interval
exceed the off-ramp flow by about that amount, but the confirmed 136 veh/h
Moffett loop profile does not by itself explain it. An unmeasured SR-85
connector, the unprofiled off-ramp, detector mismatch, and the five-vs-four
lane model gap are all relevant. Do not set a 330 veh/h ramp flow from this
residual.

## Segment B: 401948→401507, about +1,529 veh/h

PeMS reports station 401948 at PM 48.21, five lanes, mean 5,086 veh/h; station
401507 at PM 48.69, six lanes, mean 6,615 veh/h. The reported net change is
+1,529 veh/h. Caltrans identifies Shoreline NB loop and diagonal on-ramps; its
exit table places the NB Shoreline exit at PM 48.60, between those PeMS
postmiles. That makes this an interval with both likely entering and exiting
traffic—not a single on-ramp count.

| Candidate movement | PeMS / source evidence | Direction and interval assessment | Current status |
| --- | --- | --- | --- |
| Shoreline Boulevard loop on-ramp | Caltrans lists “Shoreline Blvd Collector (Loop and Diagonal) On-ramp.” PeMS ID 402922 is labeled `OR`, “Shoreline Blvd on loop,” but metadata gives direction `S`, PM 48.17, and the same coordinate as another Shoreline record. | Officially documented NB entry exists at the interchange. The PeMS row's direction/postmile/coordinate do not line up cleanly with the 401948→401507 PM interval; do not use it as an NB ramp count without checking its detector map/configuration. | Not in current ramp profile scan and not modeled. |
| Shoreline Boulevard diagonal/collector on-ramp | Caltrans lists the diagonal as well as loop entrance; the checked October PeMS metadata has no corresponding candidate row in the project's current ramp-ID list. | Candidate NB inflow likely lies in the Shoreline interchange area, but a lane-specific PeMS station and precise merge point were not identified in the current inventory. | Not mapped, profiled, or modeled. |
| Shoreline Boulevard off-ramp | PeMS 402921 is `FR`, “Shoreline Blvd off,” with direction `S`, PM 48.17, and the same coordinate as 402922. Caltrans' exit table lists NB Shoreline at county PM 48.60. | The NB exit is documented and its official postmile falls between the two mainline stations. The PeMS detector metadata is inconsistent with that location/direction, so the ID cannot currently quantify the exiting flow. | Not in current ramp profile scan and not modeled. |
| HOV direct connector into NB US-101 | SUMO edge `11479095` is one lane, HOV-designated in the local network, and has a connection to mainline edge `509747406`; VTA confirms the NB SR-85→NB US-101 direct connector exists. | If that SUMO connection is the actual connector merge, it adds traffic between 401948 and 401507 and could help explain a positive difference. But it has no measured flow profile, and its placement is not reconciled with the local OSM snapshot: OSM way `11479095` terminates at node `689349785` (37.408020, −122.070052), while the SUMO connection is at junction `447918140` (37.411823, −122.077327). Treat the merge interval as unverified until the network build/source version is checked. | Present in the SUMO graph but absent from the ramp demand inventory and H0 flows; mapping needs source/topology audit. |
| Old Middlefield Way off-ramp | Caltrans exit table lists NB Old Middlefield Way at county PM 48.97; local SUMO connects mainline lane 0 to way `30990690` at the end of synthetic edge `509747406-AddedOffRampEdge`. | Official PM places this exit after station 401507 (PM 48.69), so it should not reduce the flow measured there. The SUMO detector placement is close to this split: all six virtual loops are on lanes 1–6 at position 70.24 m of a 94.71 m through edge; the ramp branches from lane 0 at the edge end. Thus the loops are on through lanes before the modeled exit, not on the exit lane, but only about 24.5 m upstream of the split. This deserves visual/geometric review. | Exit exists in the network; the detector is not on its exit-only lane. The network geometry/postmile agreement still needs review. |

The `401507` generated virtual loops use
`509747406-AddedOffRampEdge_1` through `_6`; lane 0 is the Old Middlefield
exit branch. The edge has seven lanes because the network represents an
additional diverge/through transition, although PeMS reports six mainline
lanes. This is not evidence that the PeMS station counts ramp vehicles, but
the short distance from detector to split makes it a sensitive mapping.

**Assessment:** The +1,529 veh/h difference is plausible as a net outcome of
one or more substantial entries, minus the Shoreline exit, but no current
station data validates gross entry/exit volumes. The SUMO HOV connector is a
candidate, not a confirmed explanation; Shoreline on/off detector identities
also need manual reconciliation. Keep the residual flagged as a net mainline
change.

## Next checks before assigning ramp demand

1. Compare the exact OSM extract used to build `us101_corridor.net.xml` with
   the current provenance snapshot; resolve the `11479095` endpoint/merge
   mismatch before relying on that connector topology.
2. Visually audit the physical NB Shoreline loop/diagonal on-ramps and NB
   Shoreline exit in the SUMO GUI, including connections and lane counts.
3. Resolve the metadata/map identity for PeMS 402921/402922 and determine
   whether those IDs are current, correctly directed detectors for the NB
   entrance/exit.
4. Reconcile PeMS postmile with the 401507 sensor position relative to the
   Old Middlefield exit split.
5. Only then compare measured ramp totals against time-aligned mainline
   residuals; retain detector uncertainty and per-day spread.
