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
| 428588 | FR | Mathilda Ave | 636 | Data available; SUMO edge needs audit |
| 428589 | OR | Mathilda Ave. rm-n-loop | 328 | Data available; SUMO edge needs audit |
| 423301 | OR | NB 101 to WB 237 I/C on | — | No qualifying rows; edge needs audit |
| 402917 | FR | Moffett Blvd off diag | — | No qualifying rows; edge needs audit |
| 402919 | OR | Moffett Blvd on loop | 136 | Data available; SUMO edge needs audit |
| 425894 | FR | Rengstorff Ave off diag | — | No qualifying rows; edge needs audit |
| 425895 | FR | Rengstorff Ave off loop | — | No qualifying rows; edge needs audit |
| 425893 | OR | Rengstorff Ave on | — | No qualifying rows; edge needs audit |
| 425699 | FR | San Antonio Rd off | — | No qualifying rows; edge needs audit |
| 425546 | OR | San Antonio Rd on | 487 | Data available; SUMO edge needs audit |
| 425694 | FR | Embarcadero Rd off | — | No qualifying rows; edge needs audit |
| 425696 | FR | Embarcadero Rd off | — | No qualifying rows; edge needs audit |
| 425897 | OR | Embarcadero Rd on | 787 | Data available; SUMO edge needs audit |

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
