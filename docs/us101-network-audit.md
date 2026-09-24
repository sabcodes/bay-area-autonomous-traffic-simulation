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
| `396010342`, at the Oregon Expressway terminal junction | OSM `placement=transition` is unsupported; no edge retains this ID after `--geometry.remove`. | Resolved as an ID/geometry simplification, **not** a missing movement: OSM way `396010342` continues way `396010343` through node `3988099144`. The generated one-lane edge `396010343` spans `1080063002` to `1392020693` and connects lane 0 to lane 0 of five-lane edge `396010341`. The exact painted ramp geometry still belongs in the visual audit. |
| `348360455`, near the Shoreline interchange | Sharp turn radius of 7.99 m at the edge end. | It is a two-lane motorway link signed toward CA-85 South / US-101 South, about 65 m from the northbound mainline route. Check ramp curvature and its connection in SUMO. |
| `690599564#0`, near the Shoreline interchange | A junction cluster is reduced because of parallel outgoing movements. | OSM marks the link toward US-101 North / Old Middlefield Way; it is about 91 m from the mainline route. Confirm the resulting split/merge movement visually. |
| `941192341`, Mathilda Avenue / SR-237 approach | SUMO does not join a junction cluster because of parallel incoming movements. | It is a two-lane link signed for eastbound SR-237, about 255 m from the mainline route. Confirm its relation to the SR-237 boundary movements. |
| `19146053#0`, near West Maude Avenue / SR-237 | A minor green connection exceeds 19.44 m/s; SUMO warns a turn lane may be missing. | It is a two-lane link for eastbound SR-237, outside the modeled through-mainline route. Check whether its approach connection is in scope and plausible. |

Other logged warnings include unsupported cycleway compounds, minor-street
turn geometry, and signal programs elsewhere in the broad bounding box. They
were not associated with the audited US-101 through-route edges in this pass.
The full captured log was temporary and is not a tracked artifact. To inspect
it again without replacing the current project network, run the same importer
into a fresh temporary directory:

```bash
audit_dir=$(mktemp -d)
.venv/bin/netconvert \
  --osm-files data/osm/us101_corridor.osm.xml \
  --output-file "$audit_dir/us101_corridor.net.xml" \
  --geometry.remove --ramps.guess --junctions.join --tls.discard-simple \
  > "$audit_dir/netconvert.log" 2>&1
```

## Known geometry mismatches

- At PeMS station 401948, PeMS reports five active northbound US-101 lanes,
  while OSM and SUMO represent edge `617335302` as four lanes. Caltrans'
  managed-lane source and the user's PeMS station screenshot support the
  five-lane observation. A [2015 VTA/Caltrans project report](https://www.vta.org/system/files?file=2019-09%2FAppendix+B++-+US+101+Express+Lanes+Project%E2%80%99s+Project+Report%2C+August+2015_0.pdf)
  (section 3.3.1, printed pages 13–14) explicitly lists a northbound auxiliary
  lane from Moffett Boulevard to N. Shoreline Boulevard. This historical
  design record corroborates the possible missing modeled lane; it is not a
  current as-built survey. A network correction still needs a source-backed
  lane-to-lane connection design at both ends of edge `617335302`.
- At station 402377, PeMS reports four lanes and the matched OSM/SUMO edge
  `861090931` has five. A close aerial view centered on the PeMS coordinate
  (37.440393, -122.113925) confirms the detector is on US-101 rather than the
  adjacent E Bayshore Road/frontage facility. The same 2015 report lists a
  northbound auxiliary lane from San Antonio Road to Oregon Expressway, so a
  five-lane physical cross-section with only four PeMS detectors is plausible.
  However, the report predates the measured 2025 data and the aerial image
  does not establish which lane, if any, PeMS omits. Keep the station in the
  inventory, but do not treat its four-lane flow as a proven full-freeway total
  or change the network until detector coverage is confirmed.
- PeMS 402920 is labeled as a two-lane southbound SR-85 on-ramp. The closest
  generated SUMO feature is a two-lane synthetic entrance feeding southbound
  CA-85 edge `11479094` (~9.9 m from the station coordinate); the one-lane NB
  US-101 HOV connector is ~37.4 m away. Treat 402920 as likely outside the NB
  study route and do not use its observed profile as NB ramp demand. The
  Playwright-captured Google Maps imagery confirms only the interchange area;
  it does not resolve lane markings. Prior HOV-path scenarios remain
  counterfactual sensitivities. Audit the actual NB general-purpose connector
  separately before changing its geometry.
- At station 401507, the nearest generated edge has seven lanes because an
  added exit/diverge lane is represented in the synthetic SUMO transition.
  The six PeMS mainline lanes and the virtual-loop positions lie before the
  modeled Old Middlefield split, but the short spacing remains sensitive. The
  [2018 VTA/Caltrans pavement-delineation sheets PD-18 and PD-19](https://www.vta.org/system/files?file=2019-11%2FAppendix+C+-+US101-SR85+Express+Lanes+Project+Plans.pdf)
  draw a northbound Shoreline entrance and Old Middlefield exit in this area;
  they support the existence of both movements, not the precise position of
  the modeled seven-lane transition or the 2025 painted lane count.

## Playwright visual evidence (2026-09-24)

The repeatable screenshot command is documented in the
[README](../README.md#playwright-map-audit). It stores the PNG and a timestamped
URL/coordinate JSON record under ignored `outputs/map_audit/`; third-party map
imagery is not committed. These are interpretation aids, not surveyed plans or
proof of current lane configuration.

| PeMS station | Captured satellite view | What it supports | What it does not settle |
| --- | --- | --- | --- |
| 401948 | [Moffett NB](https://www.google.com/maps/@37.409514,-122.071728,20z/data=!3m1!1e3) | The station-centered view shows the divided US-101 carriageway and a separate managed-lane area. | The complete lane transition to Shoreline and SUMO connection indices. |
| 401507 | [Shoreline NB](https://www.google.com/maps/@37.412677,-122.079539,20z/data=!3m1!1e3) | The view shows nearby ramp pavement, gore markings, and a mainline cross-section. | Whether the seven-lane synthetic SUMO edge represents the painted exit-lane transition at the detector's precise longitudinal position. |
| 402377 | [San Antonio–Oregon NB](https://www.google.com/maps/@37.440393,-122.113925,20z/data=!3m1!1e3) | The station coordinate is on US-101, not the parallel frontage road. | Whether all five modeled lanes have active PeMS detectors. |

The same script captured the four remaining importer-warning areas at the
[Shoreline loop](https://www.google.com/maps/@37.411452,-122.079141,19z/data=!3m1!1e3),
[Shoreline/La Avenida link](https://www.google.com/maps/@37.413468,-122.078318,19z/data=!3m1!1e3),
[Mathilda/SR-237 approach](https://www.google.com/maps/@37.401426,-122.026866,19z/data=!3m1!1e3),
and [West Maude/SR-237 approach](https://www.google.com/maps/@37.395001,-122.045769,19z/data=!3m1!1e3).
Those views locate the movements and distinguish the two SR-237 boundary
areas from the NB US-101 through route. They do **not** establish that the
SUMO sharp-radius or junction-cluster warnings are harmless: connection
indices, turn radii, and allowed lane changes still need a network-level check.
Two more 21z views center the [SR-85 split](https://www.google.com/maps/@37.408584,-122.069243,21z/data=!3m1!1e3)
and [Shoreline-side merge](https://www.google.com/maps/@37.410960,-122.075152,21z/data=!3m1!1e3)
at the ends of four-lane SUMO edge `617335302`; lane paint and bridge shadows
remain insufficient to infer safe new connection indices.

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
2. Resolve the remaining 401948/402377 lane-count questions and the 401507
   synthetic transition, then apply only source-backed corrections. Preserve
   competing interpretations as named network variants if geometry remains
   uncertain. Keep the 402920 station-to-path counterfactual out of the
   observed NB demand model.
3. Record the final patch and source evidence, rebuild the network, rerun route
   checks, and rerun the H0 smoke test.

The current network is suitable for continued calibration experiments only
with these limitations visible. It is not yet an audited basis for claiming a
controller benefit.
