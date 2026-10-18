# Project memory and handoff

**Updated:** 2026-10-18
**Repository:** `sabcodes/bay-area-autonomous-traffic-simulation`
**Local Obsidian vault:** `Auto-Car Traffic Research`

## Purpose and current position

This project compares human-like traffic with explainable autonomous-vehicle
coordination policies on a US-101 corridor. The
[experiment charter](experiment-charter.md) defines the research question and
fair-comparison rules. The [roadmap](project-roadmap.md) is the milestone source
of truth: **M0–M7 practical experiment work is complete; M8 is next.**
M0–M7 practical experiment work is complete as of 2026-10-18. M7 is a conditional OFAT screen: 54/54 valid runs, 1620 independently recalculated raw metrics, 480 group/paired records, 28 independently checked factor records, 54 native metadata checks and 165 passing tests. M8 research packaging is next. M3 held-out fidelity and M5 low-engagement limits remain. See the
[M7 closeout](m7-sensitivity-uncertainty-report.md) and [frozen specification](m7-sensitivity-uncertainty-spec.md).
Earlier dated operational entries below are historical; all campaign processes
have completed and old PID/SIGCONT instructions must not be reused.
M4 is complete; the [harness closeout](m4-experiment-harness-report.md) records
its acceptance evidence.

## M2 decision to preserve

M2 is complete at the project's practical accuracy standard. Both directed
US-101 through routes and all 40 adjacent branch junctions were reviewed.
Four branch movements carry fixed H0 demand and 36 do not. Mathilda NB and
Rengstorff SB lane-count defects were corrected in versioned network patches.
The Shoreline NB and CA-85 SB exits each take the two rightmost lanes while
four continue. Three importer warnings remain visible and are accepted as
documented modeling approximations; West Maude/SR-237 is outside the US-101
mainline acceptance area. This decision does not assert exact as-built paint,
PeMS loop wiring, or calibrated managed-lane demand.

The accepted generated network SHA-256 is
`13103c0b31d22dff15159b56e5ba03f0becd9594868c4cdfeac60497e86b9bc6`.
The exact public OSM input snapshot and its provenance are versioned in
`data/osm/`, alongside the correction patch in `network/us101_corridor/patches/`.
The 40 branch paths have passenger-legal connections and terminate without
graph-boundary, depth-limit, or cycle outcomes. H0 seeds 41, 42, and 43 each
completed 13,482 vehicles without route, teleport, collision,
emergency-braking, or SUMO warning entries. These are network/run checks,
not calibration claims.

Read the [M2 acceptance record](us101-m2-acceptance.md),
[40-row checklist](us101-ramp-review-checklist.md),
[warning decisions](us101-importer-warning-review.md), and
[network audit](us101-network-audit.md) before changing the network.

## M3 closeout and stopping point

M3 execution now uses `scripts/run_m3_baseline.py` and
`configs/us101_m3_experiment.json`. Twelve bounded calibration cases are saved in
`reports/m3/candidates_report.json`. The final selection is `buffer_exit_tau15`
(1.5 s headway, 4% truck proxy, 700/2,000 veh/h net-entry and 1,500 veh/h
net-exit group assumptions). The 1,007.33 m upstream buffer uses the unchanged
M2 network and station 400790's separately labeled 80%-coverage inlet proxy;
comparison targets retain 90% coverage. Final calibration and sensitivities
are complete: 15/15 calibration runs cleared cleanly, 8.32% flow MAPE and
8.15 mph speed MAE. The frozen scenario is
`configs/us101_human_baseline_m3_frozen.json`; `reports/m3/freeze.json` records
the pre-validation treatment and source hashes. All six held-out validation
runs cleared cleanly and matched the frozen treatment. Combined errors were
19.37% flow MAPE and 14.90 mph speed MAE: the speed target was missed.
October 15 missed both targets (29.95%, 21.50 mph); October 16 met both
(8.79%, 8.30 mph). The October 15 upstream bottleneck was not reproduced.
This closes the practical M3 experiment, not a successful field-validation
claim. See the [closeout record](m3-human-baseline-report.md) and
[results](../reports/m3/README.md). Do not tune against these held-out errors.
The [staged plan](m3-human-baseline-plan.md) records the exact resume point.
M4 was authorized by a new user instruction on October 16, 2026. Its
[plan](m4-experiment-harness-plan.md) and [spec](m4-experiment-harness-spec.md)
preceded implementation; M3 settings and validation results remain frozen.
The [demand ledger](m3-demand-ledger.md) distinguishes measured
flows, group estimates, and omitted movements. Public 2024 Caltrans annual
truck/ramp inputs and their hashes are saved in `data/caltrans/`.

The split GP/express allocation cases with longer headways produced
teleports and are rejected. The final representative-day full-lane mean
errors are 8.38% flow MAPE and 5.93 mph speed MAE. The earlier no-buffer
15-run calibration is preserved separately (7.67% flow, 12.51 mph speed).
These calibration figures are separate from held-out validation. The reserved
dates were October 15–16, 2025; choices were frozen before running them. PeMS speeds are never
commands. The old nine-date average includes two Saturdays and is diagnostic
only. Provisional lane mappings remain modeling choices, not field-wiring
proof. See the [sensor audit](us101-sensor-audit.md) and
[ramp detector audit](us101-ramp-audit.md).

## M4 closeout and resume point

The spec-driven M4 sequence is complete: plan, specification, implementation,
checks, and real-run acceptance. Run `PYTHONPATH=src .venv/bin/python -m
bay_area_traffic_sim run-us101-experiment` with
`configs/us101_m4_experiment.json`. This declares H0 on October 8, 2025, seeds
41–43, 1 s samples, and a 0.1 m/s stop threshold. The report includes windowed
exit throughput, actual-departure travel times through clearance, stopped-queue
proxies, temporal variability of domain mean speed, and acceleration smoothness.

All three runs cleared 22,951 vehicles without SUMO warnings. Their legacy trip
metrics match M3 exactly; route files and detector summaries are byte-identical.
All 67 tests and lint passed. The [closeout](m4-experiment-harness-report.md) and
[versioned evidence](../reports/m4/README.md) record the exact acceptance checks.
Runtime traces stay under `outputs/us101_corridor/m4/m4_h0_2025_10_08/`; existing
experiment directories are preserved, so repeat with a new experiment ID.

Queue proxies exclude temporary insertion backlogs, travel-time cohorts use
actual departures, temporal speed variability is not a wave-stability test,
and acceleration smoothness is not energy use. M3's held-out failure remains
unchanged. At the M4 checkpoint, M5–M8 remained. The later M5 closeout below records that historical checkpoint; the current M7 closeout is at the end.

## Historical M5 closeout and resume point, 2026-10-16

M5 is complete for the [supervised comparison](m5-cooperative-cacc-report.md).
The original plan/spec commits c276d1f/9fe5c69 preceded source. The final
[revision-4 spec](m5-supervised-cacc-spec.md) at 75d4ad4 preceded runtime source
643d0da. All six runs accepted and each cleared 22,951 vehicles without SUMO
warnings. All 102 tests passed; the independent audit checked six raw outputs,
30 paired metrics, every aggregate, matching exported fleets/schedules and
unchanged source/route/network/input hashes. All H0 metrics and detector
summaries exactly replay M4. See [versioned results](../reports/m5/README.md).

This is a low-engagement supervisor: retain frozen physical treatment and
original gains, yield to all native maneuver/cooperation flags, and engage only
after 2 s of quiet state. Active requests cover 1.99–2.06% of all-run passenger
timesteps. Throughput changes -0.30%, scheduled total time +0.68%, RMS
acceleration -0.80%. These mixed changes do not demonstrate a traffic benefit.
Continuous CACC remains unresolved. The rejected overlay matrix had 2/1/2
teleports; a native-CACC probe had 40 emergency-braking warnings. All failures
and their correctly suppressed aggregates are preserved under reports/m5/.

Reproduce with configs/us101_m5_experiment.json and a new experiment ID. Final
raw outputs are under outputs/us101_corridor/m5/m5_h0_supervised_cacc_2025_10_08/.
libsumo 1.27.1 is project-local; three workers isolate engine state. The accepted
package is published in [PR #1](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/1)
and was merged into main at `0a56d5afe54d9b04f0a6326ebec5977dabbec77f`
on 2026-10-17 at 07:28:49 UTC. The pre-merge publication commit is `70409b8`.
M6 centralized control is next. M3's failed held-out fit remains unchanged.

## Working rules

- Use CLI access for Mac operations. If a GUI-only action is necessary, ask
  the user to perform it; the user explicitly declined Mac UI control during M7.

- Keep the repository documentation and versioned inputs authoritative for
  reproducibility. Obsidian is a navigable research notebook and handoff
  surface; link back to the relevant repository record when a finding changes.
- Rebuild the network and regenerate the branch ledger and routes after a
  topology change. Record the new network hash and rerun the relevant scenario.
- Preserve missing PeMS observations as missing, not zero.
- Compare later policies against H0 with the same network, demand window,
  vehicle mix, and seed set. Treat controller effects as unproven until M3
  calibration and separate-day evaluation are complete. M3's failed October 15
  fit remains a limitation of any later policy interpretation.

## Context synchronization

The M5 closeout, roadmap, README, and `CONTEXT.md` were synchronized on
2026-10-16. The matching Obsidian project area is
`Auto-Car Traffic Research/US-101 Traffic Simulation`; its project home,
milestones, source index, decisions, and M5 handoff point back to these
versioned records. GitHub's current branch remains the publication source of
truth; Obsidian publication checkpoints record the verified commit separately.


### M5 merge checkpoint

PR #1 was merged on explicit user request at 2026-10-17 07:28:49 UTC.
GitHub reported the PR mergeable with no configured status checks; the accepted
102-test and six-run evidence remains in the M5 closeout. Local main was
fast-forwarded to the merge commit. Obsidian publication records now distinguish
the historical PR checkpoint from the merged main state. M6 remains next.

## M6 implementation checkpoint, 2026-10-17

The [plan](m6-centralized-control-plan.md) at f1550ca and
[spec](m6-centralized-control-spec.md) at b50a22c preceded source 26a71d6.
M5 PR #1 merged while M6 was starting; use the attached isolated worktree
`/Users/sabarnoislam/.codex/worktrees/m6-centralized-control/Self Driving Cars Bay Area Traffic Simulation`
for M6. Do not switch or modify the shared primary checkout.
[PR #2](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/2)
is the M6 publication surface.

The frozen rule uses downstream simulated speed and upstream native lane limits:
30 s vehicle-timestep weighting, 15/20 m/s hysteresis, 25 m/s congestion target,
1 m/s limit changes and native clearance recovery. No network/demand/fleet/
physical-parameter changes. All 120 tests and lint passed. The 3000 s preflight
had zero SUMO warnings but no actuation (minimum interval speed 18.3452 m/s);
its false actuation acceptance is preserved without threshold tuning. Full
H0/CACC/CENTRAL seeds 41-43 are running. Final acceptance is pending; preserve
M3's held-out failure and M5's low engagement.

## Historical M6 closeout and resume point, 2026-10-17

Nine of nine runs accepted, each clearing 22,951 vehicles with zero SUMO warnings, collisions, teleports or final running/waiting/discarded vehicles. All 125 tests and lint pass. The independent audit verifies 270 raw metrics, 90 paired metrics, every VSL decision, matching exported fleets/schedules, and exact H0/CACC replay against M5. Every central run has nonzero actuation and restored native limits.

CENTRAL versus H0 changes mean all-exit throughput +0.36%, scheduled-cohort total time -0.98%, RMS acceleration +0.47%, and peak insertion backlog -1.63%.

The [closeout](m6-centralized-control-report.md), [plan](m6-centralized-control-plan.md),
[specification](m6-centralized-control-spec.md) and [results](../reports/m6/README.md)
are authoritative. The 3000 s preflight did not activate; preserve it. The full
window satisfies actuation without changing thresholds, geography or gains.
M3 field-fidelity and M5 low-engagement caveats remain. M7 sensitivity and M8
research packaging are next; no further policy is authorized by this closeout.

M6 PR #2 is merged into main at [ef8d20c](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/commit/ef8d20c196298de88509097c06e5a7c40782de3f).
The attached M6 worktree retains the accepted raw outputs. Runtime source 26a71d6 is pinned by report hashes.
The accepted raw path is outputs/us101_corridor/m6/m6_h0_cacc_central_vsl_2025_10_08/.
The publication checkpoint is recorded separately in Obsidian after Git push.

## M6 merge checkpoint, 2026-10-17

[PR #2](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/2)
merged into main at [ef8d20c](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/commit/ef8d20c196298de88509097c06e5a7c40782de3f) on
2026-10-17 at 01:07:35 America/Los_Angeles (08:07:35 UTC), on explicit user
request. Runtime, tests, configurations and accepted reports exactly match the
reviewed PR head 1c9dfde. The 125-test and independent audit evidence remains
applicable. M7 sensitivity is next; no M7 implementation has started.

## M7 implementation checkpoint, 2026-10-17

The user authorized M7 through plan, specification, implementation, measured
verification and Obsidian/context/GitHub updates. Plan 655758b and specification
b4e968e precede implementation 1fb436c. The frozen OFAT campaign has 54 runs:
base H0/CACC/CENTRAL seeds 41-45; demand 0.8/1.2, penetration 0/0.5, range 50 m,
extra delay 1 s, loss 20%, requested headway 2 s and VSL target 22 m/s on 41-43.
All 140 initial tests and lint passed; strengthened inactivity tests follow.

Run: `PYTHONPATH=src .venv/bin/python scripts/run_m7_sensitivity.py`.
Raw path: `outputs/us101_corridor/m7/m7_ofat_2025_10_08/`. Existing campaign
paths are never overwritten. Independent raw audit and final acceptance are
pending. The working branch is `codex/m7-sensitivity-uncertainty` in the primary
checkout; no other chat should switch it during this campaign.
[Draft PR #3](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/3)
is the publication surface. The initial push approval block was resolved by
verifying the existing private repository and account admin access. Obsidian
plan/spec/decisions and implementation checkpoint were verified through CLI.
M3 fidelity, M5 low engagement, and all M6 limitations remain.

## M7 evidence-storage checkpoint, 2026-10-17

At 24/54 clean runs, iCloud optimization evicted 86 M7 files. An independent
raw audit encountered `TimeoutError: [Errno 60]` during SHA-256 fingerprinting,
after its numeric checks. This was a local-file availability problem, not a
simulation failure. Mac UI access was declined; the user explicitly requested
CLI access or a request for their help. Do not use Mac UI control.

Apple's documented FileManager `startDownloadingUbiquitousItem(at:)` API restored
all 86 files through a small native Objective-C CLI under outputs/; the Swift
command-line toolchain had an unrelated module-definition error. Cloud-only
file count returned to zero. No global settings, simulation reruns or treatment
changes were needed. The incremental audit now restores cloud-only M7 files
through CLI and retries transient reads at most three times. Auditor source,
raw metric checks and cache fingerprint rules are unchanged. Active audit
session changed to 86160; campaign session 78457 continues. This runtime session
reference is a temporary handoff aid, not scientific evidence.

Primary API source: https://developer.apple.com/documentation/foundation/filemanager/startdownloadingubiquitousitem(at:)

## M7 paused by user, 2026-10-17 02:43 America/Los_Angeles

User requested an overnight pause, including the run. SIGSTOP suspended both
process trees; all nine processes report stopped status T. Completed: 27/54,
all valid and independently audited. Higher-demand CACC seeds 41/42/43 are
paused at summary times 7223.0/7218.5/7275.0 s. The current simulation state is
in process memory, not a serialized SUMO checkpoint. Keep Codex open and do not
reboot/terminate these processes. Resume only after the user requests it.

Local identities and start times are saved in outputs/m7_pause_state.json;
outputs/resume_m7.py validates every identity before sending SIGCONT. Campaign
session 78457, audit session 38010. Do not start a second campaign. If processes
are lost, preserve existing evidence and design a documented recovery rather
than invoking the non-resumable runner against its existing directory.

Fresh regression: 145 tests pass (16.45 s), lint and whitespace pass. Runtime
source remains unchanged. Final audit, remaining 27 runs and closeout/publication
remain pending. Draft PR #3 stays unmerged. No automatic morning restart set.

## M7 explicit resume and interruption recovery, 2026-10-17

The user requested continuation. The guarded SIGCONT helper found the paused
processes no longer existed; it sent no signals. All 27 completed outcomes and
raw-audit caches remained intact. No serialized SUMO state had been saved.
The recovery dry run verified source/input/campaign hashes and identified 27
completed, three interrupted, and 24 unstarted planned runs. Partial evidence
was moved into outputs/m7_interruptions/20261018T033611876447Z/ before restarting
the same three case/policy/date/seed combinations. No rejected/completed outcome
was retried and no controller, matrix, sampling or validity setting changed.

The operational driver is outputs/recover_m7.py, with SHA recorded in the
[versioned recovery record](../reports/m7/operational_recovery.json). It reuses
the unchanged harness job runner and statistical functions, keeps existing
completed case reports, and assembles remaining reports from retained and new
outcomes. Campaign session 75309 and audit session 24202 are the current local
sessions. Earlier paused-process identities are historical and must not be
resumed. CLI-only user preference remains. Final acceptance is still pending.

## Higher-demand checkpoint, 2026-10-17

All nine demand x1.2 outcomes pass and are independently audited, taking the
campaign to 33/54. A separate calculation checks all 90 higher-demand group/paired
metric records. CENTRAL minus matching H0: throughput -7.83 +/- 38.79 veh/h
(-0.0924%), scheduled total time +2.45 +/- 18.72 s (+0.0932%), RMS acceleration
-0.0154%, and peak insertion backlog -0.3238%. All three CENTRAL runs activate
(140 lane-limit commands; 63,000-64,260 limited-lane seconds) and restore limits.
The base mean throughput/time improvements do not persist in this demand case;
seed spreads exceed these small mean effects. This is not a significance claim.

Higher-demand CACC changes throughput -0.3853%, scheduled total time +0.2698%,
RMS acceleration -0.7409%, and peak backlog +0.4458%. Active passenger command
share remains 2.1095-2.1391%. CACC's traffic tradeoffs remain mixed. Equipment
and communication sensitivity results are pending; no settings were retuned.

## Zero-equipment checkpoint, 2026-10-17

All three zero-equipment CACC runs are valid and independently audited, taking
the campaign to 36/54. Each exactly matches same-seed base H0 on all 30 metrics
(90 exact values), legacy whole-run metrics and detector-summary SHA-256.
There are zero equipped vehicles, equipped samples or commands; all eligible
passengers remain native. This is the specified full-corridor null-control
check, not an inactive-run rejection. Remaining equipment/communication and
controller-setting cases are pending.

## User-requested storage pause at completed boundary, 2026-10-17

Free space fell from about 13 GiB to 2.6 GiB during the resumed campaign.
The user chose pause at the next completed batch. The coordinator was suspended
first so no following case could launch; the half-equipment runs finished and
all three raw audits completed. Final state: 39/54 valid runs and independent
raw audits (1,170 metric values); 15 unstarted; zero incomplete runs. Simulation,
audit, final-check waiter and storage-guard process trees were then stopped
and terminated. All scientific outputs and caches are durable on disk. Codex
may close; no live-memory state is required. Previous PID/SIGCONT instructions
are historical and must not be used.

The versioned reports/m7/paused_checkpoint.json records hashes and remaining
cases: range_050, delay_1000, loss_020, headway_2000, vsl_220. The coordinator
stopped before building the completed penetration_050 case report, so the root
campaign report still lists 36 results; all 39 per-run result files are intact.
This is report assembly pending, not lost or incomplete simulation evidence.

Resume only on explicit user request, preferably with at least 10 GiB free:
first dry-run PYTHONPATH=src .venv/bin/python outputs/recover_m7.py. It must
find 39 retained, zero interrupted and 15 unstarted runs, and matching frozen
source/input/config hashes. Then --execute rebuilds the completed case report
without rerunning any completed outcome, before launching the final 15.
Restart the independent auditor and final-check waiter with PYTHONPATH=src.
No automatic restart is scheduled. Final campaign/fleet/group/factor audit,
plots, acceptance closeout and final publication are still pending.

## Explicit continuation after freeing storage, 2026-10-17

The user requested continuation after freeing space, with further iCloud uploads
expected to release storage. CLI measured about 7.1 GiB free at restart; the
additional expected space is not counted until available. All 39 result hashes,
runtime source and frozen config matched the paused checkpoint. Recovery found
39 retained, zero interrupted and 15 unstarted runs. No completed outcomes were
rerun. The half-equipment child report was rebuilt from its three existing
results; the root campaign report now includes all 39 completed outcomes.

The remaining five cases continue unchanged. CLI storage guard suspends M7 if
free space falls below 2 GiB. Active local sessions: campaign 7414, independent
audit 12972, storage guard 62935, final-check waiter 14302. These supersede all
previous session/PID references. Final acceptance remains pending. The versioned
reports/m7/resume_checkpoint.json records this continuation and recovery hash.

## User storage threshold update, 2026-10-17

The user explicitly instructed: pause if free storage reaches 5 GiB. The CLI
guard now checks every five seconds and suspends all M7 simulation, audit and
final-check process trees at or below 5 GiB. This supersedes the earlier 2 GiB
threshold. Measured space immediately after the change was about 6.5 GiB.
The replacement guard session is 71913; campaign7414, audit12972 and final
checks14302 continue. Do not automatically resume a threshold-triggered pause.

## Storage-triggered user pause, 2026-10-18

The user's 5 GiB rule triggered. Available space dropped sharply between
five-second samples; the guard observed about 0.23 GiB and suspended all ten
M7 simulation/audit/final-check processes. Storage subsequently recovered to
about 7.6 GiB. Do not automatically resume: the user-requested pause remains.
All ten suspended process commands/start times and T states were verified.

Completed: 42/54 valid and independently audited, covering 1,260 raw metric
values. The range_050 case is complete. Three delay_1000 seeds are suspended
at summary times 3645.5/3563.0/3623.5 s (41/42/43); nine runs in loss_020,
headway_2000 and vsl_220 are unstarted. Completed outputs/caches are on disk;
the three unfinished runs depend on live memory. Keep Codex and this Mac
session open to preserve their exact state. This supersedes the earlier
completed-batch pause's safe-to-close guidance.

Use outputs/resume_m7_storage.py WITHOUT --resume for read-only identity/state
verification. On explicit user request, --resume verifies all identities and
free space >5 GiB before SIGCONT; immediately restart the 5 GiB disk guard.
It archives the old pause record. Old outputs/resume_m7.py identities are stale.
If these processes are lost, archive the three partial runs and resume with
outputs/recover_m7.py, retaining all 42 completed outcomes and frozen settings.
Current live paused sessions: campaign7414, audit12972, final-check14302; guard
71913 exited after suspending them. Final native metadata check is prepared
in outputs/m7_native_metadata_audit.py for after the full 54-run report exists.
Final campaign/fleet/replay/group/factor checks, plots, 145-test regression,
closeout and final publication remain pending. No M7 acceptance claim yet.

## Explicit live-process resume, 2026-10-18

The user authorized continuation. Free space measured 11.7 GiB. All ten paused
process commands, start times and stopped states matched before SIGCONT; the
three delay runs resumed from their preserved positions without rerunning.
The old local pause record was archived under outputs/m7_storage_pause_history/.
The 5 GiB guard restarted as session89111. Campaign7414, audit12972 and final
checks14302 remain active; 42 completed valid/audited outcomes are retained.
No scientific settings changed. The remaining 12 outcomes and full final
verification, native metadata audit, plots and closeout are still pending.

## Communication and live-process checkpoint, 2026-10-18

M7 is active as of 2026-10-18: 48/54 valid and independently raw-audited outcomes. Delay and packet-loss cases are complete; three headway runs are underway, followed by three VSL runs. Storage is about 29 GiB free with the user-requested pause at or below 5 GiB. Final campaign acceptance remains pending.

Campaign session7414, independent audit12972 and storage guard89111 continue.
Final checker74488 supersedes14302 and waits for both 54 outcomes and 54 raw
audits. Run outputs/m7_native_metadata_audit.py after the final report exists.
Then inspect plots, finish the closeout and AC1-AC6, synchronize Obsidian/context
and publish PR #3 ready for review. Do not merge without user request.
See reports/m7/communication_checkpoint.json for independently checked delay/loss
group records. All completed outcomes and frozen runtime settings are retained.

## Initial M7 closeout, 2026-10-18

M0–M7 practical experiment work is complete as of 2026-10-18. M7 is a conditional OFAT screen: 54/54 valid runs, 1620 independently recalculated raw metrics, 480 group/paired records, 28 independently checked factor records, 54 native metadata checks and 145 passing tests. M8 research packaging is next. M3 held-out fidelity and M5 low-engagement limits remain.

Plan 655758b -> frozen spec b4e968e -> runtime 1fb436c. Source remained unchanged
through all 54 outcomes. All nine original M6 runs exactly replay 270 metrics;
zero equipment replays 90 H0 values, legacy metrics and detector summaries.
The full independent audit verifies matching-demand routes/fleets/schedules,
raw trips/summary/trajectories, VSL decisions, equipment/message accounting,
source/input hashes and all statistics. Native grids are 30,600 half-second
steps per run with unchanged 7200 s clearance. Lint and whitespace pass.

The five-seed base CENTRAL mean throughput/time changes are +0.523%/-1.146%,
with larger paired seed spreads and favorable directions on 3/5 seeds.
At demand x0.8 it remains inactive and exactly equals H0; at x1.2 those small
mean improvements do not persist. CACC sensitivity results have mixed traffic
tradeoffs. No settings were retuned and no overall benefit is established.

See [final closeout](m7-sensitivity-uncertainty-report.md), [results/plot/activity table](../reports/m7/README.md), [machine report](../reports/m7/report.json),
[raw audit](../reports/m7/independent_audit.json), [factor audit](../reports/m7/factor_audit.json)
and [metadata audit](../reports/m7/native_metadata_audit.json).
Raw evidence remains local under outputs/us101_corridor/m7/m7_ofat_2025_10_08/.
Prior operational checkpoints retain pause/recovery history. All simulation,
incremental audit, final-check and storage-guard processes have finished.
No future run or restart is scheduled. User preference remains CLI-only and
pause at or below 5 GiB for future authorized long runs.

Branch codex/m7-sensitivity-uncertainty publishes [PR #3](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/3).
The final publication SHA is recorded in Obsidian after push. The PR is ready
for review and unmerged; do not merge or start M8 without a new user request.
OFAT does not estimate interactions/total uncertainty, and seed SD is not a
confidence interval. Preserve M3 fidelity, unknown gross ramp flows, native
supervision and ideal VSL limits; no capacity/energy/field-safety claim follows.

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
