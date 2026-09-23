# Shoreline PeMS ramp identity audit

## Finding

PeMS station IDs **402921 and 402922 are not northbound US-101 ramp detectors**.
The October 16, 2025 PeMS station metadata labels both as freeway 101, direction
`S`, district 4, lane type `FR` and `OR` respectively, at route postmile 48.17
(state postmile 397.843), with identical approximate coordinates
37.409050, -122.071117. Their names are “Shoreline Blvd off” and “Shoreline
Blvd on loop.” These fields identify them as a southbound US-101 off-ramp and
on-ramp pair. The same records are present in the August 27 metadata snapshot.

This resolves the direction question for these IDs: **exclude 402921/402922
from northbound ramp-flow estimation.** It does not identify the exact roadway
path or SUMO edge, because the two stations share one rounded coordinate and
postmile, and metadata names are not surveyed detector locations.

The live PeMS station pages show the same current US-101-S location, CA PM
48.17, coordinate, and lane counts. Their change logs also show older
2011–2014 entries at PM 48.62, coordinate 37.411999, -122.078452, followed by
March 25, 2022 entries at PM 48.17 and the current coordinate. The older PM
48.62 happens to sit near Caltrans' NB Shoreline exit PM 48.60, which can make
the IDs look like NB-ramp evidence if the historical rows are read without
their dates. For the October 2025 observations, the active location is the
post-2022 US-101-S record; the old location must not be used to map these
current counts onto a northbound ramp.

## What the source records say

| PeMS station | Freeway / direction | PeMS lane type / lanes | Postmile | PeMS name | Assessment |
| --- | --- | --- | ---: | --- | --- |
| 402921 | US-101 / S | FR / 1 | 48.17 | Shoreline Blvd off | Southbound US-101 off-ramp detector |
| 402922 | US-101 / S | OR / 2 | 48.17 | Shoreline Blvd on loop | Southbound US-101 on-ramp detector |
| 402920 | SR-85 / S | OR / 2 | R23.82 | Shoreline Blvd on diag | Separate Shoreline-area diagonal detector on southbound SR-85; do not silently relabel it as a US-101 station |
| 401926 | US-101 / S | ML / 4 | 48.17 | Shoreline Blvd rm-s-loop | Nearby southbound US-101 mainline station sharing the same reported coordinate/postmile |
| 401948 | US-101 / N | ML / 5 | 48.21 | Moffett Blvd | Northbound mainline detector just upstream by PeMS postmile |
| 401507 | US-101 / N | ML / 6 | 48.69 | Shoreline Blvd | Northbound mainline detector downstream by PeMS postmile |

The two PeMS metadata snapshots agree on the station IDs, names, route,
direction, type, lane count, postmile, and coordinate. The detector inventory
in `data/pems/metadata/d04_tmdd_meta_2025_10_16.xml` adds one operational
detector for 402921 (detector 413602, lane-number 1) and two operational
detectors for 402922 (413603 lane-number 1; 413604 lane-number 10). Those
inventory lane numbers are metadata identifiers; they do not provide a
georeferenced lane shape or a SUMO edge mapping.

The downloaded five-minute PeMS exports contain records for both stations.
For example, the 2025-10-16 file at 07:00 reports an observed flow for 402922,
whereas the corresponding 402921 aggregate flow/coverage fields are blank.
Blank values mean **unavailable**, not a measured zero. The project's current
`us101_ramp_station_profiles.json` does not include either ID because its
configured ramp-station set excludes them, so it currently publishes no
profile for them.

## Independent official corridor evidence

Caltrans' 2021 notice explicitly lists the **northbound US-101 Shoreline Blvd
Collector (Loop and Diagonal) On-ramp** among its NB US-101 ramp-meter locations.
Caltrans' US-101 exit table places the NB Shoreline Blvd exit at county PM
48.60 and Old Middlefield Way at 48.97. Thus, the northbound Shoreline
interchange ramps are real and lie between mainline stations 401948 (PM 48.21)
and 401507 (PM 48.69), but the two `S`-direction PeMS records 402921/402922 are
not measurements of those northbound ramps.

The local OSM extract and generated SUMO network remain the geometry sources
for this project. Their topologies can be inspected, but the PeMS metadata
coordinate alone cannot select which nearby path is 402921/402922. In
particular, do not infer that a similarly named OSM/SUMO Shoreline edge is the
same physical ramp just from its name or nearest-node distance.

## Consequence for the flow residual

Neither 402921's off-ramp value nor 402922's on-ramp value can be subtracted
from or added to the **northbound** 401948→401507 net flow change. Caltrans' NB
Shoreline ramp-meter notice confirms a northbound entrance in the interval,
but those two southbound PeMS records are not valid NB ramp counts. A separate
candidate, 402920, measures southbound SR-85 on-ramp flow at about 128.5
vehicles/hour over 12 common days. OSM confirms a connected HOV route into NB
US-101, but the detector-to-lane mapping is unverified; 402920 cannot by itself
close the balance. The date-aligned mainline net change is +1,621.625
vehicles/hour over 12 common days (288 morning intervals), replacing the
earlier +1,529 estimate that used unmatched date sets.

## Next mapping step and human check

Available local PeMS text metadata and TMDD inventory are enough to settle the
directional identity and rule out IDs 402921/402922 for this NB study. They are
not enough to place either detector on a particular physical ramp, or to map a
northbound Shoreline detector to a SUMO edge. Before using 402920 as NB HOV
connector demand, visually compare its PeMS station configuration and two
detector lanes with the single-lane OSM/SUMO connector path. A screenshot or
station configuration export is still useful to verify that mapping. No extra
visual confirmation is needed to reject 402921/402922 as northbound US-101
counts.

## Primary sources

- Local PeMS station metadata: `data/pems/metadata/d04_text_meta_2025_10_16.txt`
  (rows 743, 979–980, 1465–1466) and
  `data/pems/metadata/d04_text_meta_2025_08_27.txt` (same station rows).
- Local PeMS detector inventory:
  `data/pems/metadata/d04_tmdd_meta_2025_10_16.xml` (station IDs 402921 and
  402922) and the 2025-08-27 snapshot.
- Local PeMS five-minute export: `data/pems/d04_text_station_5min_2025_10_16.txt.gz`
  (records for 402921 and 402922); the 25 downloaded daily exports are listed
  in `outputs/pems_calibration/us101_ramp_station_profiles.json`.
- Caltrans District 4, “On-Ramp Meters to be Activated on Northbound Interstate
  101,” June 4, 2021: <https://dot.ca.gov/caltrans-near-me/district-4/d4-news/2021-06-04-on-ramp-meters-to-be-activated-on-northbound-interstate-101>.
- Live PeMS station configuration pages: [402921](https://pems.dot.ca.gov/?station_id=402921&dnode=VDS&content=sta_cfg) and [402922](https://pems.dot.ca.gov/?station_id=402922&dnode=VDS&content=sta_cfg). Their current-location and change-log panels confirm the active location and March 25, 2022 relocation entries described above.
- Caltrans, California Numbered Exit Uniform System, US-101 exits, December
  2024: <https://dot.ca.gov/-/media/dot-media/programs/safety-programs/documents/exit/202412-calnexus-us-101-a11y.pdf>.
- OSM source snapshot provenance:
  `data/osm/us101_corridor.osm.provenance.json` (retrieved from Overpass;
  source snapshot `data/osm/us101_corridor.osm.xml`).
- Generated SUMO topology:
  `outputs/us101_corridor/us101_corridor.net.xml`.
