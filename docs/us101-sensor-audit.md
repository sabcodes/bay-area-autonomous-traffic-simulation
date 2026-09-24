# US-101 PeMS sensor audit

## Purpose

These are the candidate District 4, northbound US-101 mainline detector
stations automatically selected inside the SR-237-to-Oregon-Expressway/Page
Mill study boundary. They were derived from the August 27 and October 16, 2025
PeMS metadata snapshots. The endpoint is the Oregon Expressway interchange at
US-101 county postmile 52.17 in Caltrans' December 2024 exit table. Thirteen
stations are accepted as corridor mainline cross-sections; five candidates are
excluded as beyond the endpoint or collector locations, and one additional
station is held out because its through-mainline coverage is ambiguous. The
accepted inventory is separate from the smaller subset used by the existing
draft calibration scenario.

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
| 401948 | MOFFETT BLVD | 5 | [map](https://www.openstreetmap.org/?mlat=37.409514&mlon=-122.071728#map=16/37.409514/-122.071728) | Accept PeMS cross-section; model gap remains | Five active PeMS lane measurements on the northbound mainline; SUMO maps four lanes on edge `617335302`. |
| 401949 | SHORELINE BLVD RM-N-COLL | 5 | [map](https://www.openstreetmap.org/?mlat=37.414582&mlon=-122.083368#map=16/37.414582/-122.083368) | Exclude | Close zoom places marker on separated collector/ramp roadway. |
| 401996 | FAIR OAKS | 4 | [map](https://www.openstreetmap.org/?mlat=37.396411&mlon=-122.015716#map=16/37.396411/-122.015716) | Provisional keep | Looks about right. |
| 401997 | MATHILDA AVE | 4 | [map](https://www.openstreetmap.org/?mlat=37.398829&mlon=-122.026742#map=16/37.398829/-122.026742) | Provisional keep | Looks about right; no qualifying 07:00–08:59 observations in the downloaded files. |
| 401998 | Ellis Street rm-n-diag | 4 | [map](https://www.openstreetmap.org/?mlat=37.404178&mlon=-122.051070#map=16/37.404178/-122.051070) | Provisional keep | Close zoom confirms marker on northbound mainline. |
| 402370 | 4A5324 LOC 70 | 4 | [map](https://www.openstreetmap.org/?mlat=37.395920&mlon=-122.013438#map=16/37.395920/-122.013438) | Provisional keep | Appears consistent with the Moffett-area sensors. |
| 402372 | 4A5324 loc 72 | 4 | [map](https://www.openstreetmap.org/?mlat=37.405470&mlon=-122.055924#map=16/37.405470/-122.055924) | Provisional keep | Looks about right. |
| 402376 | 4A5324 LOC 75 | 6 | [map](https://www.openstreetmap.org/?mlat=37.435945&mlon=-122.109246#map=16/37.435945/-122.109246) | Accept | PM 51.0 is before endpoint PM 52.17; nearest SUMO edge `700010299` is a six-lane US-101 motorway. No qualifying 07:00–08:59 observations in the downloaded files. |
| 402377 | 4A5324 loc 76 | 4 | [map](https://www.openstreetmap.org/?mlat=37.440393&mlon=-122.113925#map=16/37.440393/-122.113925) | Accept with lane caveat | PM 51.4 is before endpoint; nearest SUMO edge `861090931` is a five-lane US-101 motorway. PeMS reports four lanes and has qualifying data on 13 dates; preserve the model/data lane mismatch. |
| 402379 | 4A5324 LOC 77 | 4 | [map](https://www.openstreetmap.org/?mlat=37.445961&mlon=-122.119760#map=16/37.445961/-122.119760) | Accept | PM 51.9 is before endpoint; nearest SUMO edge `361615812` is a four-lane US-101 motorway. No qualifying 07:00–08:59 observations in the downloaded files. |
| 402380 | 4A5324 loc 78 | 4 | [map](https://www.openstreetmap.org/?mlat=37.451442&mlon=-122.125642#map=16/37.451442/-122.125642) | Exclude | PM 52.4 is beyond Oregon Expressway endpoint PM 52.17. |
| 404522 | NB 101 to WB 237 I/C | 4 | [map](https://www.openstreetmap.org/?mlat=37.400972&mlon=-122.036547#map=16/37.400972/-122.036547) | Provisional keep | SUMO match is on a four-lane motorway; no qualifying 07:00–08:59 observations in the downloaded files. |
| 404529 | San Francisquito Cr | 5 | [map](https://www.openstreetmap.org/?mlat=37.453280&mlon=-122.128420#map=16/37.453280/-122.128420) | Exclude | State postmile 402.237 is north of the endpoint at state PM 402.14. |
| 422116 | oppo S of Clarke Ave | 5 | [map](https://www.openstreetmap.org/?mlat=37.456467&mlon=-122.133857#map=16/37.456467/-122.133857) | Exclude | State postmile 402.607 is north of the endpoint at state PM 402.14. |
| 425545 | San Antonio Rd rm-n-coll | 5 | [map](https://www.openstreetmap.org/?mlat=37.428818&mlon=-122.101776#map=16/37.428818/-122.101776) | Hold out pending geometry review | PeMS classifies it as ML and SUMO's nearest US-101 edge has five lanes, matching PeMS; the `rm-n-coll` name makes full through-mainline coverage uncertain. Do not use as a full cross-section until the collector/mainline position is visually reconciled. |
| 425697 | Embarcadero Rd rm-n-coll | 4 | [map](https://www.openstreetmap.org/?mlat=37.450295&mlon=-122.124287#map=16/37.450295/-122.124287) | Exclude | Collector label and PM 52.29 place it beyond the Oregon Expressway endpoint. |
| 425892 | Rengstorff Ave rm-n-diag | 5 | [map](https://www.openstreetmap.org/?mlat=37.421844&mlon=-122.093417#map=16/37.421844/-122.093417) | Provisional keep | SUMO match is on the NB mainline; no qualifying 07:00–08:59 observations in the downloaded files. |

## Interpretation caution

PeMS labels with `rm` or `diag` can still be reported as mainline (`ML`) in
the metadata. Do not automatically exclude them, but inspect those locations
especially carefully.

## M1 data summary

The reproducible station-by-station output is
`outputs/pems_calibration/us101_corridor_m1_station_profiles.json`; the
aggregate summary is
`outputs/pems_calibration/us101_corridor_final_morning_peak.json`. Both read
the 25 local exports (2025-10-01, 2025-10-07 through 2025-10-16, and
2025-10-18 through 2025-10-31) and retain only 07:00–08:59 observations with
at least 90% lane coverage. Eight of the 13 accepted locations provide
qualifying readings. Six have 13 days each (2025-10-01, 2025-10-07 through
2025-10-16, and 2025-10-18 through 2025-10-19); stations 401507 and 401534
have 12 days each (2025-10-07 through 2025-10-16 and 2025-10-18 through
2025-10-19). Stations 401997, 402376, 402379, 404522, and 425892 have no
qualifying rows in these exports. These are unavailable observations, not
zero-traffic measurements. Station 425545 has qualifying data on 13 dates but
is not included in the accepted profile because its collector/mainline coverage
is unresolved.

Across the eight accepted stations with readings, the report contains 2,448
five-minute observations, with an average of 418.9 vehicles per five minutes
per station and an average speed of 50.7 mph. This is an average across
detector cross-sections, not a summed corridor flow.

The 13-day date set includes weekend dates; it is the set available after the
coverage filter, not a weekday-only sample. Use the separate H0 common-date
profile for baseline calibration rather than assuming this whole M1 summary is
the experiment's date set. The December 2024 Caltrans [US-101 exit table](https://dot.ca.gov/-/media/dot-media/programs/safety-programs/documents/exit/202412-calnexus-us-101-a11y.pdf)
places the Oregon Expressway endpoint at county postmile 52.17.

## Flow-balance result

The audited station order is 402370, 401996, 401998, 402372, 401534, 401948,
and 401507. Five adjacent comparisons are currently usable. The two Moffett-
to-Shoreline residuals are +238 and +1,622 vehicles/hour when compared on the
same 12 dates and 288 five-minute slots; they remain net changes, not ramp
counts. Stations 401998 and 402372 map to the same uninterrupted SUMO edge but
differ by -196 vehicles/hour; that is treated as detector disagreement rather
than ramp demand. The user's PeMS screenshots
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
