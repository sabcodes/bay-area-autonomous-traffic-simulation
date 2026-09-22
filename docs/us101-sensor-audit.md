# US-101 PeMS sensor audit

## Purpose

These are the candidate District 4, northbound US-101 mainline detector
stations automatically selected inside the corrected SR-237-to-Oregon-
Expressway/Page-Mill study boundary.
They were derived from the August 27 and October 16, 2025 PeMS metadata
snapshots. The current provisional morning report intentionally uses only the
nine earlier reviewed candidates; six of those supplied qualifying readings.
The ten unsure locations are excluded until follow-up review.

## What to check

Open each map link and check only three things:

1. It is on northbound US-101, not on a ramp or a nearby road.
2. It lies between the SR-237 interchange and Page Mill Road.
3. Its recorded lane count looks plausible for that location.

Mark a row **keep**, **exclude**, or **unsure**. An **unsure** row is fine; it
means we check it more carefully before calibration.

| ID | PeMS name | Lanes | Map | Decision | Notes |
| --- | --- | ---: | --- | --- | --- |
| 401507 | SHORELINE BLVD | 6 | [map](https://www.openstreetmap.org/?mlat=37.412677&mlon=-122.079539#map=16/37.412677/-122.079539) | Provisional keep | Looks about right. |
| 401534 | MOFFETT BLVD | 4 | [map](https://www.openstreetmap.org/?mlat=37.407511&mlon=-122.065278#map=16/37.407511/-122.065278) | Unsure | Needs follow-up. |
| 401948 | MOFFETT BLVD | 5 | [map](https://www.openstreetmap.org/?mlat=37.409514&mlon=-122.071728#map=16/37.409514/-122.071728) | Unsure | Needs follow-up. |
| 401949 | SHORELINE BLVD RM-N-COLL | 5 | [map](https://www.openstreetmap.org/?mlat=37.414582&mlon=-122.083368#map=16/37.414582/-122.083368) | Provisional keep | Looks about right. |
| 401996 | FAIR OAKS | 4 | [map](https://www.openstreetmap.org/?mlat=37.396411&mlon=-122.015716#map=16/37.396411/-122.015716) | Provisional keep | Looks about right. |
| 401997 | MATHILDA AVE | 4 | [map](https://www.openstreetmap.org/?mlat=37.398829&mlon=-122.026742#map=16/37.398829/-122.026742) | Provisional keep | Looks about right. |
| 401998 | Ellis Street rm-n-diag | 4 | [map](https://www.openstreetmap.org/?mlat=37.404178&mlon=-122.051070#map=16/37.404178/-122.051070) | Provisional keep | Looks about right. |
| 402370 | 4A5324 LOC 70 | 4 | [map](https://www.openstreetmap.org/?mlat=37.395920&mlon=-122.013438#map=16/37.395920/-122.013438) | Provisional keep | Appears consistent with the Moffett-area sensors. |
| 402372 | 4A5324 loc 72 | 4 | [map](https://www.openstreetmap.org/?mlat=37.405470&mlon=-122.055924#map=16/37.405470/-122.055924) | Provisional keep | Looks about right. |
| 402376 | 4A5324 LOC 75 | 6 | [map](https://www.openstreetmap.org/?mlat=37.435945&mlon=-122.109246#map=16/37.435945/-122.109246) | Unsure | Added by corrected northern boundary. |
| 402377 | 4A5324 loc 76 | 4 | [map](https://www.openstreetmap.org/?mlat=37.440393&mlon=-122.113925#map=16/37.440393/-122.113925) | Unsure | Added by corrected northern boundary. |
| 402379 | 4A5324 LOC 77 | 4 | [map](https://www.openstreetmap.org/?mlat=37.445961&mlon=-122.119760#map=16/37.445961/-122.119760) | Unsure | Added by corrected northern boundary. |
| 402380 | 4A5324 loc 78 | 4 | [map](https://www.openstreetmap.org/?mlat=37.451442&mlon=-122.125642#map=16/37.451442/-122.125642) | Unsure | Near Oregon Expressway/Embarcadero endpoint. |
| 404522 | NB 101 to WB 237 I/C | 4 | [map](https://www.openstreetmap.org/?mlat=37.400972&mlon=-122.036547#map=16/37.400972/-122.036547) | Provisional keep | Looks about right. |
| 404529 | San Francisquito Cr | 5 | [map](https://www.openstreetmap.org/?mlat=37.453280&mlon=-122.128420#map=16/37.453280/-122.128420) | Unsure | Check whether this is beyond the intended endpoint. |
| 422116 | oppo S of Clarke Ave | 5 | [map](https://www.openstreetmap.org/?mlat=37.456467&mlon=-122.133857#map=16/37.456467/-122.133857) | Unsure | Likely beyond the intended endpoint; verify. |
| 425545 | San Antonio Rd rm-n-coll | 5 | [map](https://www.openstreetmap.org/?mlat=37.428818&mlon=-122.101776#map=16/37.428818/-122.101776) | Unsure | Check collector/mainline context. |
| 425697 | Embarcadero Rd rm-n-coll | 4 | [map](https://www.openstreetmap.org/?mlat=37.450295&mlon=-122.124287#map=16/37.450295/-122.124287) | Unsure | Check collector/mainline context at endpoint. |
| 425892 | Rengstorff Ave rm-n-diag | 5 | [map](https://www.openstreetmap.org/?mlat=37.421844&mlon=-122.093417#map=16/37.421844/-122.093417) | Provisional keep | Looks about right. |

## Interpretation caution

PeMS labels with `rm` or `diag` can still be reported as mainline (`ML`) in
the metadata. Do not automatically exclude them, but inspect those locations
especially carefully.
