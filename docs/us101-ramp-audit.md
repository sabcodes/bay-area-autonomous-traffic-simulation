# US-101 PeMS ramp detector audit

## Purpose

The corrected corridor contains six PeMS on-ramp (`OR`) candidates and seven
off-ramp (`FR`) candidates. These sensors provide spatial demand evidence, but
their coordinates are close enough to US-101 that automatic nearest-edge
matching often selects the freeway instead of the ramp. Every mapping must be
visually checked before the observed flow is injected into SUMO.

## October 2025 morning data availability

The first 07:00–08:59 scan found qualifying observations for four on-ramps and
one off-ramp. PeMS did not provide qualifying rows for the other eight
candidates in the downloaded days. Missing values must be estimated later from
flow conservation and MTC demand structure; they must not be treated as zero.

| ID | Type | PeMS name | Mean veh/hour | Status |
| --- | --- | --- | ---: | --- |
| 428588 | FR | Mathilda Ave | 636 | Accepted: edge `9080606` |
| 428589 | OR | Mathilda Ave. rm-n-loop | 328 | Accepted: edge `509747339`, merging at `509747346` |
| 423301 | OR | NB 101 to WB 237 I/C on | — | No qualifying rows; edge needs audit |
| 402917 | FR | Moffett Blvd off diag | — | No qualifying rows; edge needs audit |
| 402919 | OR | Moffett Blvd on loop | 136 | Accepted: edge `847214392#0`, merging at `1047818462` |
| 425894 | FR | Rengstorff Ave off diag | — | No qualifying rows; edge needs audit |
| 425895 | FR | Rengstorff Ave off loop | — | No qualifying rows; edge needs audit |
| 425893 | OR | Rengstorff Ave on | — | No qualifying rows; edge needs audit |
| 425699 | FR | San Antonio Rd off | — | No qualifying rows; edge needs audit |
| 425546 | OR | San Antonio Rd on | 487 | Accepted: edge `9739842#1`, merging at `700010299` |
| 425694 | FR | Embarcadero Rd off | — | No qualifying rows; edge needs audit |
| 425696 | FR | Embarcadero Rd off | — | No qualifying rows; edge needs audit |
| 425897 | OR | Embarcadero Rd on | 787 | Excluded: merge is beyond the analysis endpoint |

Ramp files do not contain usable speeds for these observations. Their role is
to constrain demand and routing; the mainline virtual detectors remain the
speed-validation targets.

## Mapping acceptance rule

For every ramp with a chosen SUMO edge, confirm all of the following:

1. The edge represents the named on-ramp or off-ramp, not an adjacent freeway
   lane or surface street.
2. Its travel direction and connectivity are correct.
3. An on-ramp route can merge into the audited northbound mainline without a
   U-turn, teleport, or surface-street detour.
4. An off-ramp route leaves the mainline and does not rejoin it inside the
   study segment.
5. Its lane count and merge/diverge geometry look plausible.

Only accepted mappings should move from observed targets into generated SUMO
flows and origin/destination routes.

## First accepted mappings

The five reporting ramps were reviewed interactively at their PeMS coordinates
on the OpenStreetMap web map. The visible ramp geometry was then checked against
OSM road tags and connected paths in the imported SUMO network. Four mappings
pass the acceptance rule and are active in `configs/us101_human_baseline.json`.
The Embarcadero on-ramp is a valid northbound ramp, but it merges after edge
`361615812`, the current analysis endpoint, so injecting it would not affect
any detector in this experiment.

The Mathilda off-ramp profile is split from upstream station 402370 demand:
those vehicles start with the mainline traffic and leave on edge `9080606`.
The remaining 402370 demand continues through the corridor. The three accepted
on-ramp profiles start on their audited ramp edges and follow connected paths
onto the northbound mainline. Missing ramp profiles remain unknown and are not
silently converted to zero flow.
