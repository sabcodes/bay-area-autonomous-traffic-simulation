# SR-85 station 402920 lane-count sensitivity

## Visual and metadata evidence

PeMS metadata for station 402920 reports an OR detector on SR-85 southbound,
two lanes, and the name “Shoreline Blvd on diag.” Its coordinate is in the
SR-85/US-101 interchange area. The nearest generated SUMO feature is a
two-lane synthetic entrance feeding southbound CA-85 edge `11479094`, about
9.9 m from the station coordinate; the one-lane NB US-101 HOV connector is
about 37.4 m away. Together, PeMS route/direction/type and nearest graph
geometry support treating 402920 as a southbound SR-85 entrance outside the NB
study path. VTA documents an HOV-only direct connector and a separate
general-purpose northbound SR-85-to-US-101 ramp. A Playwright-captured Google
Maps view at [the station coordinate](https://www.google.com/maps/@37.40848,-122.070905,18z/data=!3m1!1e3),
checked 2026-09-24, confirms only the broad interchange location; the lane
markings are not clear enough to determine a taper or exact detector roadway.
Therefore neither prior HOV mapping nor its lane counts represent observed
geometry or demand.

The OSM-derived SUMO network models NB HOV connector edge `11479095` as one
lane. Both scenarios below map southbound station 402920 onto that northbound
edge, so both are now explicitly counterfactual; neither is a mapped-network
comparison using observed NB ramp demand. The alternate network is built under
`outputs/us101_corridor/sr85_two_lane_shared_merge/` and does not replace the
baseline network. Neither is accepted as station 402920's actual path.

## Merge hypotheses tested

The connector is fed by lanes 3 and 4 of edge `1343445177`. Its existing
one-lane connection feeds US-101 lane 5 of edge `509747406`.

An adjacent-lane split that mapped connector lanes 0 and 1 to US-101 lanes 4
and 5 produced about 744 seconds of average waiting for the station 402920
vehicles in seed 41, with a maximum over 2,200 seconds. That mapping was
rejected as implausible for this model and is not used by the current config.

The counterfactual sensitivity adds connector lane 1 and maps both connector
lanes to the existing dedicated receiving lane 5. This two-to-one merge ran
with seeds 41, 42, and 43: all 13,800 vehicles completed in each run, station
402920 ramp trips had zero waiting, and the SUMO logs reported no teleports,
collisions, or emergency braking.

## Matched three-seed comparison

Both scenarios use the same complete PeMS dates and seeds.

| Metric | One-lane connector | Two-lane / lane-5 merge |
| --- | ---: | ---: |
| Mean trip time | 382.57 s | 382.72 s |
| Mean trip speed | 58.916 mph | 58.891 mph |
| Mean waiting time | 0.00002 s | 0 s |
| Simulated flow at station 401507 | 4,980.3 veh/h | 4,976.8 veh/h |
| Station 401507 flow MAPE | 30.95% | 31.01% |

The differences are tiny relative to the model’s broader calibration error.
They do not support a claim that the extra ramp lane improves corridor
performance. Because 402920 is likely a southbound SR-85 entrance, these runs
are counterfactual topology/input sensitivities—not calibration evidence for
the NB US-101 connector and not a controller comparison. The two lanes entering
one reserved freeway lane are a convenient, stable hypothetical only.

## Next audit

Before implementing the actual NB connector, obtain a source specific to that
connector (Caltrans/VTA plan or sharper lane-level imagery) and confirm the
lane count, taper, and receiving US-101 lanes. Keep both station-402920 runs
separate from baseline calibration and controller experiments.
