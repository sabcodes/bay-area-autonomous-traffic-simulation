# M6 variable speed limit interpretation notes

Checked 2026-10-17 while the frozen matrix was running. These references inform
interpretation and later sensitivity work; they did not change M6 parameters.

FHWA describes speed harmonization as adjusting speeds when congestion thresholds
are reached and queues become imminent. This supports the broad choice of an
explainable threshold policy, not the numerical M6 settings or any benefit claim.
Source: https://ops.fhwa.dot.gov/bn/lbr.htm

FHWA-HRT-16-023 (March 2016) describes a density-based approach with sensing in the
harmonization zone and directly upstream/downstream of a bottleneck. This is a
richer sensing arrangement than M6's single downstream observation zone.
Source: https://www.fhwa.dot.gov/publications/research/operations/16023/002.cfm

Project inference: observation geography and threshold selection can determine
whether feedback activates, even when the larger domain is congested. The
nonactivating 3000 s probe is evidence about this particular observation/rule,
not evidence that VSL generally cannot help. Preserve that null result and
report full-window actuation. Do not borrow benefits from other corridors or
claim FHWA validated the 15/20/25 m/s thresholds, 30 s intervals, 1 m/s changes,
or this US-101 model. Calibrated sensing/threshold/zone comparisons belong to M7.

M6 compares one fixed illustrative policy against the frozen baseline. Queue
relocation toward insertion should be evaluated with scheduled total time and
insertion backlog, in addition to on-road queue counts. See the frozen contract
in docs/m6-centralized-control-spec.md and the M3 held-out fidelity caveat.
