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

Every row remains **open** until it has a dated source view or as-built plan,
an OSM-to-SUMO movement comparison, an explicit lane/permission decision,
and a recorded resolution. In particular, a visually plausible map tile does
not prove the exact current lane index or detector coverage. If the evidence
cannot settle one, keep it open and exclude any experiment requiring that
claim. Existing H0 smoke-test success is not an M2 sign-off.

For each row, review the **whole traced path**, not just its first edge:

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
ledger. All states below are open; this table is an inventory, not approval.

| Review ID | Through-route transition | Side edge | State |
| --- | ---: | --- | --- |
| NB-00-I | 0 | `509747285` | Open |
| NB-05-O | 5 | `9080606` | Open |
| NB-06-I | 6 | `509747339` | Open |
| NB-09-O | 9 | `9545875` | Open |
| NB-10-I | 10 | `509747350` | Open |
| NB-13-O | 13 | `20113705` | Open |
| NB-14-I | 14 | `281956182` | Open |
| NB-17-O | 17 | `394385426` | Open |
| NB-19-I | 19 | `777748240` | Open |
| NB-22-O | 22 | `5005672` | Located; lane review open |
| NB-23-I | 23 | `394387883` | Open |
| NB-24-I | 24 | `11479095` | Open |
| NB-26-O | 26 | `30990690` | Located; lane review open |
| NB-28-I | 28 | `685973436` | Located; lane review open |
| NB-30-O | 30 | `9245798` | Located; lane review open |
| NB-31-I | 31 | `8927566` | Located; lane review open |
| NB-32-O | 32 | `4370043` | Located; lane review open |
| NB-33-I | 33 | `9739842#1` | Located; lane review open |
| NB-35-O | 35 | `13100980` | Open |
| SB-00-I | 0 | `27086204#3` | Open |
| SB-02-O | 2 | `8925871` | Open |
| SB-04-O | 4 | `125299850` | Open |
| SB-05-I | 5 | `534473511` | Open |
| SB-06-O | 6 | `8923902` | Open |
| SB-07-I | 7 | `394369030` | Open |
| SB-09-I | 9 | `304467430` | Open |
| SB-11-O | 11 | `8924695` | Located; warning review open |
| SB-12-O | 12 | `38083577` | Open |
| SB-15-O | 15 | `8924268` | Open |
| SB-16-I | 16 | `949062561` | Open |
| SB-17-O | 17 | `394385424#0` | Open |
| SB-18-I | 18 | `509747360` | Open |
| SB-21-O | 21 | `394382945` | Open |
| SB-22-I | 22 | `281956185` | Open |
| SB-25-O | 25 | `185252028` | Open |
| SB-26-I | 26 | `8927500#0` | Open |
| SB-28-O | 28 | `8923686` | Open |
| SB-29-I | 29 | `517246480` | Open |
| SB-31-I | 31 | `509747343` | Open |
| SB-34-O | 34 | `8927783` | Open |

## Cross-cutting decisions still open

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
7.99 m sharp-turn warning. These four rows remain open for lane-level review.

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
 the current paint. Keep `NB-28-I` open.

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
location**, not a current lane-link or lane-count approval. All four rows
remain open.

- Resolve the 401948 five-detector versus four-lane baseline mismatch without
  silently promoting the provisional five-lane sensitivity scenario.
- Resolve whether PeMS 402377's four detectors cover all five modeled lanes.
- Locate PeMS 401507 relative to the Shoreline entrance and Old Middlefield
  exit seven-lane synthetic transition.
- Review the Shoreline sharp-radius/parallel-movement warnings and the
  SR-237 approach warning movements before adding their ramp demand. The
  generated side paths place warning edge `348360455` in `SB-11-O` and
  `SB-16-I`, and `690599564#0` in `NB-28-I`; the two SR-237 approach warning
  edges did not appear in this bounded branch trace, so check them separately.
- Check current express/HOV lane permissions. The current importer and this
  passenger-legal trace do not certify occupancy or toll eligibility.
