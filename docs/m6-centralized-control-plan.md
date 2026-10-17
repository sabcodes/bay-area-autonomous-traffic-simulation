# M6 centralized control plan

Written 2026-10-17 before the specification and implementation. Starting point:
accepted M5 commit 70409b8; PR #1 remains open. M6 branches from that state and
will use a stacked PR until M5 is merged.

1. Confirm M5 evidence, frozen M3 inputs, local runtime and Obsidian handoff.
2. Specify one explainable feedback variable speed limit (VSL), its geography,
   timing, diagnostics, fair comparison and measurable acceptance criteria.
   Freeze parameters before traffic outcomes; no benefit-based retuning.
3. Implement the central lane-limit controller through the existing harness,
   preserving the accepted H0 and supervised CACC implementations.
4. Check hand calculations, invalid configuration, timing/empty-data/cleanup,
   deterministic small SUMO replay and a corridor preflight. Preserve failures.
5. Run a fresh H0/CACC/CENTRAL matrix on 2025-10-08, seeds 41-43.
6. Independently recompute raw metrics and policy decisions; verify fleet,
   schedule, input hashes and exact H0/CACC replay against M5. Publish results
   with seed spread, limitations, synchronized context, Obsidian and GitHub.

Completion requires clean simulations and an auditable comparison, not a
positive performance result. M3 held-out fit remains limited; continuous CACC,
policy optimization and broader sensitivity belong to later milestones.
