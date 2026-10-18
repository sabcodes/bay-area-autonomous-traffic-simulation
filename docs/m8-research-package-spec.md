# M8 research package specification

Frozen before implementation, 2026-10-18. Implements [plan](m8-research-package-plan.md)
(commit 071de85). Runtime source/configs and accepted M3-M7 evidence stay frozen.

## Artifacts and behavior

- `docs/final-research-report.md`: self-contained question, corridor/data selection,
  calibration/held-out design, policy definitions, timing/cohorts/metric units,
  results with sample spread, null/rejected outcomes, limitations, primary sources,
  plain-language conclusion and links to detailed artifacts.
- `docs/reproduction.md`: exact clone-only build/check/test commands and separate
  local-input/full-run commands, pinned engine, acquisition/profile guidance,
  fresh output IDs, raw storage boundary and resource precautions.
- `scripts/build_m8_package.py`: standard-library only, runnable with Python >=3.11
  from any working directory, no production metric/controller imports.
- `reports/m8/headline_results.json` and `results.md`: deterministic computed
  M3 calibration/validation scores and all 13 M7 policy/case comparisons, four
  headline metrics each. Include exact per-seed pairs, H0 denominator, n, mean,
  sample SD, range and sign counts. Never pool dates/demand or sensitivity seeds
  41-43 with the five-seed base denominator.
- `reports/m8/manifest.json`: sorted SHA-256 of versioned package inputs (M3-M7
  reports, docs, research, configs, simulator source, scripts/tests, network,
  project metadata), and generated table/data. No host paths or timestamps.
  Exclude itself and the later closeout verification record to avoid cycles.
- `reports/m8/verification.json` and `docs/m8-research-package-report.md`: actual
  commands, counts, results, acceptance mapping and limitations of verification.

## Numerical and failure contracts

1. Derive the expected M7 run population from frozen campaign cases/seeds/policies.
   Require exactly 54 unique accepted outcomes, exact campaign/config agreement,
   one date 2025-10-08, and no missing/duplicate/extra runs. Require the accepted
   independent M7 audit to hash-bind that report; check its saved simulator hashes.
2. For each non-H0 policy/case use matching-demand H0 and identical seed. Each of
   the four headline values and pair differences must be finite real numbers
   (booleans rejected). Compute policy minus H0, sample SD (n-1), min/max,
   positive/negative/zero counts, and 100 * mean(diff) / mean(matched H0).
   Compare each computed statistic and individual pair against the accepted M7
   aggregate records at rel_tol=1e-10, abs_tol=1e-10. Any mismatch aborts publication.
3. Recompute M3 scores from each run's saved station error means and require the
   published summary to match. Preserve five calibration days/15 runs and both
   held-out days/six runs, seed 41-43, clean clearance and frozen treatment hash.
   Report October 15 and 16 separately plus their combined scores.
4. Fail with nonzero exit on missing/rejected/nonfinite inputs, schema/population
   errors, wrong audit hashes, altered simulator source, stale generated outputs
   or missing/changed manifest entries. Validate all inputs before any output.
5. Default build regenerates table/data/manifest only. `--check` writes nothing,
   recomputes expected bytes and compares every generated artifact and manifest.
   Document that regenerating a manifest is not an authenticity signature: Git
   history/review supplies the trust anchor. No raw-audit claim for this checker.
6. `--check-local-inputs` checks every expected input path/hash in the frozen M3
   config, reporting missing/mismatch and nonzero exit without starting SUMO.
   This separate prerequisite check does not claim local raw output availability.

## Acceptance

| ID | Requirement | Evidence |
| --- | --- | --- |
| AC1 | Plan -> spec -> implementation in separate commits | Git ancestry |
| AC2 | Faithful complete methods/results/caveats/source synthesis | Final report, cross-check against M3-M7 evidence, source URLs checked |
| AC3 | Numerical correctness and complete seed populations | 52 recomputed M7 records against audited aggregates; M3 scores; targeted malformed-input tests |
| AC4 | Reproducibility and provenance | Clone-only check, local prerequisites check, two byte-identical builds, manifest tamper/missing-file detection, no runtime changes |
| AC5 | Regression and presentation | Full pytest, ruff, whitespace/local-link checks, reused figure inspection |
| AC6 | Context and publication | README/roadmap/CONTEXT/project memory, linked Obsidian plan/spec/decision/results/handoff, pushed reviewable PR |

M8 completion means research packaging is complete at the practical experiment
standard. It cannot remove the M3 held-out fidelity failure, about 2% supervised
CACC engagement, M5 rejected variants, M7 OFAT/interactions limitations, ideal
sensing/actuation, missing field evidence, or raw data distribution boundary.
No fresh full-window simulation or controller change is required.
