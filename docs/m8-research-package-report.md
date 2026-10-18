# M8 research package acceptance record

Completed 2026-10-18 at the project's documented practical experiment standard.
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
