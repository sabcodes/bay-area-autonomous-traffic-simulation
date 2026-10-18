# M8 research package plan

Authorized 2026-10-18. M7 PR #3 is merged at ad33a7f. This plan precedes the
specification and implementation; M8 packages the completed practical experiments.

## Outcome

Deliver a reproducible final research report for the audited US-101 northbound
corridor, SR-237 to Oregon Expressway/Page Mill Road. Explain what was tested,
what the evidence says, what failed, and what cannot be concluded.

## Sequence

1. Confirm merged M7, inventory saved evidence and local prerequisites, and record
   the M8 scope in project memory and Obsidian.
2. Commit this plan. Then define and commit a specification with artifact paths,
   numerical contracts, failure behavior, reproduction tiers and acceptance checks.
3. Implement a small standard-library report builder/checker. Recompute headline
   pairs directly from saved per-run values, bind the published evidence with
   SHA-256, and produce a deterministic Markdown table and machine data.
4. Write the final methods/results/limitations/source report and exact commands.
   Preserve held-out M3 failure, rejected M5 variants, low CACC exposure, null
   controls, mixed effects, and the limits of one-day OFAT and seed spread.
5. Verify independently: hand/reference comparisons against existing audited
   tables, package tampering/missing-data tests, full regression, lint, local
   links, repeat-build byte identity, and visual review of reused figures.
6. Update CONTEXT.md, roadmap, README, project memory and linked Obsidian notes
   at decisions and completion. Push the branch and create a reviewable GitHub
   PR; record the verified publication SHA in Obsidian. Leave merging to the user.

## Scope decisions

- Use accepted frozen outputs; no new controller, retuning, calibration or costly
  simulation campaign is needed for research packaging.
- Make clone-only package verification explicit. Full runtime reproduction also
  needs ignored local PeMS inputs/profiles and exact engine versions; do not
  represent a clone as containing those prerequisites or raw trajectories.
- Reuse accepted figures and detailed M3-M7 artifacts, linking rather than
  duplicating them. Generate only the final headline table and provenance.
- Keep simulator source, accepted configs, raw outputs and historical reports
  unchanged. M8 evidence checks are additional packaging checks, not fresh raw
  trajectory audits or evidence of field validity.

## Completion evidence

A final report, data-derived tables, content manifest, runnable check command,
acceptance record with actual verification results, and synchronized publication.
The specification will map each requirement to concrete checks before code exists.
