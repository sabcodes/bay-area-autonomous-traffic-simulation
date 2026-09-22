# US-101 network audit checklist

`outputs/us101_corridor/us101_corridor.net.xml` is an automatically imported
draft. Do not use it for a performance claim until this checklist is completed.

## Source record

- Use the adjacent `data/osm/us101_corridor.osm.provenance.json` to identify
  the boundary, source endpoint, timestamp, and exact query used.
- The OSM XML itself is intentionally untracked because it is downloaded data.
- Record any later re-download as a new provenance entry before replacing it.

## Review in SUMO

Open the network with the SUMO graphical tools installed in `.venv` and inspect
both directions, even though the first experiment will focus on northbound.

1. Verify US-101 mainline lane count and speed on every segment from SR-237 to
   Page Mill Road.
2. Trace each on-ramp and off-ramp, especially Shoreline Boulevard, Ellis
   Street, Mathilda Avenue, and Page Mill Road; confirm entry/exit connectivity.
3. Check that merge and diverge geometry leaves realistic acceleration and
   deceleration distance.
4. Review every importer warning involving an affected freeway or ramp edge.
   A warning is a review task, not something to ignore globally.
5. Confirm no unintended turnarounds, missing lanes, detached road pieces, or
   impossible lane changes remain on candidate routes.

## Make corrections reproducible

- Store hand-authored changes under `network/us101_corridor/patches/`.
- Describe each change, its source evidence, and the edge/junction it changes.
- Rebuild the network and rerun this checklist whenever OSM data or a patch
  changes.

## Exit condition

The network is ready for demand calibration only after a reviewer can trace
representative SR-237-to-Page-Mill and ramp-to-mainline routes without a broken
or implausible movement, and every remaining warning has an explicit decision.
