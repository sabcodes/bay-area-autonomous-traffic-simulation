# M7 sensitivity and uncertainty closeout

**In progress, 2026-10-18: 48/54 valid and independently audited. Headway and VSL cases remain; final acceptance pending.**

The [plan](m7-sensitivity-uncertainty-plan.md) at 655758b and
[specification](m7-sensitivity-uncertainty-spec.md) at b4e968e precede runtime
implementation 1fb436c. [PR #3](https://github.com/sabcodes/bay-area-autonomous-traffic-simulation/pull/3)
is the publication surface. The frozen config is
`configs/us101_m7_sensitivity.json`.

## Question and design

Evaluate whether the fixed M6 comparison is sensitive to operating demand,
passenger equipment, acceleration-message assumptions, requested controller
settings and random seeds. This is a bounded OFAT screen on 2025-10-08, not an
optimizer or a model of total uncertainty. Fifty-four fresh full-window runs
use the unchanged M3/M6 network, observed inputs, native behavior, physical
limits, fleet mix, measurement window [900,8100), 0.5 s step and 7200 s clearance.

The base comparison uses H0/CACC/CENTRAL seeds 41-45. Demand x0.8/x1.2 uses all
three policies on 41-43. Other factors use 41-43: passenger equipment 0/50%,
leader range 50 m, extra acceleration-message delay 1 s, 20% message loss,
requested CACC headway 2 s, and congested VSL target 22 m/s. Every policy pairs
with H0 at the same demand, date and seed. Non-demand factors also compare
with the same base policy using the identical three-seed subset.

Equipment is selected by a stable SHA-256 rule on passenger ID; trucks remain
native. Messages use a separate hash of follower, leader and simulation step.
These selections do not consume SUMO RNG. A delayed message must belong to the
current leader; unavailable or dropped acceleration uses ACC, without stale
hold. Current local gap and speed remain available. The range case changes
both sensed leader following and communication, so it is not a pure packet
range experiment. Requested headway changes leave native Krauss tau at 1.5 s.
VSL still controls the original 14 lane segments using nine downstream lanes.

## Acceptance traceability

| AC | Evidence | Status |
| --- | --- | --- |
| AC1 | Plan 655758b, spec b4e968e, runtime 1fb436c; frozen 54-run config | Verified |
| AC2 | Hand calculations, hash/message/delay boundaries, invalid settings, real SUMO deterministic and zero-equipment tests | Verified |
| AC3 | Existing strict M6 gates, valid-inactive M7 versus failed restoration, nonfinite/missing/failed aggregation checks | Tests pass; final regression pending |
| AC4 | Fresh matrix, matching-demand route/fleet/schedule checks, exact M6 and zero-equipment replay | In progress |
| AC5 | Independent raw trips/summary/trajectory metrics, VSL ledger, equipment/message accounting, inputs, aggregates and fingerprints | In progress |
| AC6 | Machine report, plots, validity/activity table, interpretation, context/Obsidian/GitHub | In progress |

M7 distinguishes execution validity from activity. Zero equipment and
nonactivating VSL are intentional null cases, while warnings, collisions,
teleports, incomplete clearance, wrong engines, CACC native fallbacks or VSL
restoration failures still reject the run. Means are null unless every planned
seed and metric qualifies. Individual outcomes and failure reasons remain.

## Preliminary H0 seed expansion

All five H0 seeds are clean and independently audited; original seeds 41-43
match all 90 M6 metrics exactly. Throughput mean/sample SD changes from
8274.50/29.44 to 8266.00/46.99 veh/h. Scheduled total time changes from
1533.90/6.49 to 1540.50/13.99 s. These describe H0 only; controller and full
sensitivity results remain pending. The wider observed spread illustrates
why three seeds should not be mistaken for a complete uncertainty estimate.

## Expanded base comparison checkpoint

All 15 base runs pass clean clearance. All nine original M6 runs match every
one of their 270 metric values exactly. Five-seed paired CENTRAL minus H0:
throughput +43.20 +/- 91.50 veh/h (+0.52%), scheduled total time -17.65 +/-
38.24 s (-1.15%), RMS acceleration +0.49%, peak insertion backlog -2.33%.
Throughput improves on 3/5 seeds and total time falls on 3/5; spreads exceed
mean effects. Five-seed CACC changes throughput -0.21%, scheduled total time
+0.71%, RMS acceleration -0.77% and peak backlog +0.81%. RMS acceleration
falls on all five CACC seeds, but the traffic tradeoffs remain mixed.
These are base-case findings; sensitivity conclusions remain pending. A
separate calculation checked all 90 base group/paired metric summaries.

## Reduced-demand checkpoint

All nine demand x0.8 runs pass clean clearance. The VSL never activates in
any of the three CENTRAL seeds: zero commands and zero limited-lane exposure,
with completed/restored controllers. All 90 CENTRAL metric values exactly
match same-demand H0. This is a valid inactive/null control under the frozen
M7 rule, not a reason to change the trigger. CACC minus H0 changes throughput
-0.12%, scheduled total time +1.59%, RMS acceleration -0.58% and peak insertion
backlog -5.93%. Active commands remain 2.13-2.19% of passenger timesteps.
Higher-demand and other sensitivity outcomes remain pending.

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

## Reproduce and audit

Prerequisites remain the project-local SUMO/libsumo 1.27.1 environment, frozen
M3 observed profiles and metadata, and accepted M2 network. Raw PeMS files are
local prerequisites and are not published by M7. Use a new campaign ID and
output/audit directory for an exact replay; existing runs are never overwritten.

```sh
PYTHONPATH=src .venv/bin/python scripts/run_m7_sensitivity.py --config PATH_TO_NEW_CAMPAIGN_CONFIG
.venv/bin/python scripts/audit_m7_results.py --config PATH_TO_NEW_CAMPAIGN_CONFIG --report PATH_TO_NEW_REPORT --output PATH_TO_NEW_AUDIT
.venv/bin/python scripts/summarize_m7_results.py --report PATH_TO_NEW_REPORT --audit PATH_TO_NEW_AUDIT --output PATH_TO_PRESENTATION
```

The shipped raw path is `outputs/us101_corridor/m7/m7_ofat_2025_10_08/`.
The auditor imports no production metric/controller implementation. It reuses
the independent M6 NumPy trajectory parser, independently reconstructs trips,
health, VSL decisions from recorded interval totals, equipment selection and
message accounting, and verifies every group/pair. Full-corridor packet and
live sensor histories are not exported; communication timing and loss behavior
also have deterministic real-engine integration checks. Fingerprinted caches
reuse a raw audit only when run metadata, every raw file and both auditors match.

## Local evidence availability

During the sweep, iCloud evicted 86 runtime evidence files and a raw-audit
fingerprint read timed out. Apple's documented
[FileManager download API](https://developer.apple.com/documentation/foundation/filemanager/startdownloadingubiquitousitem(at:))
restored them through a native CLI. Cloud-only count returned to zero; raw
checks and cache fingerprints were retained. No simulation reruns or policy
changes followed. Mac operations remain CLI-only at the user's request.
Keep raw evidence locally available when reproducing audits in cloud-managed
folders; local availability is separate from scientific run acceptance.

## Pause and recovery

The user paused the simulation and audit processes at 27 completed/audited runs.
On explicit continuation, the suspended processes no longer existed. Their
partial outputs were retained under the local interruption archive, and the
three interrupted demand x1.2 CACC seeds were restarted from time zero with
identical settings. The 27 completed outcomes were reused unchanged; 24 other
planned runs had not started. These process interruptions are operational
history, distinct from scientific run rejection. See the
[recovery record](../reports/m7/operational_recovery.json) for source hashes,
retained/interrupted/unstarted paths and recovery-driver hash.

## Completed-batch pause and continuation

The user chose to pause at a completed batch boundary after free space fell
to approximately 2.6 GiB. All 39 completed outcomes have independent raw checks
(1,170 metric values); 15 runs remain unstarted and none is incomplete.
All M7 processes have stopped. Results and caches are durable on disk; see the
[paused checkpoint](../reports/m7/paused_checkpoint.json). Final acceptance,
full campaign-level statistics/replay auditing and plots remain pending.
The user subsequently freed space and explicitly resumed. The measured restart
space was about 7.1 GiB. The CLI storage guard initially paused below 2 GiB;
the user subsequently raised the threshold to pause at or below 5 GiB. All 39 result
hashes matched, no completed runs were repeated, and the final 15 continue.
See the [resume checkpoint](../reports/m7/resume_checkpoint.json).

## Storage threshold pause and explicit resume

The user's 5 GiB threshold triggered on 2026-10-18. The guard sampled a rapid
space drop at about 0.23 GiB and suspended all M7 process trees. Space recovered
to about 7.6 GiB, but the run remains paused. Forty-two outcomes and all their
raw checks are complete (1,260 metric values); three delay cases are suspended
in memory and nine runs have not started. See the
[storage pause checkpoint](../reports/m7/storage_pause_checkpoint.json).

The user subsequently authorized continuation with 11.7 GiB free. All ten
process identities matched, the delay runs resumed from memory, and the 5 GiB
storage guard remains active. No completed outcomes were rerun.

The completed range case changes throughput +0.0020%, scheduled total time
+0.0292%, RMS acceleration -0.4524% and peak insertion backlog -0.7974% versus
matching three-seed H0. Active passenger share is 2.0303-2.0620%. A separate
calculation checked all 30 range group/paired metric records. This factor
alters sensed leader following as well as acceleration-message range.

## Communication checkpoint, 2026-10-18

All three extra-delay and all three packet-loss runs are valid and independently
raw-audited, taking the campaign to 48/54. A separate stdlib calculation checked
all 60 delay/loss group and paired metric records, including same-seed H0
references, sample SDs, ranges, signs and percentage denominators. Runtime
source remains unchanged since 1fb436c. See the
[communication checkpoint](../reports/m7/communication_checkpoint.json).

Against matching H0, extra acceleration-message delay 1 s changes throughput
-0.0504%, scheduled total time +1.2132%, RMS acceleration -0.5268% and peak
insertion backlog +0.6784%. Packet loss 20% changes throughput -0.3787%, total
time +1.4209%, RMS acceleration -1.2739% and backlog +2.7493%. Packet loss is
realized at 19.89-20.02% of message opportunities. These are mixed outcomes,
not an overall benefit or a pure V2V contribution. Only acceleration feedforward
is delayed or dropped; current local gap and speed remain. The supervisor
still limits engagement to roughly 2% of passenger timesteps.

The three headway runs are underway; VSL target runs follow. Free space is
about 29 GiB and the 5 GiB CLI pause guard remains active. The final checker now
waits for both all 54 outcomes and all 54 incremental raw audits before running
the full campaign/fleet/replay/statistics checks. Final interpretation and
publication remain pending.

## Limits and next milestone

M3 failed held-out fidelity remains (combined speed MAE 14.90 mph; October 15
missed both targets). Supervised CACC remains low-engagement; continuous CACC
and its rejected variants remain unresolved. Demand factors and communication
settings are illustrative assumptions, not fitted probability distributions.
OFAT does not identify interactions. One calibration date and five/three seeds
cannot establish total uncertainty, confidence intervals, an optimal policy,
field safety or deployment readiness. VSL sensing and actuation remain ideal.

All-exit throughput is not mainline capacity; stopped counts are queue proxies;
temporal speed variability is not wave stability; acceleration squared is not
energy. Scheduled total time and insertion backlog help expose displaced delay.
[Primary-source notes](../research/m7-methodology.md) explain SUMO semantics,
not empirical justification for the chosen numerical sensitivities. M8 final
research packaging follows after M7 acceptance.
