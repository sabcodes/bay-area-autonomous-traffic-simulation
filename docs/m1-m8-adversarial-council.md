# M1-M8 adversarial council review

Requested and completed 2026-10-18. Reviewed baseline:
[`e642424`](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/commit/e64242422a8abb34c6ba46d4d11b12dc3a43e8a9),
M8 PR #4. The numerical synthesis survives the scoped review. **Three
reproduction defects were confirmed and corrected in the publication.** Exact
archived derived inputs remain necessary for full hash-bound replay; portable
raw-to-frozen-input reconstruction was not demonstrated.

## Council composition and method

| Seat | Initial challenge |
| --- | --- |
| Foundations reviewer | M1 PeMS parsing, coverage/stations, lane alignment; M2 network/topology, demand and provenance |
| Baseline/measurement reviewer | M3 fitting/freeze/validation, weighting and raw scores; M4 cohort/metric/health contracts |
| Controllers/sensitivity reviewer | M5 supervision/messages, M6 VSL, M7 populations/denominators, nulls, audits and claims |
| Coordinating chair | M8 saved-package integrity, replay instructions, claim/evidence consistency and adjudication |

Three reviewer agents made separate initial analyses at the fixed revision.
They then challenged each other's evidence and proposed corrections in a
rebuttal round. The chair independently reproduced the provenance and output
isolation counterexamples, made corrections, and ran a targeted correction
review with all three reviewers. All three passed that correction review.

This is an internal same-model council sharing project context. It is not an
external peer review, a fully blinded exercise or evidence that agreement alone
establishes correctness. Reviewers were read-only; the chair alone changed the
publication. No accepted scientific run was replaced, recalibrated or retuned.
The [machine council record](../reports/m8/council_review.json) retains findings,
checks, decisions and residual limits. The
[post-council verification](../reports/m8/council_verification.json) records the
new full regression and package checks; the original
[M8 verification](../reports/m8/verification.json) remains an unchanged historical
checkpoint.

## Adjudicated findings

References below identify the reviewed baseline, rather than shifting line
numbers in the corrected publication. P2 means a correction was needed for
reliable reproduction guidance. These findings did not demonstrate incorrect
accepted outcome values.

### F1, P2: raw regeneration cannot promise frozen input bytes in a relocated clone

Baseline `docs/reproduction.md:63-83` instructed raw reconstruction followed by
the frozen input-hash checker. `scripts/prepare_m3_upstream_proxy.py:15-36` passes
absolute filenames into the boundary provenance, and `pems.py:341` serializes
them verbatim. The frozen config hashes the complete resulting JSON.

The accepted upstream profile contains seven absolute source paths. Changing
only these paths to `/tmp/fresh-clone/data/pems/...` preserves all profile values
but changes the SHA-256:

| Serialization | SHA-256 |
| --- | --- |
| Accepted | `ee9f7b11d208799167ca1d8bbdb43d6e7ecd4a7eeb541f57080223209c25bab7` |
| Relocated provenance only | `e7752109803518a16eb956311540fa2bb9d360ebfc5dac056c155e8d21596215` |

A second trigger is the source inventory: both accepted derived profiles record
**25 scanned filenames**, including exports without qualifying observations.
The seven M3 dates or 12/13 qualifying M1 dates cannot recreate those serialized
records. Original per-raw-file content hashes were not archived, so filenames
alone cannot prove byte-identical raw re-downloads.

**Correction:** [reproduction](reproduction.md) now separates exact restoration
of the two archived derived-profile snapshots from legacy raw reconstruction,
lists their hashes and the complete scanned date set, and states the portability
boundary. The final report and context qualify completion accordingly. Frozen
inputs, source and hashes are unchanged. The misleading reproduction promise is
resolved; the legacy portability limitation remains explicitly open for a future
versioned preparation contract.

### F2, P2: M3 replay can overwrite accepted phase reports

Baseline `docs/reproduction.md:140-143` instructed changing `output_directory`
only. `configs/us101_m3_experiment.json:34-35` separately sets `report_directory`
to `reports/m3`; `run_m3_baseline.py:214-216` writes phase reports there.
Validation also reads calibration from that configured directory at lines
206-209. Following the guide could replace accepted evidence and break freeze
and package bindings.

**Correction:** the guide now provides a concrete config-preparation snippet
with fresh runtime **and report** directories. The current README also routes
M3 replay to that recipe instead of repeating canonical-write commands. Both phases use the same separate
config. The chair executed the snippet in a scratch directory, confirmed no
canonical report/runtime directory was touched, and confirmed that a repeated
namespace is refused before simulation. The legacy runner itself still permits
replacement if a caller reuses paths; this is disclosed. The corrective guide
is checked without starting a full calibration campaign.

### F3, P2: engine-enforcement wording exceeds the implemented gate

Baseline `docs/reproduction.md:40-43` stated that the runtime harness rejects an
incompatible engine. `experiment_harness.py:387-389` compares controlled engine
diagnostics against the **locally installed** SUMO executable. That is an
agreement check, not an independent expected-version 1.27.1 gate. H0 has no
controller-version comparison.

**Correction:** the guide states exactly what the gate checks and retains the
explicit 1.27.1 installation prerequisite. Every accepted M3-M7 provenance record
inspected reports 1.27.1; all 52 controlled M5-M7 records agree with their local
executable. No accepted engine mismatch was established. The controller reviewer
initially rated this wording issue P3; the chair adopted P2 because the replay
guide claimed a stronger safeguard than exists. This severity difference does
not affect the agreed correction or accepted numerical results.

## Additional reporting clarifications

- **C1, exposure denominator:** introductory wording now identifies overlay
  commands over all-run passenger timesteps. About 2% is neither window-specific
  engagement nor the acceleration-feedforward fraction. The detailed M5
  all-run fractions and policy definition were already correct.
- **C2, evaluation history:** the historical nine-date diagnostic included
  October 15/16 before the formal M3 split. The report now explains that
  "held out" describes the frozen fitting/evaluation phases, not certified
  fully unseen-data blinding. No evidence of post-freeze retuning was found;
  the narrower no-retuning claim remains.

## Independent numerical and provenance checks

| Scope | Evidence checked in the council | Result |
| --- | --- | --- |
| M1 observed data | 2,448 saved station intervals over eight observed stations; 216 raw October 8 station intervals, flow and speed, including inlet | Exact agreement with saved profiles; missingness retained |
| M1 metadata | 18 accepted/input station records across the two metadata snapshots | Location, direction, route, type, lanes and names agree |
| M2 network | Compressed/decompressed network and OSM hashes; fresh read-only topology audit | 37/36 NB/SB route edges, 19/21 branch transitions, zero unresolved boundary/depth/cycle outcomes |
| Demand ledger | Five-day station arithmetic | Net-entry residuals 697.2 and 2,060.4 veh/h; downstream 1,484.8 veh/h after stated missing-lane assumption; rounding supported, physical OD not identified |
| M3 detectors | 6,552 native XML station/interval aggregations | Match exported detector JSON |
| M3 scoring | 3,528 observed/model interval pairs, 21 final runs; all three freeze file hashes | Calibration 8.321645605% / 8.151569782 mph; validation 19.374023959% / 14.904101820 mph, individual days also reproduced |
| M4/cohorts and M5-M7 replay | Raw seed-41 H0/CACC/CENTRAL trips and fleets | All 22,951 IDs/types/speed factors/intended schedules match; each scheduled cohort has 20,449 trips; throughput and total time reproduce |
| M7 groups/pairs | 480 metric records: means, sample SDs, ranges, signs and exact matching H0 denominators | All match |
| M7 own-policy contrasts | 28 factor records | All match |
| M7 null controls | Three zero-equipment CACC and three low-demand CENTRAL | All exact same-demand H0 outcomes |
| M6/M7 VSL decisions | All 14 M7 CENTRAL interval ledgers | Decision, command, exposure and restoration arithmetic reproduces |
| Controller logic | Equipment-only acceleration messages, same-leader history, supervision and VSL authority | Consistent with active specs; no additional defect established |
| Source/audits | Source/report/config hashes, historical audit fingerprint change | Bindings match; only later factor-validation helper changed, as disclosed |

These checks are scoped corroboration. The chair's final full suite includes
190 passing tests, including the prior tests and a new manifest regression for
council findings. Some reviewer sandbox tests requiring writable temporary/cache
files could not run; that environment limitation is not counted as a test pass
or a scientific failure. Exact new commands/results appear in the post-council
verification record.

## Scientific limitations and unexamined evidence

The M3 October 15 fidelity failure, unknown gross movements/OD composition,
402377 lane uncertainty, 401948 mismatch, generic truck share, network/observation
date mismatch, conditional demand inputs, simplified managed lanes and historical
ramp-meter operation remain material limits. M5 low engagement, ideal sensing
and actuation, rounded exported acceleration and M7's one-day OFAT design with
three/five seeds limit inference. Seed SD is not total uncertainty or a field
confidence interval. These are retained scientific limitations, not newly
classified implementation errors.

The council did not rerun a full campaign or reconstruct all trajectories across
all accepted runs. It did not independently certify field striping, loop wiring,
study-day eligibility or meter settings. Full packet/live sensor histories are
not exported, and raw-file byte provenance is incomplete. The internal review
does not remove these limits. No consistent overall traffic benefit, field
safety, deployment readiness, energy saving, optimality or general V2V effect
is established.

Saved-evidence research packaging is complete after the corrections. Full replay
is conditional on archived exact inputs and the recorded environment. Original
accepted outcomes remain unchanged. Publication continues in
[PR #4](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/4)
for user review; no merge is performed by this council.
