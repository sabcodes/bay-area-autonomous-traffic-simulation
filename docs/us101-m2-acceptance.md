# M2 US-101 corridor network acceptance

**Decision date:** 2026-10-04
**Decision:** M2 is complete for the versioned US-101 corridor network at the
project's practical accuracy standard. The 40 branch junctions and both
through routes have been reviewed; the current H0 route set has also run.
This is not a claim that every road in the wider OSM extract matches current
as-built striping.

The project-level acceptance bar is a plausible route and lane layout in the
available map evidence, reproducible corrections, connected approved routes,
and no route failures in the baseline run. Exact loop wiring, surveyed
as-built sheets, and perfect calibration are not required to close M2.

## Accepted route set and evidence

The accepted H0 file has five explicit routes: the northbound US-101 through
route, the measured Mathilda off-ramp, and the measured Mathilda, Moffett, and
San Antonio on-ramps. The [40-junction checklist](us101-ramp-review-checklist.md)
records all 40 branch reviews: four carry H0 demand (`NB-05-O`, `NB-06-I`,
`NB-19-I`, and `NB-33-I`) and 36 have no H0 demand. A route-file audit confirms
the four active side edges occur in the five H0 routes and none of the other
36 side edges does. The fixed route definitions cannot select extra branches
by shortest-path rerouting.

The directed network audit covers 37 northbound and 36 southbound through
edges and all 40 adjacent branch junctions. Every branch has a
passenger-legal lane link; ordinary ramps join or leave on the right, three
two-lane exits use the two rightmost lanes, and two separate express
connectors use the leftmost lane. The Rengstorff entrance also links to the
nearest continuing lane from its short pocket. No contradictory branch-side
connection was found. The bounded side-path search reaches 18
audited-through, 14 other-motorway, and 86 surface/other endpoints, with no
graph-boundary, depth-limit, or cycle ending. The saved 2026-09-25 aerial
captures locate all 40 junctions; OSM tags, generated lane links, historical
VTA plans, and the owner's lane checks supply the movement decisions recorded
in the [network audit](us101-network-audit.md). Image limitations and
modeled approximations are in the checklist.

The accepted network is produced from the versioned OSM extract and the versioned
[edge patch](../network/us101_corridor/patches/mathilda_rengstorff.edg.xml) and
[connection patch](../network/us101_corridor/patches/mathilda_rengstorff.con.xml).
The [source snapshot](../data/osm/us101_corridor.osm.xml) is OpenStreetMap data
under ODbL; its [provenance](../data/osm/us101_corridor.osm.provenance.json)
records the Overpass query and download time. The generated network SHA-256 is
`13103c0b31d22dff15159b56e5ba03f0becd9594868c4cdfeac60497e86b9bc6`.
The patch preserves one rightmost Mathilda lane dropping into a one-lane exit
that widens downstream and a one-lane Rengstorff entrance feeding a 21.52 m
immediate-exit pocket. Shoreline northbound and CA-85 southbound each send
their two rightmost lanes to the exit while four continue. The separate
left-side CA-85 connector is retained but excluded from H0.

The rebuilt network, regenerated lane ledger, and H0 seeds 41–43 were run
against this SHA. All three H0 runs completed 13,482 vehicles without route,
teleport, collision, emergency-braking, or SUMO warning entries. This is
network/route acceptance evidence; Shoreline flow and speed errors remain M3
calibration work. The H0 report is saved at
`outputs/us101_corridor/h0_multiseed_report.json`.

## Warning and permission dispositions

The raw OSM import still warns about Shoreline edges `348360455` and
`690599564#0` and the Mathilda/SR-237 edge `941192341`; the second conversion
still reports the sharp Shoreline radius. These three are reviewed and
accepted as [documented modeling approximations](us101-importer-warning-review.md).
The connected movements are retained because the evidence does not support
deleting them or forcing a junction join. West Maude/SR-237 edge `19146053#0`
remains outside the US-101 mainline acceptance area. None of these edges, nor
the left-side CA-85 connector `38083577`, is on an H0 route. A future
experiment sensitive to these movements should check its route behavior and
lane use before interpreting the result.

For managed lanes, the current H0 passenger type represents vehicles eligible
to use the Santa Clara US-101/SR-85 express lanes: a valid FasTrak tag during
weekday tolling hours, with solo drivers allowed at full toll; outside those
hours all vehicles may use them. This is a conditional route-legality
assumption based on the [current FasTrak rules](https://www.bayareafastrak.org/en/toll-locations/express-lanes-101-sr85-santa-clara.shtml).
The simulation has no tag, occupancy, or toll-choice state, so lane use and
observed market share are not legally or behaviorally calibrated. That is an
M3/M7 modeling limitation, not a missing network connection.

## Change gate

The accepted M2 scope is the US-101 corridor network and its 40 reviewed
branch junctions. Before adding flow, rerouting, or a controller to a branch
outside H0, check the full scenario route, managed-lane eligibility, and any
warning approximation that matters to that experiment. Seek agency plans
only if a material contradiction remains. Do not interpret provisional PeMS
detector-to-lane choices as loop-wiring proof. Southbound branch demand is
absent from H0. A later network edit requires a new network hash, branch
ledger, and route check before this acceptance applies to the edited network.
