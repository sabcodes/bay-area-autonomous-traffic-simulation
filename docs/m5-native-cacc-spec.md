# M5 native CACC specification (revision 3)

**Historical/rejected policy.** The active final contract is
[supervised CACC revision 4](m5-supervised-cacc-spec.md). Failed evidence is retained.

Written 2026-10-16 before native-policy implementation. This supersedes the
custom-overlay policy in [the original spec](m5-cooperative-cacc-spec.md), whose
rejected results remain evidence. The original plan and spec preceded source
implementation. Do not erase the failed approaches.

## Evidence motivating the revision

Revision 1 teleported an exit vehicle; revision 2 corrected that exact case but
seed 43 subsequently teleported `estimated_sr85_gp_entrance_0710.16` at a merge
on lane `867254755_0` at 2072 s. Native lane-change speed adjustments are made
before TraCI speed overrides; safe-speed mode does not preserve every tactical
lane-change adjustment. Replace the integration seam rather than grow release
heuristics. Preserve the completed revision-2 matrix even though it fails.

## Policy and explicit treatment

Use SUMO 1.27.1's native CACC car-following model for passenger vTypes; trucks
keep frozen Krauss behavior. Keep original type IDs, probabilities, lengths,
minGap, speed factors/deviations, acceleration/deceleration limits, emergency
limits, routes, demand and 0.5 s step. Keep tau=1.5 s and set tauCACCToACC=1.5 s
rather than the native shorter ACC default. Set collisionAvoidanceOverride=0
(no positive margin above native safe-follow speed), collisionMinGapFactor=1
(the same full minGap collision criterion), and applyDriverState=0.
Explicitly record native CACC gains and ACC fallback gains at their pinned
1.27.1 defaults. No fitting or parameter search after comparison outcomes.

Native CACC selects cruise, gap closing, gap, or collision-avoidance behavior;
a non-CACC leader uses ACC. This is an idealized model with native leader/type
knowledge, not an external acceleration-message implementation. No radio
network or packet delay/loss is modeled. Native following and native lane-change
speed adjustment remain in their intended order; issue no TraCI speed,
acceleration, lane-change, or safety-mode commands.

The controller config declares policy=sumo_cacc, backend=libsumo (or traci for
contract checks), a 1 s diagnostic sample period, a 250 m leader-query lookahead,
and explicit vehicle_parameters. Reject missing/unknown keys, nonfinite values,
unsafe collision margins, altered tau fallback, invalid sample periods/ranges,
and unsupported backend/model before simulation. The gains follow pinned
native defaults; their complete dictionary is versioned in the experiment.

Prepare frozen H0 route generation first and retain its SHA-256. For CACC only,
change the passenger carFollowModel and the declared model-specific parameters.
Record original and treated route hashes, native vehicle types, and policy in
the manifest and report. The route XMLs intentionally differ in passenger
following attributes. Require exact equality of flows, route paths, truck types
and all other passenger attributes. Audit realized IDs, type choices, sampled
speed factors and reconstructed scheduled departures across each seed pair.

## Queries, diagnostics and reporting

Run the native model with libsumo 1.27.1, while H0 retains binary subprocess
execution. Use three separate worker processes and the existing isolated
scenario/date/seed outputs. Record actual engine version and require agreement
with the frozen binary version. Scalar vehicle state uses subscriptions.
At 1 s samples, query each passenger's leader with 250 m lookahead and native
caccVehicleMode parameter. There are no all-pairs scans or external commands.
Count actual CC, ACC, CACC_GAP_CL, CACC_GAP and CACC_CA modes separately from
queried passenger/truck leader eligibility; do not equate eligibility with mode.
Record equipped vehicle count, observed passenger samples, acceleration extrema,
queried following gaps and missing-state observations. Close engines and retain
incomplete diagnostics on exceptions. Missing state or absent native CACC mode
evidence fails acceptance. The gains are deterministic; fleet and native lane
changes can remain seed dependent.

Use the existing M4 metrics plus the specified insertion/scheduled metrics and
paired comparisons. Preserve all warning/error/teleport/collision/emergency and
clearance gates. Default command remains:

```bash
PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim run-us101-experiment --config configs/us101_m5_experiment.json
```

Use a new native-policy experiment ID. Keep the rejected matrices separate.
Report every tradeoff; clean simulation is not safety or field-fidelity proof.

## Final acceptance criteria

| ID | Evidence required |
| --- | --- |
| AC1 | Original plan/spec and this superseding spec precede their respective implementations. |
| AC2 | Native route transformation preserves all non-treatment XML; invalid/unsafe policy settings rejected; hand-calculated metric/pairing fixtures retained. |
| AC3 | Real native-CACC small-network deterministic replay and matching numeric trips across libsumo/socket; native strategic exit and mixed passenger/truck modes observed without external speed commands. |
| AC4 | Isolated parallel harness, mismatched-treatment rejection, policy/hash provenance, diagnostics/error retention and paired/null tests. |
| AC5 | Fresh six-run H0/native-CACC matrix, all clean and cleared, actual native cooperative and ACC modes present, matched physical/demand inputs and realized fleets. H0 exactly replays M4. |
| AC6 | Independent raw trip/summary/XML audit, aggregate and paired arithmetic, explicit insertion populations and preserved rejected policy evidence. |
| AC7 | Regression tests/lint/whitespace, spec review, synchronized repository/Obsidian context and verified GitHub publication. |

## Primary sources checked 2026-10-16

- Model behavior, defaults and safety override:
  https://sumo.dlr.de/docs/Car-Following-Models/CACC.html
  https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/cfmodels/MSCFModel_CACC.cpp
- Native ACC fallback:
  https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/cfmodels/MSCFModel_ACC.cpp
- TraCI/native lane-change integration:
  https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/MSVehicle.cpp
- XML parameter names:
  https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/utils/xml/SUMOXMLDefinitions.cpp
- Backend and query semantics:
  https://sumo.dlr.de/docs/Libsumo.html
  https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html
