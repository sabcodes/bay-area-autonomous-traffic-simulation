# M1-M8 adversarial council review

Status: review in progress. Requested 2026-10-18 after M8 research packaging.
Reviewed baseline: `e64242422a8abb34c6ba46d4d11b12dc3a43e8a9` (PR #4).

## Charter and review method

The user explicitly requested an adversarial council spanning M1-M2, M3-M7 and
the M8 report. Three independent reviewer passes examine foundations (M1-M2),
baseline/measurement (M3-M4), and controllers/sensitivity (M5-M7). The coordinating
chair separately challenges M8 packaging, reproduction and claim/evidence links.
These are same-model internal reviews, not independent external peer review.

Reviewers start from the same immutable revision, gather concrete counterexamples
and distinguish disclosed scientific limits from actual defects. A rebuttal pass
challenges the evidence, severity and suggested corrections. The chair adjudicates
findings, validates corrections and records unresolved limits. Reviewer passes
are read-only; the chair alone changes the publication. Accepted scientific
inputs/results stay frozen unless a demonstrated numerical defect requires a
separately recorded correction. No expensive full simulation is started merely
to reconfirm saved outcomes.

The review will retain each substantive finding, evidence/proof, decision,
correction and verification. It will record coverage and unexamined evidence;
a passing test suite or reviewer agreement alone cannot establish field validity.
The original M8 verification remains a historical checkpoint. A new post-council
record will identify newly run checks, changes and publication state.

## Work in progress

- Foundations: PeMS parsing, missingness/station/lane selection, accepted network
  and legal movements, provenance and raw-to-derived input reproducibility.
- Baseline/measurement: bounded calibration/freeze/held-out separation, error
  weighting, demand/cohort/metric definitions, health gates and replay instructions.
- Controllers/sensitivity: supervision/message semantics, activity denominators,
  VSL timing/restoration, matched populations, OFAT denominators and audit evidence.
- Chair/report: deterministic package checks, clone-only boundaries, reproduction
  safety, displayed claims and whether conclusions exceed the measured evidence.
