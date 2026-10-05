# US-101 branch and ramp review checklist

This is the M2 manual-review queue derived from the versioned
[`us101_lane_connection_audit.json`](../configs/us101_lane_connection_audit.json)
configuration. Regenerate the ignored machine-readable ledger with
`.venv/bin/python -m bay_area_traffic_sim audit-us101-lane-connections`.
The ledger gives each row's junction coordinate, directed lane links, and
passenger-legal side paths to the first through-route, other motorway,
surface road, or search boundary. The 40 rows are **branch junctions**, not
necessarily 40 different ramps. A fork may have several paths, and different
rows may belong to one interchange. Do not sum path counts as traffic demand.

The table records the **M2 network disposition** for all 40 branch junctions.
Four movements carry fixed H0 demand and 36 do not. All 40 have now been
reviewed for movement location and direction, ramp side, modeled lane count,
passenger-legal lane links, and directed connectivity. The captured aerials,
OSM tags, and owner observations were used where they show the movement
clearly. The practical M2 decision accepts a plausible, connected corridor
model with documented approximations; it does not certify every painted lane
or detector loop. Adding traffic to a branch outside H0 still requires a
scenario-specific route and permission check.

For a future scenario that uses a reviewed branch, check the **whole traced
path**, not just its first edge:

1. Match the junction coordinate and side path to a named real-world ramp.
2. Check direction, fork/merge shape, lane count, painted lane continuity,
   and legal passenger/HOV/express-lane movement against dated evidence.
3. Compare each SUMO edge and lane connection along the path with the source;
   inspect `netconvert` warnings affecting that movement.
4. Mark `verified`, `corrected and retested`, `excluded`, or `unresolved` with
   evidence and a test/report reference. No row should silently disappear
   when the network is rebuilt.

`I` traces backward from an incoming side edge; `O` traces forward from an
outgoing side edge. The index identifies a transition in the generated route
ledger. The four H0 rows are the side movements used by current demand.
The northbound and southbound through routes were also checked for directed
lane connectivity; southbound ramp demand is outside H0.

| Review ID | Through-route transition | Side edge | Coordinate | Map view | State |
| --- | ---: | --- | --- | --- | --- |
| NB-00-I | 0 | `509747285` | 37.396210, -122.014812 | [Map](https://www.google.com/maps/@37.396210,-122.014812,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-05-O | 5 | `9080606` | 37.398358, -122.024668 | [Map](https://www.google.com/maps/@37.398358,-122.024668,20z/data=!3m1!1e3) | Reviewed H0: corrected one-lane Mathilda drop |
| NB-06-I | 6 | `509747339` | 37.399157, -122.028239 | [Map](https://www.google.com/maps/@37.399157,-122.028239,20z/data=!3m1!1e3) | Reviewed H0: Mathilda one-lane entrance |
| NB-09-O | 9 | `9545875` | 37.400663, -122.035170 | [Map](https://www.google.com/maps/@37.400663,-122.035170,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-10-I | 10 | `509747350` | 37.401538, -122.039132 | [Map](https://www.google.com/maps/@37.401538,-122.039132,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-13-O | 13 | `20113705` | 37.403253, -122.047022 | [Map](https://www.google.com/maps/@37.403253,-122.047022,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-14-I | 14 | `281956182` | 37.405580, -122.056520 | [Map](https://www.google.com/maps/@37.405580,-122.056520,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-17-O | 17 | `394385426` | 37.407048, -122.063201 | [Map](https://www.google.com/maps/@37.407048,-122.063201,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-19-I | 19 | `777748240` | 37.407814, -122.066645 | [Map](https://www.google.com/maps/@37.407814,-122.066645,20z/data=!3m1!1e3) | Reviewed H0: Moffett measured entrance |
| NB-22-O | 22 | `5005672` | 37.408584, -122.069243 | [Map](https://www.google.com/maps/@37.408584,-122.069243,20z/data=!3m1!1e3) | Reviewed: two rightmost lanes exit; no H0 demand |
| NB-23-I | 23 | `394387883` | 37.410960, -122.075152 | [Map](https://www.google.com/maps/@37.410960,-122.075152,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-24-I | 24 | `11479095` | 37.411823, -122.077327 | [Map](https://www.google.com/maps/@37.411823,-122.077327,20z/data=!3m1!1e3) | Reviewed: left-side express connector; no H0 demand |
| NB-26-O | 26 | `30990690` | 37.412795, -122.079791 | [Map](https://www.google.com/maps/@37.412795,-122.079791,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-28-I | 28 | `685973436` | 37.416591, -122.086239 | [Map](https://www.google.com/maps/@37.416591,-122.086239,20z/data=!3m1!1e3) | Reviewed: right-side ramp; cluster warning accepted with limits; no H0 demand |
| NB-30-O | 30 | `9245798` | 37.418142, -122.088362 | [Map](https://www.google.com/maps/@37.418142,-122.088362,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-31-I | 31 | `8927566` | 37.423369, -122.095557 | [Map](https://www.google.com/maps/@37.423369,-122.095557,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-32-O | 32 | `4370043` | 37.425460, -122.098253 | [Map](https://www.google.com/maps/@37.425460,-122.098253,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| NB-33-I | 33 | `9739842#1` | 37.431437, -122.104552 | [Map](https://www.google.com/maps/@37.431437,-122.104552,20z/data=!3m1!1e3) | Reviewed H0: San Antonio measured entrance |
| NB-35-O | 35 | `13100980` | 37.442412, -122.116073 | [Map](https://www.google.com/maps/@37.442412,-122.116073,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-00-I | 0 | `27086204#3` | 37.444857, -122.118965 | [Map](https://www.google.com/maps/@37.444857,-122.118965,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-02-O | 2 | `8925871` | 37.430646, -122.104038 | [Map](https://www.google.com/maps/@37.430646,-122.104038,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-04-O | 4 | `125299850` | 37.428088, -122.101374 | [Map](https://www.google.com/maps/@37.428088,-122.101374,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-05-I | 5 | `534473511` | 37.420970, -122.092643 | [Map](https://www.google.com/maps/@37.420970,-122.092643,20z/data=!3m1!1e3) | Reviewed: corrected one-lane entrance and short pocket; no H0 demand |
| SB-06-O | 6 | `8923902` | 37.420823, -122.092440 | [Map](https://www.google.com/maps/@37.420823,-122.092440,20z/data=!3m1!1e3) | Reviewed: immediate right-side pocket exit; no H0 demand |
| SB-07-I | 7 | `394369030` | 37.418477, -122.089184 | [Map](https://www.google.com/maps/@37.418477,-122.089184,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-09-I | 9 | `304467430` | 37.413510, -122.082092 | [Map](https://www.google.com/maps/@37.413510,-122.082092,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-11-O | 11 | `8924695` | 37.412801, -122.080550 | [Map](https://www.google.com/maps/@37.412801,-122.080550,20z/data=!3m1!1e3) | Reviewed: right-side exit; loop-radius warning accepted with limits; no H0 demand |
| SB-12-O | 12 | `38083577` | 37.411892, -122.078360 | [Map](https://www.google.com/maps/@37.411892,-122.078360,20z/data=!3m1!1e3) | Reviewed: left-side express connector; no H0 demand |
| SB-15-O | 15 | `8924268` | 37.410705, -122.075529 | [Map](https://www.google.com/maps/@37.410705,-122.075529,20z/data=!3m1!1e3) | Reviewed: two rightmost lanes to CA-85; no H0 demand |
| SB-16-I | 16 | `949062561` | 37.407808, -122.067607 | [Map](https://www.google.com/maps/@37.407808,-122.067607,20z/data=!3m1!1e3) | Reviewed: right-side entry; loop-radius warning accepted with limits; no H0 demand |
| SB-17-O | 17 | `394385424#0` | 37.407527, -122.066295 | [Map](https://www.google.com/maps/@37.407527,-122.066295,20z/data=!3m1!1e3) | Reviewed: two rightmost lanes exit; no H0 demand |
| SB-18-I | 18 | `509747360` | 37.406961, -122.063708 | [Map](https://www.google.com/maps/@37.406961,-122.063708,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-21-O | 21 | `394382945` | 37.405257, -122.055939 | [Map](https://www.google.com/maps/@37.405257,-122.055939,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-22-I | 22 | `281956185` | 37.403049, -122.047017 | [Map](https://www.google.com/maps/@37.403049,-122.047017,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-25-O | 25 | `185252028` | 37.400658, -122.036066 | [Map](https://www.google.com/maps/@37.400658,-122.036066,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-26-I | 26 | `8927500#0` | 37.399890, -122.032420 | [Map](https://www.google.com/maps/@37.399890,-122.032420,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-28-O | 28 | `8923686` | 37.399611, -122.031169 | [Map](https://www.google.com/maps/@37.399611,-122.031169,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-29-I | 29 | `517246480` | 37.398693, -122.027075 | [Map](https://www.google.com/maps/@37.398693,-122.027075,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-31-I | 31 | `509747343` | 37.398202, -122.024811 | [Map](https://www.google.com/maps/@37.398202,-122.024811,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |
| SB-34-O | 34 | `8927783` | 37.396422, -122.016668 | [Map](https://www.google.com/maps/@37.396422,-122.016668,20z/data=!3m1!1e3) | Reviewed: right-side one-lane ramp; no H0 demand |

## Map location evidence

Google Maps aerial views were captured at all 40 modeled branch-junction
coordinates on 2026-09-25. The exact-coordinate links are in the checklist
table above; local screenshots and capture timestamps are retained in ignored
`outputs/map_audit/` files. Google's visible imagery credit does not identify
the imagery acquisition date. The views help confirm movement location and
general pavement context, but they do not establish detector coverage or
managed-lane permissions. The practical M2 network review is complete at
the level described below.

## Review outcome (updated 2026-10-04)

The 40 entries were cross-checked against their saved map captures and the
generated lane-connection ledger. Every entry has a passenger-permitted lane
link. The 35 ordinary one-lane ramp links use the rightmost mainline lane;
the three two-lane exits use the two rightmost lanes. The two separate express
connectors use the leftmost lane. The Rengstorff single-lane entrance also
links to the nearest continuing lane from its short exit pocket. These
choices agree with the visible ramp side, source tags, and the owner's
specified splits where available. For branch edges with an explicit OSM
`lanes` tag, the only source/model count difference is `9080606`: OSM says
two, while the corrected SUMO edge has one lane at the Mathilda gore and
widens later, matching the owner's observation. No contradictory branch-side
connection was found. The bounded side-path search terminates without depth
limit or cycle cases: 18 paths return to an audited through route, 14 reach another
motorway, and 86 reach a surface or other road. These shared/forked path
totals are not 118 separate ramps.

**M2 disposition:** all 40 branch junctions are reviewed and accepted as a
practical corridor network. The two found lane-count defects were corrected
at Mathilda and Rengstorff; the other branch connections are retained. Three
importer warnings are accepted as documented approximations, not suppressed
or represented as survey-grade geometry. The saved images sometimes show the
freeway at a connector endpoint rather than the ramp gore; this review uses
the entire directed path and interchange context for those rows. The decision
does not establish exact paint, PeMS loop wiring, signal phases, or managed
lane demand behavior.

Specific modeled approximations relevant to future scenarios:

- `SB-05-I` (Rengstorff entrance): the owner confirms one ramp lane, matching
  OSM. The versioned correction removes SUMO's guessed second lane and maps
  the single ramp lane to the new rightmost auxiliary lane or the nearest
  through lane. The source network then sends that auxiliary lane to the
  `SB-06-O` exit after 21.52 m. The owner's follow-up confirms this is a
  short interchange pocket rather than a lane continuing toward Shoreline.
  The five freeway lanes continue. A close aerial view shows an `ONLY`
  marking beyond the overpass; the exact merge point from pocket to through
  lane remains an operational approximation in SUMO.
- `NB-05-O` (Mathilda exit): the owner confirms that one rightmost US-101
  lane drops and the exit ramp widens later. The correction retains five lanes
  up to the gore, sends lane 0 to a one-lane ramp, and widens that ramp near
  its downstream end. The exact widening position is approximate.
- `NB-22-O` (Shoreline exit) and `SB-15-O` (CA-85 South general-purpose
  split): the owner confirms two right-side lanes exit and four continue at
  both nodes. Their saved SUMO connections already match those splits. The
  separate left-side CA-85 express connector exists at `SB-12-O`. Its
  [FasTrak access rules](https://www.bayareafastrak.org/en/toll-locations/express-lanes-101-sr85-santa-clara.shtml)
  are known; the model still needs tag/occupancy/toll state to evaluate use.
- `NB-28-I`, `SB-11-O`, and `SB-16-I` are tied to the two Shoreline
  importer warnings accepted with limits in the
  [warning review](us101-importer-warning-review.md).
- The Mathilda/SR-237 and West Maude/SR-237 warning edges are outside the
  bounded mainline branch ledger. Their warning dispositions are recorded in
  the same warning review; the West Maude warning is excluded only from the
  current mainline/H0 acceptance scope.

The 36 unused branch entries are outside the frozen H0 demand routes. Before
a later experiment uses one, check its full route and any relevant express
eligibility or signal behavior. Obtain plans only when the available sources
leave a consequential contradiction. The captured aerials and 2018 plans
establish movement existence and interchange context, not current
lane-index sign-off.

## Cross-cutting decisions for future route expansion

The first location pass establishes movement identity, **not** lane sign-off.
The OSM source tags `NB-22-O` as a two-lane exit to Shoreline Boulevard and
`NB-26-O` as a one-lane exit to Old Middlefield Way. The 2018 VTA/Caltrans
pavement-delineation plan PD-19 draws distinct Shoreline entrance and Old
Middlefield exit movements; its age precludes a current lane-count conclusion.
`NB-28-I` traces backward through `690599564#0`, tagged for US-101 North / Old
Middlefield Way, to the North Shoreline/La Avenida side of the interchange.
The saved satellite captures locate that loop and the `SB-11-O` loop carrying
warning edge `348360455`; the capture date is not a guarantee of the underlying
imagery date. Neither image resolves SUMO's parallel-movement reduction or
7.99 m sharp-turn warning. These rows have no H0 demand; their modeled links
are accepted for M2 with the limits recorded in the warning review. A scenario
that depends on detailed Shoreline ramp operation needs focused validation.

A separate Playwright pair centered on `NB-28-I` at
[37.4165909, -122.0862390](https://www.google.com/maps/@37.4165909,-122.0862390,19z/data=!3m1!1e3)
and its upstream edge start at
[37.4148066, -122.0831324](https://www.google.com/maps/@37.4148066,-122.0831324,20z/data=!3m1!1e3)
is saved under ignored `outputs/map_audit/` with timestamped JSON metadata.
The upstream view shows a separated right-side ramp/acceleration pavement;
the downstream junction view shows the US-101 carriageway near the Permanente
Creek Trail bridge but no unambiguous ramp nose. SUMO represents the last
side edge `685973436` as one lane over 337.71 m before joining the through
route. This supports the *location* of a long merge path; it does not prove
that its simulated join point, receiving lane, or lane-drop location matches
 the current paint. Retain `NB-28-I` as a documented approximation.

The next location pass covers `NB-30-O`/`NB-31-I` at Rengstorff–Amphitheater
and `NB-32-O`/`NB-33-I` at San Antonio. OSM tags the first exit for
Amphitheater Parkway/Rengstorff Avenue and the second for San Antonio Road;
their paired entrances trace from nearby surface approaches. Historical VTA
plans PD-22 and PD-25 draw corresponding northbound exit/entrance movements.
The [Rengstorff](https://www.google.com/maps/@37.4208,-122.0918,19z/data=!3m1!1e3)
and [San Antonio](https://www.google.com/maps/@37.428,-122.101,19z/data=!3m1!1e3)
Playwright views show the physical interchange ramps at the expected
locations. Close views centered on the four SUMO transition coordinates are
also retained under ignored `outputs/map_audit/`; several show only the
freeway because a long modeled connector begins or ends away from its visible
gore. Thus the image/plan match is for **movement existence and general
location**, not a current lane-link or lane-count approval. All four rows are
excluded from the frozen H0 route set.

- At 401948, compare only the four user-identified through lanes for the
  mainline total; channel 5 is provisionally assigned to the short weaving
  lane. Keep the five-lane sensitivity network as a separate candidate.
- At 402377, use SUMO lane indices 1–4 as a provisional flow-based mapping;
  the three-seed comparison does not identify the physical loop wiring.
- At 401507, compare PeMS with SUMO lanes 1–6 and exclude lane 0, which
  branches to the exit. Continue reviewing the synthetic transition's lane
  geometry as part of the Shoreline ramp audit.
- Review the Shoreline sharp-radius/parallel-movement warnings and the
  SR-237 approach warning movements before adding their ramp demand. The
  generated side paths place warning edge `348360455` in `SB-11-O` and
  `SB-16-I`, and `690599564#0` in `NB-28-I`; the two SR-237 approach warning
  edges did not appear in this bounded branch trace, so check them separately.
- Check current express/HOV lane permissions. The current importer and this
  passenger-legal trace do not certify occupancy or toll eligibility.
- The 2026-10-04 owner review resolves the side of the Shoreline and CA-85
  general-purpose splits: two right-side lanes leave and four continue in
  each case. It also resolves Mathilda's drop as one rightmost freeway lane
  that widens later on the ramp. The saved correction patch implements that
  one-lane gore. The approximate Mathilda widening location is adequate for
  the current H0 routes; refine it if downstream ramp operations are studied.
  The Rengstorff follow-up confirms an immediate exit pocket,
  matching the modeled 21.52 m segment. The CA-85 left express
  connector is a separate movement from the general-purpose split.
