# M7 sensitivity and uncertainty plan

Written 2026-10-17 before the M7 specification and implementation. Starting
point: main 7f847ba, with M6 merged through PR #2 at ef8d20c. M0-M6 are
complete at their documented practical standards. User authorized M7 through
plan, specification, implementation, measured checks and publication.

1. Inspect accepted M3-M6 contracts, raw evidence availability and notebook.
2. Freeze a bounded one-factor-at-a-time matrix and explicit acceptance
   criteria before examining M7 traffic outcomes. Cover demand, passenger
   equipment penetration, communication range/delay/loss, controller settings,
   and expanded seed spread. Do not optimize policies against sweep results.
3. Reuse the experiment harness and independent raw-output metric auditor.
   Add only demand scaling, deterministic equipment/message selection and a
   sweep runner/report. Preserve exact legacy default behavior.
4. Verify formulas, deterministic boundaries, invalid settings, zero-equipment
   and no-message controls, failed/missing-seed suppression and real SUMO
   replay. Check unchanged-input base cases against M6.
5. Execute the frozen full-window matrix. Keep raw outputs, null/inactive
   policy cases and failures. Pair treatments only against matching-demand H0.
6. Independently recalculate raw metrics, health, fleets/schedules, controller
   decisions and paired statistics. Publish plots/tables and failure cases;
   synchronize README, CONTEXT, roadmap, project memory, Obsidian and GitHub.

Completion requires an auditable sensitivity evaluation, not a traffic benefit
or universal clean behavior under stress. M3 held-out fidelity and M5 low
engagement remain limits. M8 final research packaging is outside this task.

## Design decisions

- Use a bounded OFAT screen, not a full factorial or optimizer. It exposes
  conditional sensitivity but cannot identify interactions or total uncertainty.
- Equipment is a stable hash of vehicle ID; message loss is a separate stable
  hash of follower, leader and simulation step. Neither consumes SUMO RNG.
- Communication degradation affects acceleration feedforward only; current
  range/gap/relative-speed sensing and the native safety supervisor remain.
- Frozen M6 baseline uses five seeds (41-45); sensitivity cases use 41-43.
  Seed SD/range and sign agreement are descriptive, not confidence intervals.
