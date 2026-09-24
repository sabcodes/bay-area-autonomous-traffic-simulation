# SR-85 station 402920 lane-count sensitivity

## Visual and metadata evidence

PeMS metadata for station 402920 reports an OR detector on SR-85 southbound,
two lanes, and the name “Shoreline Blvd on diag.” The user-provided map and
aerial imagery at `37.40848, -122.070905` place the detector in the
SR-85/US-101 interchange area, but do not identify its exact ramp path. VTA's
environmental assessment describes both an HOV-only direct connector and a
separate general-purpose northbound SR-85-to-US-101 ramp at the north end of
SR-85. Thus, the station cannot be assigned to the OSM HOV connector based on
proximity alone. An additional aerial review
([Google Maps](https://www.google.com/maps/@37.40848,-122.070905,80m/data=!3m1!1e3),
checked 2026-09-24) did not resolve the ramp identity or painted merge lanes.
The lane-count and receiving-lane cases below remain sensitivities, not a
verified representation of the station's road.

The OSM-derived SUMO network models HOV connector edge `11479095` as one lane.
The one-lane case remains the mapped-network comparison candidate; the
alternate network is built under
`outputs/us101_corridor/sr85_two_lane_shared_merge/` and does not replace the
baseline network. Neither is accepted as station 402920's actual path.

## Merge hypotheses tested

The connector is fed by lanes 3 and 4 of edge `1343445177`. Its existing
one-lane connection feeds US-101 lane 5 of edge `509747406`.

An adjacent-lane split that mapped connector lanes 0 and 1 to US-101 lanes 4
and 5 produced about 744 seconds of average waiting for the station 402920
vehicles in seed 41, with a maximum over 2,200 seconds. That mapping was
rejected as implausible for this model and is not used by the current config.

The current sensitivity adds connector lane 1 and maps both connector lanes to
the existing dedicated receiving lane 5. This two-to-one merge hypothesis ran
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
performance. The current merge lets both ramp lanes enter one reserved freeway
lane; it is a convenient and stable sensitivity, not a verified representation
of the painted merge markings.

## Next audit

Before adopting either lane topology, review aerial lane markings or Caltrans
plans at the actual connector exit and confirm whether the two lanes remain
separate, taper to one, or enter adjacent US-101 lanes. Keep this scenario
separate from controller experiments until that geometry is reconciled.
