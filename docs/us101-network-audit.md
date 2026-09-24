# US-101 network audit record

## Source and reproducible import

The current draft network is built from
`data/osm/us101_corridor.osm.xml`. Its adjacent provenance file records the
Overpass query, boundary, and retrieval time (`2026-09-22T07:08:48Z`). Rebuild
with:

```bash
.venv/bin/python -m bay_area_traffic_sim import-us101-osm
```

The imported SUMO network is in `outputs/us101_corridor/` and is ignored by
Git. A repeat import using the recorded `netconvert` options completed with
exit code 0. It emitted 84 warning records for the broad OSM extract; warnings
outside the study freeway and ramps are not automatically defects. Relevant
motorway-link warnings and their follow-up decisions are listed below.

## Automated topology checks

The configured northbound route from station 402370 to the Oregon Expressway
endpoint contains 37 edges. All 37 edge IDs exist in the generated network,
all 36 adjacent pairs connect node-to-node, and each of the 13 ordered
checkpoint pairs has a route. The route traverses motorway and motorway-link
edges; its generated edges have modeled limits of 65 mph on freeway segments
and about 49.7 mph on link segments.

The reverse southbound route between corresponding mainline edges near
stations 402379 and 402370 is also connected (41 edges, all motorway or
motorway-link). This is a graph-connectivity check, not a lane-by-lane visual
inspection of the southbound facility.

All five saved H0 routes (mainline, three on-ramps, and one off-ramp) were
checked: every edge exists and every adjacent pair connects. The three-seed H0
simulation previously completed all 13,482 vehicles per seed without route,
teleport, collision, or emergency-braking warnings. This validates those
specific routes, not every ramp in the imported network.

## Relevant importer warnings

| OSM edge / location | Import warning | Current interpretation |
| --- | --- | --- |
| `396010342`, near the Oregon Expressway end of the extract | OSM `placement=transition` is unsupported; no matching edge appears in the generated network. | The edge is just north of the selected route endpoint, but its relation to the Oregon Expressway interchange should be visually checked before treating it as irrelevant. |
| `348360455`, near the Shoreline interchange | Sharp turn radius of 7.99 m at the edge end. | It is a two-lane motorway link about 65 m from the northbound mainline route. Check ramp curvature and its connection in SUMO. |
| `690599564#0`, near the Shoreline interchange | A junction cluster is reduced because of parallel outgoing movements. | It is about 91 m from the mainline route. Confirm the resulting split/merge movement visually. |
| `941192341`, San Antonio/Mathilda-area approach | SUMO does not join a junction cluster because of parallel incoming movements. | It is a two-lane motorway link about 255 m from the mainline route. Confirm whether this is an intended separate ramp movement. |
| `19146053#0`, near the SR-237 interchange | A minor green connection exceeds 19.44 m/s; SUMO warns a turn lane may be missing. | It is outside the modeled through-mainline route but near the SR-237 interchange. Check whether the movement is in scope and whether its lane connection is plausible. |

Other logged warnings include unsupported cycleway compounds, minor-street
turn geometry, and signal programs elsewhere in the broad bounding box. They
were not associated with the audited US-101 through-route edges in this pass.
The full captured log was temporary and is not a tracked artifact; regenerate
it by running the import command with output redirected to a separate log.

## Known geometry mismatches

- At PeMS station 401948, PeMS reports five active northbound US-101 lanes,
  while OSM and SUMO represent edge `617335302` as four lanes. Caltrans'
  managed-lane source and the user's PeMS station screenshot support the
  five-lane observation, but a network correction still needs a lane-to-lane
  connection design.
- At station 402377, PeMS reports four lanes and the matched OSM/SUMO edge
  `861090931` has five. The station is accepted in the data inventory, but the
  discrepancy is not corrected in the model.
- At station 402920 on the SR-85 HOV connector, two PeMS detector lanes map to
  a one-lane OSM/SUMO connector. Existing one-lane and two-lane hypotheses were
  run, but neither confirms the actual painted merge.
- At station 401507, the nearest generated edge has seven lanes because an
  added exit/diverge lane is represented in the synthetic SUMO transition.
  The six PeMS mainline lanes and the virtual-loop positions lie before the
  modeled Old Middlefield split, but the short spacing remains sensitive.

## M2 status and remaining work

**M2 is not complete.** The topology checks establish that the selected H0
routes are connected, but the M2 exit condition also requires visual review of
both directions, every ramp/merge/diverge, and each relevant warning. No
hand-authored network correction has yet been applied under
`network/us101_corridor/patches/`, and the generated network is not versioned.

Before M2 can be closed:

1. Inspect the relevant warning locations and the Shoreline, SR-85, Moffett,
   San Antonio, SR-237, and Oregon Expressway movements in SUMO or aerial
   imagery.
2. Resolve the four lane/transition discrepancies above and apply only
   source-backed corrections; preserve competing interpretations as named
   network variants if the geometry is still uncertain.
3. Record the final patch and source evidence, rebuild the network, rerun route
   checks, and rerun the H0 smoke test.

The current network is suitable for continued calibration experiments only
with these limitations visible. It is not yet an audited basis for claiming a
controller benefit.
