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

The earlier unconstrained southbound shortest path was **not** a valid
through-mainline audit route: its 41 edges included six one- or two-lane
motorway links through the SR-85 interchange (`394382945 → 8925144 →
394382094#0 → 9899589 → 281956181 → 281956185`). It left and rejoined the
freeway. A versioned checkpoint at four-lane edge `867247243` now forces the
southbound through path. The corrected route has 36 edges and no edge narrower
than four lanes. This corrects the prior 41-edge claim; the 41-edge path remains
in a regression test specifically because graph connectivity alone missed the
shortcut.

The new lane-link ledger checks all 36 northbound and 35 southbound adjacent
edge pairs for actual SUMO lane connections that permit passenger vehicles.
It inventories 19 northbound and 21 southbound junctions with an immediate
incoming or outgoing side connection. A bounded directed search follows each
side connection to the first audited through route, other motorway, or surface
road. The resulting 118 path endings comprise 86 surface/other-road endings,
18 returns to an audited through route, and 14 other-motorway endings; none hit
the depth or cycle limit. Forks and shared paths mean these are neither 118
independent ramps nor 118 validated movements. This is a systematic topology
inventory, not a lane-marking sign-off.

All five saved H0 routes (mainline, three on-ramps, and one off-ramp) were
checked: every edge exists and every adjacent pair connects. The three-seed H0
simulation previously completed all 13,482 vehicles per seed without route,
teleport, collision, or emergency-braking warnings. This validates those
specific routes, not every ramp in the imported network.

## Full through-route lane-connection ledger

The [audit configuration](../configs/us101_lane_connection_audit.json) records
both directions and the southbound SR-85 checkpoint. The
[ledger builder](../src/bay_area_traffic_sim/corridor_junctions.py) records lane
counts, passenger-permitted through-lane mappings, side-branch lane mappings,
and coordinates for every transition. Reproduce its ignored JSON output with:

```bash
.venv/bin/python -m bay_area_traffic_sim audit-us101-lane-connections
```

The output is `outputs/us101_corridor/lane_connection_audit.json`. A test
reconstructs both routes, checks every through connection, and confirms that
removing the SR-85 checkpoint reintroduces narrow ramp links. The 40 branch
junctions are a [manual review checklist](us101-ramp-review-checklist.md),
**not** 40 visually approved ramps. A branch trace stops at the first trunk or
surface road and does not prove the rest of an interchange or a precise lane
marking. The current network also does not encode verified express-lane
eligibility rules. We will not use this ledger alone to declare M2 complete.

This matters for the human baseline as well as for geometry. [VTA's current
express-lane guide](https://www.vta.org/go/express-lanes) requires a FasTrak
account/tag for express-lane use and distinguishes toll-paying solo drivers
from qualifying carpools; its [occupancy FAQ](https://www.vta.org/faq/what-are-carpool-occupancy-requirements)
gives HOV 3+ as the toll-free threshold for US-101/SR-85. SUMO's generic
`passenger` permission check only proves a car can follow a link in the
imported graph. It does **not** model toll choice, occupancy, access-zone
markings, or lane-change restrictions. These behavioral/legal layers must be
represented or bounded as sensitivity assumptions before treating
lane-specific simulation results as calibrated reality.

The [2018 VTA/Caltrans pavement-delineation and sign plans, sheets PD-18–PD-34](https://www.vta.org/system/files?file=2019-11%2FAppendix+C+-+US101-SR85+Express+Lanes+Project+Plans.pdf)
were visually inspected as historical primary evidence. PD-18 and PD-19 draw
the Shoreline NB entrance and the separate Old Middlefield NB exit; PD-22–PD-25
draw Rengstorff and San Antonio ramps; PD-31–PD-33 draw the Oregon/Embarcadero
movements. They help identify which branch should exist, but their June 2018
approval and sign-work purpose do not prove the September 2026 as-built lane
count or precise SUMO connection indices. They do not cover the eastern
Moffett/SR-237 section of this study route. The downloaded source used for
visual review has SHA-256
`7ad55de077d9a517bec70353feaf3149c46d579f6b18f49a6639972515b64a3d`.
VTA reported [new express-lane striping in October 2021](https://www.vta.org/blog/us-101sr-85-gets-makeover-preparation-new-express-lanes),
so the 2018 plan must not be treated as the final post-conversion paint.
[Caltrans District 4 lists as-built records as a requestable record type](https://dot.ca.gov/caltrans-near-me/district-4/d4-popular-links/district-4-records-request).
No records request has been submitted; post-2022 pavement-delineation/as-built
sheets for Santa Clara US-101 PM 47.9–52.2 would be the strongest documentary
route to resolving the open lane-index decisions.

## Relevant importer warnings

| OSM edge / location | Import warning | Current interpretation |
| --- | --- | --- |
| `396010342`, at the Oregon Expressway terminal junction | OSM `placement=transition` is unsupported; no edge retains this ID after `--geometry.remove`. | Resolved as an ID/geometry simplification, **not** a missing movement: OSM way `396010342` continues way `396010343` through node `3988099144`. The generated one-lane edge `396010343` spans `1080063002` to `1392020693` and connects lane 0 to lane 0 of five-lane edge `396010341`. The exact painted ramp geometry still belongs in the visual audit. |
| `348360455`, near the Shoreline interchange | Sharp turn radius of 7.99 m at the edge end. | It is a two-lane motorway link signed toward CA-85 South / US-101 South. The directed side-path ledger places it on review paths `SB-11-O` and `SB-16-I`; inspect the actual curvature and lane connection there. |
| `690599564#0`, near the Shoreline interchange | A junction cluster is reduced because of parallel outgoing movements. | OSM marks the link toward US-101 North / Old Middlefield Way. The directed ledger places it on `NB-28-I`; confirm the resulting split/merge movement visually. |
| `941192341`, Mathilda Avenue / SR-237 approach | SUMO does not join a junction cluster because of parallel incoming movements. | It is a two-lane link signed for eastbound SR-237, about 255 m from the mainline route. Confirm its relation to the SR-237 boundary movements. |
| `19146053#0`, near West Maude Avenue / SR-237 | A minor green connection exceeds 19.44 m/s; SUMO warns a turn lane may be missing. | It is a two-lane link for eastbound SR-237, outside the modeled through-mainline route. Check whether its approach connection is in scope and plausible. |

Other logged warnings include unsupported cycleway compounds, minor-street
turn geometry, and signal programs elsewhere in the broad bounding box. They
were not associated with the audited US-101 through-route edges in this pass.
None of the four unresolved warning edge IDs in the table occurs in the five
generated H0 route definitions. The directed trace confirms that two
Shoreline warnings lie on other reachable review paths even though H0 does
not traverse them; they cannot be dismissed for M2. The Mathilda and West
Maude warnings are on SR-237/approach movements outside those H0 routes and
did not appear in the bounded branch trace; audit their approach context
separately rather than calling them NB US-101 mainline defects.
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
  five-lane observation. [VTA's Phase 3 project record](https://www.vta.org/projects/us-101-and-state-route-85-express-lanes-project-phase-3)
  says the existing double carpool lanes north of the Mountain View SR-85
  interchange were converted to double express lanes, with service beginning
  in February 2022. VTA's [Phase 3 fact sheet](https://www.vta.org/sites/default/files/2020-01/85-101%20phase%203_011320_0.pdf)
  says that conversion did not construct new traffic lanes. An earlier
  [VTA/Caltrans project report](https://www.vta.org/system/files?file=2019-09%2FAppendix+B++-+US+101+Express+Lanes+Project%E2%80%99s+Project+Report%2C+August+2015_0.pdf)
  (section 3.3.1, printed pages 13–14) also lists a northbound auxiliary lane
  from Moffett Boulevard to N. Shoreline Boulevard. Together with the 2025
  five-detector record, this is strong evidence of **at least one** missing
  modeled lane. The total physical count and which lane is omitted by OSM
  remain unsettled; the historical report is not a current as-built survey.
  The isolated five-lane candidate below tests one explicit right-side
  auxiliary-lane interpretation, but is not promoted to the audited baseline.
- At station 402377, PeMS reports four lanes and the matched OSM/SUMO edge
  `861090931` has five. A close aerial view centered on the PeMS coordinate
  (37.440393, -122.113925) confirms the detector is on US-101 rather than the
  adjacent E Bayshore Road/frontage facility. VTA's Phase 3 record describes
  double express lanes on this side of SR-85, and the 2015 report lists a
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
at the ends of four-lane baseline SUMO edge `617335302`; lane paint and bridge
shadows remain insufficient to infer the exact as-built connection indices.

## Provisional five-lane Moffett–Shoreline candidate

The versioned [edge patch](../network/us101_corridor/patches/moffett_aux_five_lane.edg.xml),
[connection patch](../network/us101_corridor/patches/moffett_aux_five_lane.con.xml),
and [H0 configuration](../configs/us101_human_baseline_moffett_aux_candidate.json)
make one lane-level hypothesis explicit. SUMO lane 0 is the rightmost lane.
This is a sensitivity scenario, **not** a claim about the present pavement,
managed-lane designation, or where the PeMS loops sit within each lane.

| Transition | Candidate mapping | Interpretation to test |
| --- | --- | --- |
| Upstream `1343740299` (6 lanes) | Lanes 0–1 retain the two-lane Shoreline exit; lane 1 also feeds new through lane 0; lanes 2–5 feed through lanes 1–4. | A right-side auxiliary/through lane begins after a shared exit choice. |
| Midsegment `617335302` | Increase 4 → 5 lanes. | All five active lanes measured by PeMS 401948 have a corresponding virtual loop. |
| Downstream `361615811` (5 lanes) | Midsegment lanes 0–4 feed downstream lanes 0–4; the Shoreline-side ramp `394387883` also feeds downstream lane 0. | The added lane rejoins a shared rightmost merge receiving lane. |

The original four-lane network is unchanged. To rebuild the isolated candidate
after importing the base network, run from the repository root:

```bash
.venv/bin/netconvert \
  --sumo-net-file outputs/us101_corridor/us101_corridor.net.xml \
  --edge-files network/us101_corridor/patches/moffett_aux_five_lane.edg.xml \
  --connection-files network/us101_corridor/patches/moffett_aux_five_lane.con.xml \
  --output-file outputs/us101_corridor/moffett_aux_five_lane/us101_corridor.net.xml
.venv/bin/python -m bay_area_traffic_sim run-us101-human-baseline-multi \
  --config configs/us101_human_baseline_moffett_aux_candidate.json \
  --seeds 41 42 43 \
  --output outputs/us101_corridor/moffett_aux_five_lane/h0_multiseed_report.json
.venv/bin/python -m pytest -q tests/test_moffett_aux_candidate.py
```

The regression test rebuilds the candidate and checks all four local branch
and merge link sets, including preservation of the Shoreline exit and ramp.
An unpatched `netconvert` rebuild was also compared against the candidate:
both contain 4,485 edges; only `617335302` changes lane count, and all
changed non-internal connections are the eight removed and ten added by this
patch. Five edge lengths near the modified junctions also shift slightly as
SUMO reconstructs their geometry, so the variant is not a pure capacity-only
change.

In three human-driver seeds (41–43), the route remained 37 edges and PeMS
401948 gained five modeled loops instead of four. Each run completed 13,482
vehicles, with no route, teleport, collision, or emergency-braking warnings.
This is a simulation integrity check, **not** a safety validation or evidence
that the new lane layout is a better representation of the real road.

The unchanged baseline was rerun with the same seeds and current inputs. Both
layouts completed 13,482 vehicles per seed. Mean trip speeds were 59.10 mph
for the four-lane baseline and 59.13 mph for the candidate; corresponding mean
travel times were 383.41 and 383.08 seconds. These tiny differences are not a
calibration success, especially because `netconvert` also adjusts nearby edge
lengths. The existing calibration code correctly excluded 401948 from the
four-lane report because PeMS measures five lanes there. With five loops, the
candidate can at least be compared against the full five-lane PeMS profile:
its three-seed mean modeled flow is 4,838 vehicles/hour versus 5,451.5
observed, with 11.54% mean five-minute flow MAPE and 8.94 mph speed MAE.
The six other comparable stations change only slightly and still show large
downstream flow and speed errors. Results live in the ignored
`outputs/us101_corridor/moffett_aux_five_lane/h0_multiseed_report.json` and
`outputs/us101_corridor/h0_moffett_matched_baseline_multiseed_report.json`.

## M2 status and remaining work

**M2 is not complete.** The topology checks establish that the selected H0
routes are connected, and a hand-authored *candidate* patch now exists, but the
M2 exit condition still requires visual review of both directions, every
ramp/merge/diverge, and each relevant warning. The baseline network remains
generated and ignored, not a versioned as-built correction.

Before M2 can be closed:

1. Inspect the relevant warning locations and the Shoreline, SR-85, Moffett,
   San Antonio, SR-237, and Oregon Expressway movements in SUMO or aerial
   imagery.
2. Resolve the as-built 401948/402377 lane-count questions and the 401507
   synthetic transition, then apply only source-backed corrections. Preserve
   the five-lane Moffett candidate and other competing interpretations as
   named variants while geometry remains uncertain. Keep the 402920
   station-to-path counterfactual out of the observed NB demand model.
3. Record the final patch and source evidence, rebuild the network, rerun route
   checks, and rerun the H0 smoke test.

The current network is suitable for continued calibration experiments only
with these limitations visible. It is not yet an audited basis for claiming a
controller benefit.
