# US-101 PeMS sensor audit

## Purpose

These are the candidate District 4, northbound US-101 mainline detector
stations automatically selected inside the SR-237-to-Page-Mill study boundary.
They were derived from the August 27 and October 16, 2025 PeMS metadata
snapshots. The October five-minute files contained usable morning readings for
8 of the 11 candidates.

## What to check

Open each map link and check only three things:

1. It is on northbound US-101, not on a ramp or a nearby road.
2. It lies between the SR-237 interchange and Page Mill Road.
3. Its recorded lane count looks plausible for that location.

Mark a row **keep**, **exclude**, or **unsure**. An **unsure** row is fine; it
means we check it more carefully before calibration.

| ID | PeMS name | Lanes | Map | Decision | Notes |
| --- | --- | ---: | --- | --- | --- |
| 401507 | SHORELINE BLVD | 6 | [map](https://www.openstreetmap.org/?mlat=37.412677&mlon=-122.079539#map=16/37.412677/-122.079539) |  |  |
| 401534 | MOFFETT BLVD | 4 | [map](https://www.openstreetmap.org/?mlat=37.407511&mlon=-122.065278#map=16/37.407511/-122.065278) |  |  |
| 401948 | MOFFETT BLVD | 5 | [map](https://www.openstreetmap.org/?mlat=37.409514&mlon=-122.071728#map=16/37.409514/-122.071728) |  |  |
| 401949 | SHORELINE BLVD RM-N-COLL | 5 | [map](https://www.openstreetmap.org/?mlat=37.414582&mlon=-122.083368#map=16/37.414582/-122.083368) |  |  |
| 401996 | FAIR OAKS | 4 | [map](https://www.openstreetmap.org/?mlat=37.396411&mlon=-122.015716#map=16/37.396411/-122.015716) |  |  |
| 401997 | MATHILDA AVE | 4 | [map](https://www.openstreetmap.org/?mlat=37.398829&mlon=-122.026742#map=16/37.398829/-122.026742) |  |  |
| 401998 | Ellis Street rm-n-diag | 4 | [map](https://www.openstreetmap.org/?mlat=37.404178&mlon=-122.051070#map=16/37.404178/-122.051070) |  |  |
| 402370 | 4A5324 LOC 70 | 4 | [map](https://www.openstreetmap.org/?mlat=37.395920&mlon=-122.013438#map=16/37.395920/-122.013438) |  |  |
| 402372 | 4A5324 loc 72 | 4 | [map](https://www.openstreetmap.org/?mlat=37.405470&mlon=-122.055924#map=16/37.405470/-122.055924) |  |  |
| 404522 | NB 101 to WB 237 I/C | 4 | [map](https://www.openstreetmap.org/?mlat=37.400972&mlon=-122.036547#map=16/37.400972/-122.036547) |  |  |
| 425892 | Rengstorff Ave rm-n-diag | 5 | [map](https://www.openstreetmap.org/?mlat=37.421844&mlon=-122.093417#map=16/37.421844/-122.093417) |  |  |

## Interpretation caution

PeMS labels with `rm` or `diag` can still be reported as mainline (`ML`) in
the metadata. Do not automatically exclude them, but inspect those locations
especially carefully.
