# SR-85 station 402920 lane-count sensitivity

## Visual and metadata evidence

PeMS metadata for station 402920 reports an OR detector on SR-85 southbound,
two lanes, and the name “Shoreline Blvd on diag.” The user-provided satellite
view at `37.40848, -122.070905` places the detector on a separate diagonal
connector beside US-101. It visually supports a two-lane connector near the
detector. The screenshot does not conclusively identify the exact lane-to-lane
connection where the connector joins US-101, so the merge remains a hypothesis.

The OSM-derived SUMO network models connector edge `11479095` as one lane. The
one-lane case remains the existing comparison candidate; the alternate network
is built under `outputs/us101_corridor/sr85_two_lane_shared_merge/` and does not
replace the baseline network.

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
