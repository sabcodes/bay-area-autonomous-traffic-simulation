# M3 demand ledger and limits

The selected H0 model uses measured five-minute entry/ramp profiles plus three
explicit estimates for groups of missing movements. Those group estimates
improve traffic accounting but do not identify individual ramp volumes. The
calibration dates are October 7–10 and 14, 2025. Validation keeps the estimates
fixed while using each validation day's measured entry and reporting ramps.

## Calibration accounting

| Item | Five-day mean (veh/h) | Treatment |
| --- | ---: | --- |
| Inlet proxy 400790 | 6,126 | Five-day mean; five-minute flow at 80% coverage, about 1 km before the analysis start |
| Study-start mainline 402370 | 5,674 | 90%-coverage comparison target; no longer the imposed inlet |
| Mathilda exit 428588 | 816 | Measured, subtracted from upstream through demand |
| Mathilda entrance 428589 | 354 | Measured entrance |
| Moffett entrance 402919 | 158 | Measured entrance |
| San Antonio entrance 425546 | 560 | Measured entrance |
| Embarcadero entrance 425897 | 952 | Outside the endpoint; excluded |
| Missing group before 401998 | 700 | Constant net-entry proxy on `509747350` |
| Missing group before 401507 | 2,000 | Constant net-entry proxy on GP connector `394387883` |
| Missing group after 401507 | 1,500 | Constant net-exit proxy on `4370043`, from diverge `394368089` |

The first group follows conservation between stations 401996 and 401998:
observed net change +235 veh/h minus measured Mathilda net change
(354 − 816 = −462) leaves approximately +697 veh/h. It combines all other
entries and exits in that interval. The second uses the complete comparison
401534→401507: +2,218 veh/h minus the measured Moffett entrance of 158 leaves
about +2,060 veh/h. The separate 401948→401507 difference is +2,047 veh/h,
but 401948's five measured channels versus four modeled lanes make it a
weaker allocation constraint. The rounded 700/2,000 constants are fitted on
calibration data. No validation-day downstream residual sets these constants.

Daily 401534→401507 differences range from 2,060 to 2,317 veh/h on the five
calibration days. This establishes a persistent net increase, not the gross
flow of either the GP or express connector. Assigning the second group to the
GP connector is a working allocation hypothesis. The express connector,
unmeasured exits, and other entrances can redistribute the same net change.

The third group is a calibration-only downstream hypothesis: mean Shoreline
flow of 8,041 veh/h plus measured San Antonio entry of 560 minus 5,616 across
the four reporting San Antonio–Oregon channels leaves 2,985 before the
unmeasured fifth lane. Assuming 1,500 veh/h in that lane gives a rounded
1,500 veh/h net-exit group. That assumption is not a lane count or individual
off-ramp measurement. Exit demand is routed out of inlet vehicles, not added
to total generated arrivals. Its location represents multiple unknown
movements after Shoreline.

The inlet is station 400790 (37.391922, -121.998077), outside the scored
station selection. Its seven selected weekday profiles have 24 numeric
five-minute intervals at at least 80% reported coverage. Mainline targets
retain the 90% rule. The three existing edges `395354963`, `28485321`, and
`28485321-AddedOffRampEdge` give a 1,007.33 m buffer before the accepted M2
analysis reach. The network hash is unchanged. This boundary was chosen using
calibration runs, because the old boundary suppressed upstream congestion;
omitted exits in the buffer and imputed inlet counts remain uncertainty.

## Every northbound branch in the accepted M2 ledger

| Branch review | Side edge | H0 treatment |
| --- | --- | --- |
| NB-00-I | `509747285` | Unknown; zero separate input; observed adjacent mainline net change is only +11 veh/h |
| NB-05-O | `9080606` | Measured Mathilda exit |
| NB-06-I | `509747339` | Measured Mathilda entrance |
| NB-09-O | `9545875` | Unknown; included in the first group's net accounting |
| NB-10-I | `509747350` | Representative input location for the first group |
| NB-13-O | `20113705` | Unknown; included in the first group's net accounting |
| NB-14-I | `281956182` | Unknown; zero separate input; 402372→401534 net +109 veh/h is unresolved |
| NB-17-O | `394385426` | Unknown; zero separate exit; contributes to the same unresolved net change |
| NB-19-I | `777748240` | Measured Moffett entrance via `847214392#0` |
| NB-22-O | `5005672` | Unknown; included in the second group's net accounting, zero separate exit |
| NB-23-I | `394387883` | Representative input location for the second group |
| NB-24-I | `11479095` | Unknown express demand; zero separate input; alternative group allocation remains a limitation |
| NB-26-O | `30990690` | Unknown exit; zero separate input; beyond the last full-cross-section reporting station |
| NB-28-I | `685973436` | Unknown entrance; zero separate input in H0 |
| NB-30-O | `9245798` | Unknown exit; zero separate input in H0 |
| NB-31-I | `8927566` | Unknown entrance; zero separate input in H0 |
| NB-32-O | `4370043` | Representative location for the 1,500 veh/h downstream net-exit hypothesis |
| NB-33-I | `9739842#1` | Measured San Antonio entrance |
| NB-35-O | `13100980` | Unknown exit; zero separate input in H0 |

An explicit zero in this working scenario is an omission assumption, not a
zero observation. Individual gross OD flows are not identifiable from the
current detector totals. The three groups' 50% and 150% flow cases form a
simulation sensitivity envelope (350/1,000/750 and 1,050/3,000/2,250 veh/h,
entry/entry/exit respectively). They are
not statistical confidence bounds. Station 402377 near the downstream end
has four measured channels on five physical lanes. Its two possible four-lane
selections are evaluated separately and are excluded from candidate scoring.
Whole-corridor travel time and individual ramp/control benefits remain
conditional on these omissions, especially beyond station 401507.

## Additional official inputs

Public files are saved in `data/caltrans/` with URLs and SHA-256 values in
`data/caltrans/provenance.json`. Caltrans's [Traffic Census Program](https://dot.ca.gov/programs/traffic-operations/census)
publishes annual daily truck and ramp volumes, which do not give October 2025
directional AM demand.

The `Truck AADTs 2024` sheet, rows 2147–2150, reports truck shares of 3.86%
and 3.81% at SR-237 and 4.58% and 4.50% at SR-85 (back/ahead legs, both
directions). The working fleet is 96% passengers and a 4% generic 12 m truck
proxy. Truck acceleration is 1.2 m/s², deceleration 4.0 m/s², and modeled
maximum speed 24.59 m/s. These physical proxy settings are assumptions, not
measured class-specific calibration. The 2% and 6% fleet cases bracket the
annual proxy; their shares are also assumptions.

The `D4-RAMP-ADT-2024` sheet has 2024 daily volumes of 2,700 at the Moffett
NB entrance (row 641) and 7,800 at the Rengstorff NB entrance (row 650).
The SR-85 NB connector row 644 has a 2019 daily value of 9,900 and blank
2020–2024 cells. That older value does not verify the 2,000 veh/h allocation.
The Rengstorff count also shows why zero separate downstream demand must be
treated as an omission. Converting these daily values to peak-hour flows
would require a temporal and directional assumption; this model does not
present such a conversion as measured evidence.

Caltrans's [March 2025 ramp-meter announcement](https://dot.ca.gov/caltrans-near-me/district-4/d4-news/2025-03-26-101-metering-lights)
scheduled adaptive metering upgrades beginning April 8 in the study area and
estimated completion by October 2025. Exact study-day meter settings are not
available here. H0 represents delivered ramp flow, without reconstructing
meter signals or upstream ramp queues. A future ramp-metering intervention
must define that existing-control baseline before claiming operational benefit.

## Initial diagnostic result

On the five-day calibration average, seed 42 with the two missing-entry
groups completed 21,179 trips. Shoreline flow MAPE improved from 33.0% to
3.5%, and speed MAE from 13.2 to 4.9 mph. Other reporting-station flow errors
also improved, while upstream speeds remained roughly 17–22 mph too high.
The 06:00–07:00 observed averages on those same weekdays are near 59–60 mph
at stations 402370, 401998, and 401507, so the major observed slowdown develops
during the analysis period rather than starting from a congested 06:00 state.
This motivates the bounded headway calibration and explicit upstream
bottleneck/boundary limitation in the final report.
