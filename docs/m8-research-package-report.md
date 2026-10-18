# M8 research package acceptance record

Original acceptance completed 2026-10-18 at the project's practical experiment standard.
The original checks below are historical; post-council corrections and current
verification are recorded in the addendum at the end of this document.
[Final report](final-research-report.md), [tables](../reports/m8/results.md),
[reproduction](reproduction.md), [manifest](../reports/m8/manifest.json) and
[verification record](../reports/m8/verification.json) form the final package.

| Acceptance | Evidence | Result |
| --- | --- | --- |
| AC1 plan before spec before implementation | 071de85 -> 974ecb6 -> bedffd1 | Pass |
| AC2 faithful synthesis | M3-M7 comparisons, rejected/null outcomes, metric units/cohorts, source checks and explicit scientific limits | Pass |
| AC3 correct complete populations | All 52 M7 headline metric records recomputed against accepted aggregate/pair records, M3 six-station scores recomputed across 21 runs; final displayed values checked | Pass |
| AC4 reproducibility/provenance | Deterministic repeated builds, read-only check, 9 local input hashes, tamper/missing-file tests and complete package manifest | Pass |
| AC5 regression/presentation | Full 189-test suite, lint, whitespace, package links, three reused figures inspected | Pass |
| AC6 context/publication | README, CONTEXT, roadmap, memory and linked Obsidian notes; branch pushed to a reviewable GitHub PR | Pass; publication URL/SHA in final handoff |

The suite adds 24 M8 tests to the prior 165. These include complete populations,
missing/duplicate/rejected runs, date mismatches, null/boolean/string/nonfinite
metrics, altered aggregates, wrong audit hashes, changed simulator source,
M3 score/station/freeze failures, missing/mismatched prerequisites, manifest
content tampering, missing artifacts and read-only check behavior. Generated
outputs are written only after numerical/input validation. Package check uses
Git-tracked inputs; stage new package files before intentional regeneration.

Manual review of the reused M7 figure confirmed all 13 labels, four panels,
individual seeds, sample SD and null controls. The M3 held-out figure visibly
preserves the October 15 upstream mismatch; M6 preserves its earlier independent
three-policy view. No new figure was needed. Local source URLs were checked
against primary Caltrans, SUMO and FHWA pages on 2026-10-18.

M8 is a saved-evidence packaging check, not a fresh raw-trajectory audit. M7's
1620 raw metric checks, 480 group/paired checks, 28 factor checks and 54 native
metadata checks remain recorded historical evidence. No accepted M3-M7 report,
frozen config or simulator source changed. No full-window simulation was rerun.
The content manifest does not sign or authenticate evidence; Git history and
review supply that trust anchor. Verification.json is a later observation record
excluded from the content manifest to avoid a self-hash cycle.

Completion preserves the M3 held-out fidelity failure (combined speed MAE
14.90 mph), about 2% active supervised CACC exposure, one-day OFAT scope,
ideal sensing/actuation and local raw-data boundary. Results establish no
consistent overall traffic benefit or field safety/deployment claim. M8 is
complete for review; merging the publication PR is a separate user decision.


## Post-council acceptance addendum - 2026-10-18

The user extended review to M1-M7 and this report. The
[adversarial council](m1-m8-adversarial-council.md) found three reproducibility
wording/instruction defects and established no accepted numerical error in its
bounded checks. All three reviewers passed targeted correction review. Replay
guidance now requires exact archived derived profiles, fresh M3 runtime AND
report directories, and precise local engine-agreement semantics. All-run overlay
exposure and historical validation-date exposure are clarified.

Saved-evidence research packaging remains accepted; portable raw-to-frozen input
reconstruction is not demonstrated. The underlying legacy input serialization
still embeds absolute provenance paths. This limitation is disclosed rather than
changing accepted input identities or claiming raw regeneration is portable.

Current full regression: 190 tests, with one new regression protecting council
machine findings through the manifest and explicitly excluding later verification
observation records. Lint, whitespace, package/input/link, repeated-build and clean
checkout checks pass. The exact commands, counts and artifact hashes are in
[post-council verification](../reports/m8/council_verification.json). Accepted
M3-M7 reports, configs, network and simulator source remain unchanged; headline
JSON/table bytes are identical. The original `verification.json` and its original
manifest fingerprint remain historical evidence and are not rewritten.
