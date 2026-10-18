# M7 sensitivity and uncertainty specification

Frozen 2026-10-17 after plan 655758b and before M7 implementation/results.
This is a conditional OFAT sensitivity screen, not policy optimization or a
probabilistic uncertainty model. Network, class mix, native behavior, physical
limits, observed inputs, 0.5 s step, [900,8100) measurement and 7200 s clearance
retain M3-M6 settings. One calibration date: 2025-10-08. No held-out retuning.

## Frozen matrix

| Case | Change from M6 | Policies | Seeds | Runs |
| --- | --- | --- | --- | ---: |
| base | None | H0, CACC, CENTRAL | 41-45 | 15 |
| demand_080 | All generated flow rates x0.8 | H0, CACC, CENTRAL | 41-43 | 9 |
| demand_120 | All generated flow rates x1.2 | H0, CACC, CENTRAL | 41-43 | 9 |
| penetration_000 | 0% equipped passengers | CACC | 41-43 | 3 |
| penetration_050 | 50% equipped passengers | CACC | 41-43 | 3 |
| range_050 | Leader query/message range 50 m | CACC | 41-43 | 3 |
| delay_1000 | Extra acceleration-message age 1 s | CACC | 41-43 | 3 |
| loss_020 | Independent deterministic 20% message loss | CACC | 41-43 | 3 |
| headway_2000 | Requested CACC headway 2 s | CACC | 41-43 | 3 |
| vsl_220 | Congested VSL target 22 m/s | CENTRAL | 41-43 | 3 |

Total 54 fresh full-window runs. All treatments pair by exact seed with H0 at
the same demand (base H0 for non-demand factors). Base CACC/CENTRAL are the
settings references for interpreting factor changes. No mixed-demand pairs.
Store every planned run and retain failed/inactive cases; do not retry them
with altered settings. Additional runs require a labeled spec amendment.

## Demand contract

`demand_scale` is an optional finite positive numeric baseline setting, default
1. Scale each finalized through/exit/entrance five-minute rate AFTER measured
exits are subtracted, BEFORE route writing and input accounting. Warmup scales
by the same factor. Do not edit observed profiles or hashes. At 1.0 preserve
byte-identical route files. Within each demand case all policies use the same
route bytes and match exported vehicle ID/type/speed-factor/intended schedule.
Actual inserted cohort sizes may differ; retain scheduled-cohort total time and
insertion backlog alongside actual-departure metrics.

## Equipment and communication contract

Optional supervised-CACC keys: `penetration` (default 1), `message_delay_seconds`
(default 0), `message_loss_probability` (default 0). Require finite numbers,
penetration/loss in [0,1], delay >=0 and aligned to 0.5 s. Bound supported delay
to 5 s to keep snapshot memory bounded. Reject unknown keys and booleans.
Legacy DEFAULT_CONTROLLER and default numerical behavior remain unchanged.

Use SHA-256 of UTF-8 `equipment|<vehicle-id>`, first eight bytes big-endian /
2**64, equipped iff value < penetration. Selection is stable across seeds,
runs and process order; realized fraction need not equal target exactly.
Only equipped passenger followers receive commands or broadcast acceleration;
trucks and unequipped passengers remain native. Keep subscriptions for sensing
all leaders; do not change SUMO vehicle types, native following, lane-change
modes, safety modes or simulator RNG. Report eligible/equipped vehicle counts,
equipped-ID SHA-256 and passenger/equipped timestep denominators.

A current sensed leader in range uses current gap and speed. Acceleration
feedforward additionally requires an equipped passenger leader, a message from
that SAME leader at step k-delay/0.5, and successful delivery. History contains
only accelerations and retains delay+1 snapshots. Zero extra delay preserves
M5 previous-step acceleration semantics. New leaders without old messages,
losses or unequipped leaders use ACC with zero feedforward. No stale-message
hold, prediction or delayed relative-speed sensing. Hash UTF-8
`message|<follower>|<leader>|<step>` as above; delivered iff value >= loss.
No network RNG. Record message opportunities/deliveries/losses/unavailable
history and cooperative/ACC/cruise commands. Communication range also bounds
sensed leader following, as in M5; label that combined effect explicitly.

## Execution validity and activity

M4-M6 strict acceptance remains the default. M7 explicitly permits inactive
controllers: zero-equipped CACC and nonactivating VSL are valid null controls.
A valid M7 run still requires every original health/clearance gate, complete
metrics, completed matching-version engine, no CACC native fallbacks, and VSL
restoration plus positive update count. Activity is a separate status, never
inferred from numerical outcome. Warnings/collisions/teleports/backlog or
exceptions reject the run. Preserve errors and diagnostics. Zero-equipment
CACC must exactly replay H0 on seeds 41-43; legacy base H0/CACC/CENTRAL must
exactly replay all 30 M6 metrics on seeds 41-43.

## Reporting, uncertainty and verification

Use all 30 existing metrics. Publish per-run outcomes, policy activity/exposure,
per-case seed count/mean/sample SD/min/max and paired per-seed differences,
mean/sample SD/range/positive-negative-zero counts and percent of H0 mean.
A group or pair aggregate is null unless EVERY planned seed is valid and the
metric is finite; show available seed count and failure reasons. No surviving-
seed-only averages. Do not pool dates, demand cases or factors. Plot paired
throughput, scheduled total time, RMS acceleration and peak insertion backlog,
with spread and individual seeds, plus a failure/activity table.

| AC | Required evidence |
| --- | --- |
| AC1 | Plan then spec commits precede implementation; frozen config exactly covers 54 runs. |
| AC2 | Hand-checked scaling and selection/message boundary/delay tests; bad values rejected before simulation; no RNG consumption; deterministic real-SUMO replay and zero-equipment native behavior. |
| AC3 | Full existing regression/lint checks; strict M6 inactivity gates preserved; failed/missing/nonfinite aggregate suppression tested. |
| AC4 | All planned outcomes retained, matching-demand route/fleet/schedule checks, exact base M6 replay and zero-equipment H0 replay. Stress failures are evidence, not milestone failure. |
| AC5 | Independent raw trip/summary/trajectory recalculation for every numerically completed run, independent VSL ledger/selection diagnostics checks, hashes and every aggregate/pair checked. Auditor imports no production metrics/controller functions. |
| AC6 | Versioned machine report, audit, plots, failure table, closeout/limits and synchronized context, Obsidian and GitHub PR. |

M3's held-out failure, unknown gross ramp flows, ideal VSL sensing/actuation,
M5's low engagement and rejected continuous variants remain. Seed spread is
stochastic simulation variation, not a confidence interval or total uncertainty.
No capacity, wave stability, energy, real-world safety or deployment claims.
