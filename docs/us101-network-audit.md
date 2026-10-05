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
junctions have been reviewed in the
[checklist](us101-ramp-review-checklist.md) using the ledger, source tags,
saved map views, and owner observations. They are junction rows, not 40
separate ramps or 40 surveyed lane layouts. A branch trace stops at the first
trunk or surface road and does not prove the rest of an interchange or a
precise lane marking. The current network also does not encode verified
express-lane eligibility behavior. The ledger is one part of the M2 decision.

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
None of the four warning edge IDs in the table occurs in the five
generated H0 route definitions. The directed trace confirms that two
Shoreline warnings lie on other reachable review paths even though H0 does
not traverse them; they were reviewed for M2 and retained as documented
approximations. The Mathilda and West Maude warnings are on SR-237/approach
movements outside those H0 routes and did not appear in the bounded branch
trace. The Mathilda approach was reviewed separately; West Maude lies outside
the US-101 mainline acceptance area.
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
  managed-lane source and the user's station-centered review support four
  through lanes plus a short fifth entry-to-exit weaving lane near the ramp.
  Treat the fifth PeMS channel as that auxiliary lane for the mainline-only
  comparison, while retaining the user's map interpretation as provisional
  detector placement rather than surveyed wiring evidence. [VTA's Phase 3 project record](https://www.vta.org/projects/us-101-and-state-route-85-express-lanes-project-phase-3)
  says the existing double carpool lanes north of the Mountain View SR-85
  interchange were converted to double express lanes, with service beginning
  in February 2022. VTA's [Phase 3 fact sheet](https://www.vta.org/sites/default/files/2020-01/85-101%20phase%203_011320_0.pdf)
  says that conversion did not construct new traffic lanes. An earlier
  [VTA/Caltrans project report](https://www.vta.org/system/files?file=2019-09%2FAppendix+B++-+US+101+Express+Lanes+Project%E2%80%99s+Project+Report%2C+August+2015_0.pdf)
  (section 3.3.1, printed pages 13–14) also lists a northbound auxiliary lane
  from Moffett Boulevard to N. Shoreline Boulevard. Together with the 2025
  five-detector record, this supports the separate auxiliary-lane
  interpretation. The historical report is not a current as-built survey.
  The isolated five-lane candidate below tests one explicit right-side
  auxiliary-lane interpretation, but is not promoted to the audited baseline.
- At station 402377, PeMS reports four lanes and the matched OSM/SUMO edge
  `861090931` has five. The user's close aerial review identifies five
  continuous through lanes at the pin. A view centered on the PeMS coordinate
  (37.440393, -122.113925) confirms the detector is on US-101 rather than the
  adjacent E Bayshore Road/frontage facility. VTA's Phase 3 record describes
  double express lanes on this side of SR-85, and the 2015 report lists a
  northbound auxiliary lane from San Antonio Road to Oregon Expressway, so a
  five-lane physical cross-section with only four PeMS detectors is plausible.
  However, neither the older report nor aerial imagery identifies the lane
  loops. A three-seed lane-specific sensitivity comparison favors omitting the
  far-right lane by flow fit (4.99% versus 15.37% flow MAPE), while speed error
  is 0.15 mph lower for the opposite mapping. Use indices 1–4 only as a
  provisional flow-based choice; do not call it confirmation of physical
  detector coverage.
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

## Detector lane-channel checks (2026-10-03)

The downloaded PeMS Station 5-Minute rows include per-lane samples, flow,
occupancy, speed, and an observed flag. Checking those fields directly
separates configured/observed channels from blank slots in the fixed-width
export; it does not reveal the exact pavement location of each detector loop.

| Station | PeMS metadata and observed channels, 07:00–08:59 | SUMO/map alignment result | Remaining question |
| --- | --- | --- | --- |
| 401948 / Moffett | Metadata says 5 lanes. Channels 1–5 each have 312 observed lane records over 13 dates; channel 5 averages 77.4 vehicles per five minutes and is active. The user identifies four through lanes at the pin and a short fifth entry-to-exit weaving lane by the ramp. | The station coordinate projects onto four-lane edge `617335302`, 241 m along its 582 m length. | For mainline-through comparison, use the 4 through lanes and exclude channel 5; include the fifth only in a model that explicitly represents the weaving lane. The physical channel-to-pavement assignment remains based on map interpretation, not a surveyed loop drawing. |
| 401507 / Shoreline | Metadata says 6 lanes. Channels 1–6 each have 288 observed lane records over 12 dates; channels 7–8 have none. The user identifies six through lanes and a physically separate exit path at the pin. | The coordinate projects 70.2 m along the 94.71 m seven-lane `509747406-AddedOffRampEdge`; modeled lane 0 branches to the one-lane exit and lanes 1–6 continue to the six-lane through edge. | Aggregate SUMO lanes 1–6 to match the six PeMS channels; exclude lane 0 from the mainline total. |
| 402377 / San Antonio–Oregon | Metadata says 4 lanes. Channels 1–4 each have 312 observed lane records over 13 dates; channels 5–8 have no observations. The user identifies five continuous through lanes at the pin. | The coordinate lies 0.05 m from five-lane mainline edge `861090931`, at 161.42 m along its 454 m length. Three H0 seeds were evaluated using lane-specific loops. | Flow fit provisionally favors omitting the far-right lane (SUMO indices 1–4); speed error is marginally lower when omitting the far-left lane (indices 0–3). Keep the physical detector mapping unverified; see the sensitivity results below. |

The local PeMS metadata gives each station's lane count but does not georeference
the individual detector channels. Lane numbering varies across data systems; a
California lane-by-lane study, for example, defines Lane 1 as rightmost. See the
[PATH lane-by-lane flow and speed study](https://path.berkeley.edu/wp-content/uploads/2024/10/trb_2020_predicting_lane_by_lane_flows_and_speeds.pdf).
Do not infer a physical channel order from that study or from a District-wide
convention without station-specific configuration evidence.

### 402377 four-of-five lane sensitivity

The unknown physical mapping was bounded with five lane-specific SUMO E1 loops
on edge `861090931` at position 161.42 m. The existing H0 route and network
were run with seeds 41, 42, and 43; each candidate was compared at the 24
five-minute intervals from 07:00–08:59 against station 402377's four-channel
PeMS aggregate on the same nine observation dates used by the H0 baseline.
SUMO lane index 0 is rightmost.

| Candidate measured group | Excluded lane | Flow MAPE, mean over 3 seeds | Flow MAE | Speed MAE |
| --- | --- | ---: | ---: | ---: |
| SUMO indices 0–3 | Far-left (index 4) | 15.37% | 808.6 veh/h | 5.25 mph |
| SUMO indices 1–4 | Far-right (index 0) | **4.99%** | **257.3 veh/h** | 5.40 mph |

The flow metrics consistently favor the indices 1–4 candidate; the speed metric
favors indices 0–3 by only 0.15 mph. Use indices 1–4 as the provisional
flow-based operational mapping. This is a model fit preference, not evidence
about the actual Caltrans loop wiring. Retain both alternatives in any future
lane-specific analysis until a station-specific detector layout record is
available.

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

## Additional user-reviewed Google Maps cross-sections (2026-09-25)

The project owner counted marked freeway lanes in five Google Maps views at
the locations listed below. These are useful visual observations, not
surveyed as-built records. The screenshots show a 2026 Vexcel/Airbus imagery
credit, which is not a verified acquisition date. Counts are recorded at the
pin or named ramp section as described by the reviewer; lane transitions are
not reduced to one count for the whole interchange.

| Location | User-observed geometry | Comparison and remaining question |
| --- | --- | --- |
| Moffett / station 401948, near Exit 399A | Four northbound lanes at the station pin; a fifth lane is present briefly near the ramp. | PeMS reports five active lanes while the baseline edge has four. Determine whether the short fifth lane joins or exits and whether the detector cross-section lies within it. Keep the five-lane candidate unpromoted. |
| Shoreline / station 401507 | Six lanes at the pin. | Matches the six-lane PeMS count. The nearby seven-lane SUMO section is still a synthetic transition; locate its start/end relative to the detector and the Shoreline/Old Middlefield movements. |
| San Antonio–Oregon / station 402377 | Five roadway lanes at the pin. | Matches the five-lane OSM/SUMO edge; PeMS has four active detector lanes. The imagery supports the physical lane count but does not establish whether PeMS covers all five. |
| Mathilda northbound split (`NB-05-O`) | The owner's 2026-10-04 review confirms one rightmost freeway lane drops into the ramp, which widens farther downstream. Four freeway lanes continue. | The corrected network retains five lanes to the gore, maps lane 0 to a one-lane ramp, and maps lanes 1–4 to the four through lanes. It widens the ramp about 30 m before the end of edge `9080606`; that precise widening location is an approximation. |
| Shoreline northbound split (`NB-22-O`) | Of six approaching lanes, the two rightmost exit and four continue. | The current SUMO connection maps lanes 0–1 to the two-lane Shoreline exit and lanes 2–5 to the four continuing lanes, matching the owner review. |
| Southbound US-101 to CA-85 split (`SB-15-O`) | Six lanes approach; the two rightmost general-purpose lanes head to CA-85 and four continue on US-101. A separate left-side express connector also exists. | The SUMO connection maps lanes 0–1 to the right-side CA-85 split and lanes 2–5 through on US-101, matching the owner's general-purpose split review. OSM and SUMO also contain a separate left-side one-lane connector `38083577` from lane 5 at `SB-12-O`; its occupancy/toll permissions remain open. |

These observations settle the lane side and broad continuation at the three
reviewed exits. They do not establish managed-lane eligibility or the exact
Mathilda widening position. The 401948 lane relationship, 401507 detector
position relative to its separate exit, and 402377 detector coverage remain
provisional.

At `SB-05-I` near Rengstorff Avenue (37.420970, -122.092643), OSM and the
owner's 2026-10-04 review agree that entrance link `534473511` has one lane.
The correction removes SUMO's guessed second lane. The single ramp lane can
enter the new rightmost auxiliary lane 0 or its adjacent through lane 1; the
five upstream US-101 lanes shift to lanes 1–5. The next generated edge drops
lane 0 into the Rengstorff exit after 21.52 m. The owner's follow-up confirms
this is a short interchange pocket: drivers continuing on US-101 must join
one of the five through lanes before the pocket drops. This resolves the
endpoint and broad movement topology at `SB-05-I`/`SB-06-O`; the direct ramp
connection to through lane 1 is an operational approximation of that short
merge, not a surveyed lane-change position.

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

## M2 acceptance and limits

**M2 is complete for the versioned US-101 corridor network at the practical
project standard.** The [acceptance record](us101-m2-acceptance.md) gives the
exact network hash, the 40 reviewed branch dispositions, warning decisions,
and future-use gate. Four branches carry H0 demand; 36 do not. The topology
checks establish connected through and branch movements, and the versioned
Mathilda/Rengstorff patch corrects the two identified lane-count defects.
The generated network remains an OSM-derived model, not a surveyed as-built
record. Detector loop wiring is not claimed as verified.

### Provisional lane decisions for the current baseline

These are explicit working mappings for the route/H0 rebuild. They resolve
which model cross-section to compare; they do not claim Caltrans loop wiring or
current as-built striping has been confirmed.

| Location | Working choice | Confidence and remaining uncertainty |
| --- | --- | --- |
| 401948, Moffett | Compare PeMS Channels 1–4 to the four US-101 through lanes. Treat Channel 5 as the short weaving/auxiliary lane. Keep the separate five-lane network as a sensitivity candidate. | User map count and historical VTA corridor documentation support the cross-section. Exact loop position relative to the taper and the lane-level weaving path remain unverified. |
| 401507, Shoreline | Compare the six PeMS channels with the six continuing through lanes; exclude the lane that branches to the exit from this station comparison. | User count and map show six through lanes plus a separate exit path. Exact detector position relative to the split and the modeled lane-change path remain unverified. |
| 402377, San Antonio–Oregon | For flow sensitivity, use SUMO lane indices 1–4 against PeMS Channels 1–4 (omit rightmost index 0). | Three-seed flow fit favors this mapping: flow MAPE 4.99% versus 15.37% for indices 0–3. Speed MAE is slightly better for indices 0–3 (5.25 versus 5.40 mph). This is a provisional flow-based choice, not proof of which physical loop is absent. |
| SB-05-I, Rengstorff entrance | Use the corrected one-lane entrance and short auxiliary/nearest-through connections. | Owner confirms the pocket feeds the immediate exit; the generated 21.52 m segment and five continuing lanes match that topology. The exact merge point within the short segment is approximated. |
| NB-05-O, Mathilda | Use the corrected one-lane drop from the five-lane US-101 approach, with ramp widening later. | The lane behavior is owner-confirmed. The widening point placed in the patch is approximate. |
| NB-22-O, Shoreline; SB-15-O, CA-85 general-purpose split | Keep the current two-rightmost-exit/four-through connections. | The owner confirms the lane side and counts. Full ramp geometry and managed-lane access rules remain under review; the left-side CA-85 express connector is separate. |

The 2026-10-03 rebuild below records the earlier unpatched baseline. The
2026-10-04 rebuild that follows applies the versioned Mathilda/Rengstorff
correction. The five-lane Moffett candidate remains a separate sensitivity
network. Three Shoreline/Mathilda importer warnings are retained as reviewed
modeling approximations; the West Maude/SR-237 warning is outside the
US-101 mainline acceptance area.
See the [warning review](us101-importer-warning-review.md) and
[40-junction checklist](us101-ramp-review-checklist.md) for the evidence and
limits behind those dispositions.

### Historical unpatched rebuild and route/H0 verification (2026-10-03)

Rebuilt the base network from the saved OSM extract with
`.venv/bin/python -m bay_area_traffic_sim import-us101-osm` (using
`PYTHONPATH=src` for the project checkout). The importer exited successfully
and emitted its broad-extract warnings, including the documented unresolved
interchange cases. The generated network SHA-256 is
`48678e821b942e507d2d3940f6f63278f72f4cb978590e2d6963bba1b9ee7ad5`; the OSM
input SHA-256 is
`2e97a354b99eafcf104d98978a19a95b5f75908b5ac267cb03d20bb763c62a4e`.

Regenerated `outputs/us101_corridor/lane_connection_audit.json`. The
northbound audit route has 37 edges, 36 transitions, and 19 branch
transitions; the southbound route has 36 edges, 35 transitions, and 21 branch
transitions. All side-path searches terminated: 18 paths returned to an
audited route, 14 reached another motorway, and 86 reached a surface/other
road, with zero graph-boundary/disallowed, depth-limit, or cycle endings.
Shared/forked paths mean those are not independent ramp counts.

Reran H0 with seeds 41, 42, and 43 using
`configs/us101_human_baseline.json`. Each run completed all 13,482 vehicles
and ended at 9,900 seconds. Mean trip speed was 59.10 mph (sample SD 0.18)
and mean travel time was 383.41 seconds (sample SD 1.27). The run logs contain
no route, teleport, collision, or emergency-braking warnings. The generated
report is `outputs/us101_corridor/h0_multiseed_report.json`.

This is a routing and simulation-integrity pass. Calibration remains weak:
Shoreline 401507 has 32.94% mean flow MAPE and 10.50 mph speed MAE; across the
six reported stations, speed MAE ranges from 10.50 to 17.86 mph. The 402377
four-of-five lane choice remains a provisional sensitivity result. The
regenerated route/H0 artifacts do not close the physical lane-link or warning
questions above.

### Owner-reviewed lane corrections and rebuild (2026-10-04)

The project owner checked the four outstanding movements again against
high-resolution imagery and local layout information. At Mathilda, one
rightmost northbound US-101 lane exits and the ramp widens later. At Shoreline,
the two rightmost of six northbound lanes exit while four continue. At the
southbound CA-85 general-purpose split, the two rightmost lanes exit; a
separate left-side HOV/express flyover exists upstream. At the Rengstorff
southbound entrance, one ramp lane joins a short pocket that feeds the
immediate exit; vehicles continuing on US-101 join the five through lanes.

The [versioned edge patch](../network/us101_corridor/patches/mathilda_rengstorff.edg.xml)
and [connection patch](../network/us101_corridor/patches/mathilda_rengstorff.con.xml)
are now applied by `import-us101-osm` after the ordinary OSM import. The raw
import remains in ignored `outputs/us101_corridor/us101_corridor_osm_raw.net.xml`
for comparison. The corrected network retains five freeway lanes until the
Mathilda gore, sends only lane 0 to the one-lane ramp, and widens the ramp
farther downstream. The patch removes the guessed second Rengstorff entrance
lane; the single lane can enter the new auxiliary lane or its nearest through
lane. The exact Mathilda widening station is approximated by a split 30 m
before the end of OSM edge `9080606`.

The corrected generated network SHA-256 is
`13103c0b31d22dff15159b56e5ba03f0becd9594868c4cdfeac60497e86b9bc6`.
The regenerated lane ledger still has 37 northbound and 36 southbound route
edges, 19 northbound and 21 southbound branch transitions, and side-path
endpoint counts of 18 returning to a through route, 14 reaching another
motorway, and 86 reaching a surface/other road. There are zero graph-boundary,
depth-limit, or cycle endings. At the reviewed nodes, its connection links
match the owner's Mathilda, Shoreline, and right-side CA-85 lane assignments.
The separate left express connector is OSM way `38083577`, marked
`hov=designated`, and is modeled from the far-left lane at `SB-12-O`.
[VTA's Phase 3 budget record](https://www.vta.org/media/46946) says these
US-101/SR-85 direct carpool connectors were converted to express operation
in 2022. The current [FasTrak corridor rules](https://www.bayareafastrak.org/en/toll-locations/express-lanes-101-sr85-santa-clara.shtml)
allow tagged solo drivers at full toll, two-person carpools at half toll,
and eligible 3+ carpools free on weekdays 05:00–20:00; outside those hours
the lanes are open to all. Thus generic passenger access in SUMO is not
automatically illegal, but the model has no tag, occupancy, or toll state.

Three H0 seeds (41–43) were rerun against the corrected network. Each
completed 13,482 vehicles; mean trip speed was 59.00 mph and mean travel time
was 383.88 seconds. The run logs have no route, teleport, collision,
emergency-braking, or SUMO warning entries. Shoreline 401507 still has 32.96%
mean flow MAPE and 10.45 mph speed MAE, so this is a route/simulation check,
not a calibration claim. The generated report is
`outputs/us101_corridor/h0_multiseed_report.json`.

The Rengstorff model drops its new auxiliary lane into exit edge `8923902`
after 21.52 m. The owner's follow-up confirms that this is the intended
short interchange pocket, with five through lanes downstream. It is a normal
SUMO edge between merge and diverge nodes, rather than a SUMO-internal
junction edge; it provides the requested short connection topology. The
direct ramp-to-through-lane link approximates the required merge within the
short pocket. A tag/occupancy/toll treatment is still needed before
managed-lane use can be interpreted as legally calibrated.
The two Shoreline importer warnings and Mathilda/SR-237 warning remain in the
rebuild log. Their M2 dispositions are documented approximations.

The source OSM join is at `37.4209703, -122.0926429` and its exit split is
at `37.4208225, -122.0924400`, both at the Rengstorff Avenue interchange.
The [close aerial view](https://www.google.com/maps/@37.42090,-122.09255,22z/data=!3m1!1e3)
inspected on 2026-10-04 shows an `ONLY` marking on the rightmost southbound
lane just beyond the overpass, consistent with the immediate exit. The
attached example interchange photo is not location-specific evidence; the
owner's explicit Rengstorff description settles the pocket endpoint. The
overpass still obscures the exact lane-change position.

For any future route expansion:

1. Check route behavior and current lane use for a Shoreline/Mathilda warning
   path before an experiment sensitive to that movement.
2. Model tag, occupancy, and toll choice before interpreting express-lane
   usage as observed behavior. Keep the 402920 station-to-path counterfactual
   out of observed northbound demand.
3. Repeat the branch ledger and route/H0 checks after any topology patch and
   record its source and resulting hash.

The accepted network supports the current fixed H0 route set and provides a
reviewed corridor topology for later scenarios. Calibration and separate-day
validation remain necessary before claiming a controller benefit.
