# M5 cooperative CACC plan

Written 2026-10-16 before the M5 specification and implementation.

## Objective and boundaries

Compare the frozen human H0 with one deterministic cooperative longitudinal
controller on the accepted US-101 corridor. Retain M3's failed held-out fit;
this is a controlled simulation comparison, not field validation. M6 centralized
control and M7 sensitivity sweeps are outside this milestone.

## Sequence

1. Verify the M4 closeout, frozen inputs, baseline command, and clean Git state.
2. Research installed SUMO/TraCI contracts, then write an executable M5 spec:
   equations, timing, leader-query semantics, cooperative eligibility, fallback,
   physical limits, safety envelope, provenance, fair-comparison rules, and
   measurable acceptance criteria. Save the spec before changing source code.
3. Implement one small policy module and integrate it with the existing runner
   and M4 harness. Keep route generation and H0 behavior unchanged. Use bounded
   leader queries/subscriptions; do not scan all vehicle pairs.
4. Check hand-calculated controller cases and actual SUMO edge cases. Verify H0
   replay, deterministic replay, absence of simulation warnings, and matching
   treatment inputs. Record failures and investigate rather than hide them.
5. Execute H0 and CACC on October 8, 2025, seeds 41–43, with matching measurement
   settings. Report per-seed metrics and paired differences, including insertion
   delays/backlogs so changes in actual departure populations stay visible.
6. Run regression tests and lint, review the diff against the spec, and map every
   acceptance criterion to saved evidence. Preserve compact versioned reports;
   keep large trajectories in ignored outputs.
7. Synchronize README, CONTEXT.md, roadmap, project memory, and the Obsidian
   project/decisions/source index/daily log. Publish the implementation and
   acceptance evidence to GitHub and verify the remote revision.

## Decision record

M4 is complete at published commit e4ae0e98a8af0da1e764c7570741ebd324a0813a.
The user authorized M5 plan → specification → implementation and data-driven
verification on 2026-10-16. Superpowers and Matt Pocock skills are opt-in and
were not invoked. Obsidian vault: Auto-Car Traffic Research, project area
US-101 Traffic Simulation. The repository remains authoritative.

## Completion gate

M5 closes only with a reproducible matched comparison, passing relevant checks,
clean and cleared accepted SUMO runs, explicit controller assumptions and
limitations, synchronized context, and verified GitHub publication. If a
criterion fails, retain and explain its evidence without calling it passed.


## Closeout, 2026-10-16

Complete for the supervised comparison. The [revision-4 spec](m5-supervised-cacc-spec.md)
supersedes the rejected earlier policies. All six full runs and 102 tests pass;
independent audits preserve failures, exact H0 replay, matched exported fleets
and paired metrics. Low engagement (about 2%) and mixed outcomes limit the
conclusion. See the [closeout](m5-cooperative-cacc-report.md) and
[results](../reports/m5/README.md). Continuous CACC remains unresolved; M6 is next.
