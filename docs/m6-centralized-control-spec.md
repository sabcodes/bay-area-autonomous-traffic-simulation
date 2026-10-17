# M6 centralized variable speed limit specification

Written 2026-10-17 after plan f1550ca and before implementation. Policy settings
are frozen before outcome evaluation. This is CENTRAL on human-like traffic;
it is separate from CACC, not a combined policy.

## SC1: policy and geography

Use lane.setMaxSpeed with native Krauss following, lane changing, routing and
safety modes unchanged. All vehicle classes respond through native behavior;
speed factors still apply, so this is a lane limit, not a guaranteed vehicle
speed cap or a field compliance model. No per-vehicle commands or neighbor scans.
Control every lane of the existing upstream buffer edges 395354963, 28485321,
and 28485321-AddedOffRampEdge (1007.33 m; 14 lane segments). Observe all lanes
on the immediately downstream edges 509747302 and 509747310-AddedOnRampEdge
(503.97 m; 9 lane segments). Do not change topology or serialized route XML.
Resolve lane IDs from exact edge membership, validate nonempty/disjoint unique
edge lists before launch and actual lane existence/positive native speeds at
runtime. Preserve each original lane limit and never raise it above native.

## SC2: rule and timing

At each 0.5 s simulation step collect last-step vehicle count and mean speed
from the nine observed lanes. Across each nonoverlapping 30 s interval compute
sum(count * speed) / sum(count), a vehicle-timestep-weighted simulated mean.
Empty lanes contribute zero weight; invalid counts or populated speeds fail.
A completely empty interval releases congestion mode. Initial mode is free.
At interval end: mean < 15 m/s activates congestion; mean > 20 m/s releases;
equality or the intermediate band preserves the prior mode. In congestion,
target min(native,25 m/s); otherwise target native. Move each current limit
toward target by at most 1 m/s per update, including recovery. First decision
is at 30 s after sampling 60 steps, effective for the next simulation step.
Control from warmup through measurement; at 8100 s disable feedback, then
recover at 1 m/s per 30 s during clearance. Never use PeMS target speeds.
Restore original limits on normal completion or error before closing SUMO.
Record cleanup success; failure to restore fails acceptance.

## SC3: configuration and evidence

Explicit policy=central_vsl, backend=libsumo, control_edge_ids, observation_edge_ids,
update_seconds=30, activate_below_m_per_s=15, release_above_m_per_s=20,
congested_limit_m_per_s=25, max_change_m_per_s=1, control_end_seconds=8100.
Reject unknown/missing keys, booleans/nonfinite/invalid numeric ranges, reversed
thresholds, nonaligned update/end times, empty/duplicate/internal/overlap edges,
and invalid backend before simulation. Only libsumo is required for M6.
Emit diagnostics even on failure: actual engine version, lane IDs/native limits,
completed/restored flags, update count, changed-lane command count, active
limited-lane seconds, and an update ledger of interval weight, weighted speed,
congestion mode and applied lane limits. The ledger includes clearance recovery.

## SC4: comparison and acceptance

Fresh unchanged H0, accepted supervised CACC, and CENTRAL runs on 2025-10-08,
seeds 41-43, three isolated workers. Keep frozen network, demand, fleet, driver
parameters, 0.5 s step, measurement [900,8100), and 7200 s clearance. Reuse all
30 M4/M5 metric definitions. Pair CENTRAL-H0 and CACC-H0; also publish CENTRAL-
CACC paired differences. Preserve failures and suppress failed aggregates.
Every run requires no warnings, collisions or teleports; all 22,951 loaded
vehicles must insert and finish, with zero running/waiting/discarded vehicles.
CENTRAL additionally requires matching engine, completed/restored diagnostics,
nonzero updates, nonzero changes and nonzero limited-lane exposure. CACC retains
all M5 gates. A traffic benefit is not an acceptance requirement.

## SC5: validation and publication

Tests: hand-calculated weighted observations and strict hysteresis boundaries,
empty-data release, rate limits and clearance, configuration rejection, unknown
lanes, real toy SUMO deterministic replay with visible speed-limit changes,
cleanup after errors and failure-gate/paired-comparison regressions.
Run a 3000 s corridor preflight before the full matrix; retain its health and
ledger even if rejected. No performance tuning after outcomes. Independent
raw-output audit must recalculate trip/summary and trajectory metrics, replay
every central decision from recorded observations, verify native-limit/rate
bounds, exact H0 and CACC metrics/diagnostic replay against M5, equal route and
network/input provenance, and identical exported vehicle IDs/types/speed factors/
reconstructed intended schedules. Recompute every aggregate and paired delta.
Publish versioned report, audit, comparison table/figure, reproduction command,
plan/spec/source commits, caveats and synchronized context/Obsidian/GitHub.

## Interpretation and sources

Central sensing is ideal and simulated, thresholds are illustrative rather than
field calibrated, and the inlet-adjacent policy may shift delay into insertion
backlogs. Limited-lane seconds measure actuation, not fleet compliance. One
calibration day and three seeds estimate seed spread only. M3's failed October
15 fit and M5's approximately 2% engagement remain explicit limitations; no
field safety, energy, optimality, deployment or string-stability claim follows.

Primary API references checked 2026-10-17:
https://sumo.dlr.de/docs/TraCI/Change_Lane_State.html
https://sumo.dlr.de/docs/TraCI/Lane_Value_Retrieval.html
Installed SUMO/libsumo 1.27.1 is the runtime authority for integration checks.

## Preflight disclosure, before the full matrix

The 3000 s seed-41 probe completed/restored with zero SUMO warnings, but its
actuation gate is false: the minimum observed 30 s mean was 18.3452 m/s, above
the frozen 15 m/s trigger. No commands were issued. This nonactivating probe is
preserved in reports/m6/preflight_seed41.json. The full window will be evaluated
without changing thresholds or geography; final acceptance still requires
nonzero lane-limit actuation. All 120 tests and lint pass before that matrix.
