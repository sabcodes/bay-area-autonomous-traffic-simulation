# M7 sensitivity and uncertainty closeout

M7 is complete at the documented conditional sensitivity standard, 2026-10-18:
**54/54 valid runs**, with all planned outcomes retained. The expanded base
comparison has small, seed-dependent effects. CENTRAL's base mean throughput
and total-time improvements do not persist at 1.2x demand; at 0.8x demand its
fixed trigger never activates and its outcomes exactly equal H0. The CACC
sensitivity cases show tradeoffs between acceleration smoothness and traffic
metrics. This screen does not establish a consistent overall traffic benefit.

The [plan](m7-sensitivity-uncertainty-plan.md) at 655758b and
[frozen specification](m7-sensitivity-uncertainty-spec.md) at b4e968e precede
runtime implementation 1fb436c. Runtime source has not changed since that
implementation. The [machine report](../reports/m7/report.json),
[results, figure and activity table](../reports/m7/README.md), and
[independent raw audit](../reports/m7/independent_audit.json) are the primary
result artifacts. [PR #3](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/3)
publishes the package; acceptance does not imply it has been merged.

## Question and frozen design

Evaluate whether the fixed M6 comparison depends on operating demand, passenger
equipment, acceleration-message assumptions, requested controller settings and
random seeds. This is a bounded one-factor-at-a-time screen on calibration date
2025-10-08, not policy optimization or a probabilistic model of total uncertainty.

| Case | Change from fixed M6 settings | Policies | Seeds | Runs |
| --- | --- | --- | --- | ---: |
| base | None | H0, CACC, CENTRAL | 41-45 | 15 |
| demand_080 | Generated flow rates x0.8 | H0, CACC, CENTRAL | 41-43 | 9 |
| demand_120 | Generated flow rates x1.2 | H0, CACC, CENTRAL | 41-43 | 9 |
| penetration_000 | 0% equipped passengers | CACC | 41-43 | 3 |
| penetration_050 | 50% equipped passengers | CACC | 41-43 | 3 |
| range_050 | Leader query and message range 50 m | CACC | 41-43 | 3 |
| delay_1000 | Extra acceleration-message age 1 s | CACC | 41-43 | 3 |
| loss_020 | Deterministic 20% message loss | CACC | 41-43 | 3 |
| headway_2000 | Requested CACC headway 2 s | CACC | 41-43 | 3 |
| vsl_220 | Congested VSL target 22 m/s | CENTRAL | 41-43 | 3 |

All 54 full-window outcomes use the unchanged network, native vehicle types and
physical limits, 4% truck proxy, observed inputs, 0.5 s engine step, measurement
window [900,8100), one-second trajectory sampling and 7200 s clearance. No
settings were retuned after viewing results. Demand scaling occurs after measured
exit subtraction and before writing flow rates; observed speed profiles and
input hashes remain unchanged. Rounded emitted counts need not scale exactly.

Treatments pair by demand, date and exact seed. Non-demand sensitivities use
base H0 seeds 41-43, not the five-seed base mean. Their separate factor contrasts
subtract the corresponding base CACC/CENTRAL outcome on the same three seeds.
No dates, demand levels or factors are pooled.

## Results

Percentages below are mean paired differences divided by the mean of the exact
matching H0 seeds. Throughput is all modeled exits; total time includes scheduled
cohort insertion delay. Negative RMS acceleration indicates smoother exported
longitudinal acceleration. Metric directions alone do not define overall benefit.

| Case / policy | n | Throughput | Scheduled total time | RMS acceleration | Peak insertion backlog |
| --- | ---: | ---: | ---: | ---: | ---: |
| base / CACC | 5 | -0.212% | +0.709% | -0.775% | +0.810% |
| base / CENTRAL | 5 | +0.523% | -1.146% | +0.487% | -2.331% |
| demand_080 / CACC | 3 | -0.120% | +1.595% | -0.583% | -5.933% |
| demand_080 / CENTRAL | 3 | +0.000% | +0.000% | +0.000% | +0.000% |
| demand_120 / CACC | 3 | -0.385% | +0.270% | -0.741% | +0.446% |
| demand_120 / CENTRAL | 3 | -0.092% | +0.093% | -0.015% | -0.324% |
| penetration_000 / CACC | 3 | +0.000% | +0.000% | +0.000% | +0.000% |
| penetration_050 / CACC | 3 | -0.493% | +1.831% | -0.878% | +3.095% |
| range_050 / CACC | 3 | +0.002% | +0.029% | -0.452% | -0.797% |
| delay_1000 / CACC | 3 | -0.050% | +1.213% | -0.527% | +0.678% |
| loss_020 / CACC | 3 | -0.379% | +1.421% | -1.274% | +2.749% |
| headway_2000 / CACC | 3 | +0.369% | -0.620% | -0.042% | -0.119% |
| vsl_220 / CENTRAL | 3 | +0.252% | -0.592% | +0.270% | -2.416% |

The full 30-metric distributions, individual paired differences, sample SDs,
ranges and positive/negative/zero counts are in the machine report. The plotted
four-metric comparison shows individual seeds and mean +/- sample SD; these bars
are descriptive stochastic spread, not confidence intervals.

### Expanded base and demand

The H0 throughput mean/sample SD changes from 8274.50/29.44 veh/h over seeds
41-43 to 8266.00/46.99 over 41-45. Scheduled total time changes from
1533.90/6.49 s to 1540.50/13.99. The extra seeds expose more observed variation.

Five-seed CENTRAL minus H0 is +43.20 +/- 91.50 veh/h throughput and
-17.65 +/- 38.24 s scheduled total time. Both directions improve on only 3/5
seeds; their sample spreads exceed their mean effects. Five-seed CACC changes
throughput -0.212%, total time +0.709%, RMS acceleration -0.775% and backlog
+0.810%. RMS acceleration falls on all five seeds, with mixed traffic effects.

At 0.8x demand, all three CENTRAL controllers complete and restore native limits
with zero commands and zero limited-lane seconds. Every one of the 90 reported
metrics exactly matches same-demand H0. Retaining this inactive null result is
required by the frozen M7 acceptance rule; it is not a reason to tune the trigger.

At 1.2x demand, CENTRAL changes throughput -7.83 +/- 38.79 veh/h and total time
+2.45 +/- 18.72 s. All three activate (140 lane-limit commands each,
63,000-64,260 limited-lane seconds) and restore limits. The base mean improvements
do not persist in this operating condition. These small, dispersed differences
are not a statistical-significance or universal-harm claim.

### Equipment, messages and requested settings

Zero-equipped CACC has zero commands, equipped vehicles and equipped samples.
All 90 metrics, legacy whole-run metrics and detector-summary hashes exactly
match H0. Stable SHA-256 selection realizes approximately half of eligible
passenger vehicles at penetration 0.5; trucks stay native. Equipment is distinct
from command exposure because the native maneuver supervisor remains active.

Delay/loss affect acceleration feedforward only. A message must refer to the
current leader at the required history step; unavailable/dropped messages use
ACC with zero feedforward and no stale hold. Current local gap and speed remain
available. Deterministic hashes consume no simulator RNG. Realized packet loss
is 19.89-20.02% of message opportunities. The loss case has lower RMS acceleration
but longer scheduled total time and higher backlog than H0; it does not isolate
a benefit of V2V. The range case changes sensed following as well as messages,
so it is not a pure communication-range experiment.

Requested CACC headway 2 s leaves native Krauss tau fixed at 1.5 s. Its three-seed
mean changes versus H0 are +0.369% throughput, -0.620% scheduled total time,
-0.042% RMS acceleration and -0.119% peak backlog. Against base CACC on the same
seeds, throughput increases 55.00 +/- 31.43 veh/h and total time falls
19.97 +/- 31.89 s, while RMS acceleration increases 0.00615 +/- 0.00621 m/s².
These are favorable mean traffic changes within this case, with less smoothing
than base CACC; the settings were frozen before seeing them. Three seeds and
one calibration day do not identify an optimal headway.

VSL target 22 m/s changes the congested target while retaining the same trigger,
release, rate limit and original control/observation geography. Against H0,
throughput changes +20.83 +/- 73.62 veh/h and total time -9.08 +/- 32.71 s;
throughput improves on only 1/3 seeds and total time on 2/3. All controllers
complete and restore limits (224 commands each; 67,200-70,560 limited-lane
seconds). Against the base CENTRAL policy on identical seeds, the lower target
reduces throughput 8.67 +/- 5.25 veh/h and increases total time 6.00 +/- 4.87 s,
while reducing RMS acceleration 0.00160 +/- 0.00120 m/s² and peak backlog
22.00 +/- 19.31 vehicles. Each of those factor directions occurs on all three
seeds: the stronger intervention produces a tradeoff, not a uniform improvement.
The [paired factor contrasts](../reports/m7/factor_effects.json) show these changes
relative to their own base policy, with individual seeds and sample spread.
These are sensitivity observations, not settings selected for deployment.

## Validity, activity and acceptance evidence

All planned outcomes remain visible. The result table contains 0 rejected
outcomes; valid inactive/null controls are retained separately from failures.
Warnings, collisions, teleports, incomplete clearance, engine mismatch, CACC
native fallbacks or VSL restoration failures still reject a run. Default M6
actuation gates remain strict; only an explicit M7 configuration permits
inactivity. Aggregate means are null if any planned seed is absent, failed or
nonfinite; no surviving-seed means are reported.

| AC | Verified evidence | Status |
| --- | --- | --- |
| AC1 | Plan 655758b -> spec b4e968e -> runtime 1fb436c; frozen config exactly 54 outcomes | Pass |
| AC2 | Hand calculations, deterministic equipment/message boundaries, runtime message age, invalid inputs, real-SUMO native/null and deterministic degraded replay | Pass |
| AC3 | Full 165-test regression, lint, unchanged strict M6 gates and missing/failed/nonfinite suppression | Pass |
| AC4 | All 54 outcomes retained; matching-demand route/fleet/schedule checks; nine M6 and three zero-equipment exact replays | Pass |
| AC5 | 1620 independently recalculated raw metrics; 480 group/paired metric records; 28 factor records; 54 native metadata checks | Pass |
| AC6 | Versioned report, figure, failure/activity table, closeout, context/Obsidian/GitHub publication | Pass; final SHA recorded in publication handoff |

The raw auditor imports no production metric/controller implementation. It
independently reconstructs trips, summary health, one-second trajectories,
VSL decisions from interval totals, equipment selection and message accounting.
Matching routes, exported vehicle IDs/types/speed factors/reconstructed schedules,
frozen input/source hashes, every group/pair and percentage denominator are checked.
It exactly replays all 270 M6 values and all 90 zero-equipment values.
Fingerprint caches are reused only when run metadata, every raw XML/gzip/log and
controller diagnostic, and both auditor sources match; the final pass rehashes
that evidence. Full-corridor packet and live sensor histories are not exported,
so message timing also has hand-checked runtime and real-engine tests.

The separate [native metadata audit](../reports/m7/native_metadata_audit.json)
checks every native summary step (30,600 per completed run, 0-15,299.5 s), 0.5 s
grid, 7200 s clearance, scenario hash, frozen fleet, observation date, network
and engine provenance. The [measurement audit](../reports/m7/measurement_audit.json)
checks [900,8100), one-second samples, the 0.1 m/s stop threshold and finite metrics.
The [factor audit](../reports/m7/factor_audit.json) checks the four presentation
contrasts separately from their producer. The [verification record](../reports/m7/verification.json)
saves final counts, fingerprints, regression summary and plot inspection.

## Reproduce

Use the project-local SUMO/libsumo 1.27.1 environment and the accepted M2 network
and frozen M3 profiles/metadata. Raw PeMS files remain local prerequisites. Copy
the campaign config with a new campaign ID; never overwrite accepted output.

```sh
PYTHONPATH=src .venv/bin/python scripts/run_m7_sensitivity.py --config PATH_TO_NEW_CONFIG
.venv/bin/python scripts/audit_m7_results.py --config PATH_TO_NEW_CONFIG --report PATH_TO_NEW_RAW_REPORT --output PATH_TO_NEW_AUDIT
.venv/bin/python scripts/summarize_m7_results.py --report PATH_TO_NEW_RAW_REPORT --audit PATH_TO_NEW_AUDIT --output PATH_TO_NEW_PRESENTATION
PYTHONPATH=src .venv/bin/python -m pytest -q
.venv/bin/ruff check src tests scripts
```

Canonical local runtime evidence is under
`outputs/us101_corridor/m7/m7_ofat_2025_10_08/`. The shipped metadata checker runs
against `reports/m7/report.json` with `.venv/bin/python scripts/audit_m7_metadata.py`.
Large raw traces remain local; machine results and audit hashes are versioned.
The native engine step is 0.5 s, independent of the one-second FCD sample period;
FCD numerical checks use the exported default precision.

## Operational provenance

The user paused the campaign overnight at 27 completed runs. Suspended processes
were lost before continuation; three partial higher-demand CACC attempts were
archived and restarted from time zero with identical settings. All 27 completed
outcomes were reused. Later durable pause at 39 and live-memory storage pause at
42 preserved all completed evidence; the three delay runs continued from memory
on explicit authorization. No completed/rejected outcome was repeated for a
better result. The [recovery](../reports/m7/operational_recovery.json),
[durable pause](../reports/m7/paused_checkpoint.json),
[resume](../reports/m7/resume_checkpoint.json) and
[storage checkpoint](../reports/m7/storage_pause_checkpoint.json) preserve history.
The [communication checkpoint](../reports/m7/communication_checkpoint.json)
records the later 48-run audit.

Cloud-managed storage temporarily evicted runtime/source/Git files; a native
CLI using Apple's documented
[FileManager download API](https://developer.apple.com/documentation/foundation/filemanager/startdownloadingubiquitousitem(at:))
restored affected files. The user enabled Keep Downloaded, then freed storage.
The CLI guard enforced pause at or below 5 GiB; no automatic resume followed a
threshold pause. These interruptions concern evidence availability, not changes
to scientific acceptance. All work followed the user's CLI-only preference.

## Limits and next milestone

M3's held-out fidelity failure remains: combined speed MAE 14.90 mph, with
October 15 missing both fidelity targets. Unknown gross ramp flows remain.
Supervised CACC remains low-engagement; continuous CACC and rejected variants
remain unresolved. The chosen demand, communication and controller variations
are illustrative assumptions, not fitted probability distributions.

OFAT does not measure interactions. One calibration date with five/three seeds
cannot establish total uncertainty, confidence intervals, optimal policy, field
safety or deployment readiness. VSL sensing and actuation remain ideal. Seed
spread describes simulation randomness, not real-world forecast uncertainty.

All-exit throughput is not mainline capacity; stopped counts are queue proxies;
temporal speed variability is not wave stability; acceleration squared is not
energy. Scheduled total time and insertion backlog expose displaced delay that
actual-departure travel time can miss. [Primary-source methodology notes](../research/m7-methodology.md)
explain SUMO semantics, not empirical support for the chosen numeric factors.
M8 final research packaging is next; no M8 implementation is included here.

## Post-review reporting closeout, 2026-10-18

Both P2 findings from the independent PR reviews are resolved. M6 presentation
now rejects a report whose SHA-256 does not match the accepted audit, before
creating or changing outputs. M7 factor reporting and its independent checker
retain planned seed pairs and suppress aggregates for missing/failed runs,
missing/null/non-numeric/nonfinite metrics or nonfinite subtraction. The full
renderer is covered by a regression that previously reproduced the crash.

All 165 tests pass (20 added review regressions), with lint and whitespace clean.
Independent follow-up reviews found no residual issue in either fix. Regenerated
M6/M7 tables and figures and all 28 factor records are byte-identical to the
published artifacts. All 54 outcomes, findings and scientific interpretations
remain unchanged; no full-window simulation was rerun.

The [post-review verification](../reports/m7/post_review_verification.json)
records hashes, numeric boundary checks and independent follow-up reviews.
The original raw audit retains its original auditor fingerprint at 4c1d656;
its raw-auditor code is unchanged, with only the separate factor-validation
function updated. Current-code raw re-audits will correctly invalidate old
caches; their fingerprints were not rewritten. M7's experiment, findings,
analysis and review fixes are complete. PR #3 remains unmerged; M8 synthesis
is next and no further experiment is required for these reporting fixes.
