# US-101 PeMS sensor audit

## Purpose

These are the candidate District 4, northbound US-101 mainline detector
stations automatically selected inside the corrected SR-237-to-Oregon-
Expressway/Page-Mill study boundary.
They were derived from the August 27 and October 16, 2025 PeMS metadata
snapshots. The current provisional morning report uses the ten accepted
mainline candidates; data availability determines which supply qualifying
readings. Eight unsure northern locations remain excluded until follow-up
review, and one Shoreline collector location is explicitly excluded.

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
| 401534 | MOFFETT BLVD | 4 | [map](https://www.openstreetmap.org/?mlat=37.407511&mlon=-122.065278#map=16/37.407511/-122.065278) | Provisional keep | Close zoom places marker on northbound mainline. |
| 401948 | MOFFETT BLVD | 5 | [map](https://www.openstreetmap.org/?mlat=37.409514&mlon=-122.071728#map=16/37.409514/-122.071728) | Keep location; mapping blocked | Close zoom places marker on northbound mainline, but PeMS reports five lanes and OSM/SUMO edge `617335302` has four. |
| 401949 | SHORELINE BLVD RM-N-COLL | 5 | [map](https://www.openstreetmap.org/?mlat=37.414582&mlon=-122.083368#map=16/37.414582/-122.083368) | Exclude | Close zoom places marker on separated collector/ramp roadway. |
| 401996 | FAIR OAKS | 4 | [map](https://www.openstreetmap.org/?mlat=37.396411&mlon=-122.015716#map=16/37.396411/-122.015716) | Provisional keep | Looks about right. |
| 401997 | MATHILDA AVE | 4 | [map](https://www.openstreetmap.org/?mlat=37.398829&mlon=-122.026742#map=16/37.398829/-122.026742) | Provisional keep | Looks about right. |
| 401998 | Ellis Street rm-n-diag | 4 | [map](https://www.openstreetmap.org/?mlat=37.404178&mlon=-122.051070#map=16/37.404178/-122.051070) | Provisional keep | Close zoom confirms marker on northbound mainline. |
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

## Flow-balance result

The audited station order is 402370, 401996, 401998, 402372, 401534, 401948,
and 401507. Five adjacent comparisons are currently usable, with mean changes
of +33, +258, +14, +330, and +1,529 vehicles/hour. Stations 401998 and 402372 map to the
same uninterrupted SUMO edge but differ by -196 vehicles/hour; that is treated
as detector disagreement rather than ramp demand. The user's PeMS screenshots
confirm the US-101 northbound location in Mountain View and detector lanes 1–5.
The October 1 five-minute export independently shows five active lane
measurements for this ML station. Its roadway inventory identifies an HOV lane,
and [Caltrans describes a buffered managed/HOT lane between Moffett Boulevard
and Old Middlefield Way](https://dot.ca.gov/-/media/dot-media/programs/traffic-operations/documents/hov/2026-ca-hov-facilities-degradation-action-plan-a11y.pdf).
We therefore accept the five-lane PeMS observation as a full cross-section for
empirical flow balance. The four-lane OSM/SUMO edge remains a separate
simulation-geometry gap, reported as a note rather than used to discard the
observed flows. These residuals are net corridor changes, not measurements of
individual ramps; assign them to missing-ramp demand only after auditing the
intervening entrances and exits.
