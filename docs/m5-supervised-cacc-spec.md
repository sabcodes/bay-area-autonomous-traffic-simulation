# M5 supervised CACC specification (revision 4)

Written 2026-10-16 before implementation. This is the active M5 contract.
The [original overlay spec](m5-cooperative-cacc-spec.md) and
[native-model spec](m5-native-cacc-spec.md) are rejected historical approaches.
The user was offered scope choices after the failures; absent a preference,
proceed with the stated recommendation that preserves the frozen baseline.

## Evidence and scope

The persistent overlay failed an exit. Releasing only the changing vehicle
fixed that case but all three revision-2 seeds still had merge teleports
(2, 1, 2). SUMO's lane-change model also requests speed adjustments from
neighboring vehicles. Speed-mode safety checks do not preserve all those
adjustments when an external speed request overrides the native result.
Native CACC at the frozen 0.5 s step produced 40 emergency-braking warnings in
a seed-43 3,000 s preflight and is also rejected. Preserve all evidence.

Use a supervised external cooperative-following law with the original fixed
gains, coupled to native maneuver control for every affected passenger. Do
not change the network, 0.5 s step, fleet, demand or headway. This evaluates
CACC during steady lane following, not continuous CACC through all maneuvers.

## Eligibility and handoff

After each step, collect one scalar subscription snapshot plus direct leader,
best-lane and lane-change-state queries before issuing any commands. Query lane
change states only for existing adjacent lanes. A passenger is eligible only
when the current lane has zero best-lane offset, allows route continuation,
and every applicable native lane-change state contains only NONE or STAY.
Any strategic, cooperative, speed-gain, keep-right, blocking/helping, unknown or
other flag yields native speed authority with setSpeed(-1). An unmatched
internal lane also yields native control. Treat this as planned supervision,
not a missing-state fallback.

Require 2.0 s of quiet state after insertion or any native maneuver request
before re-engaging CACC. This fixed handoff interval avoids switching control
in the middle of the native maneuver response. Record supervised native samples
and reason counts independently from active CACC commands and missing state.
All passengers are equipped and may supply ideal acceleration messages even
while supervised natively. Trucks remain human driven and do not broadcast.

## Unchanged command law

The original parameters remain: h=1.5 s, cruise gain=0.4/s, gap gain=0.2/s²,
relative-speed gain=0.8/s, acceleration feedforward gain=0.5, accel limit=2.6,
decel limit=4.5 m/s², leader query cutoff=250 m TraCI gap. For ego speed v,
allowed speed V, returned gap r, leader speed u and previous-step acceleration b:

- cruise a_c = 0.4*(V-v)
- following a_f = 0.2*(r-1.5*v) + 0.8*(u-v) + 0.5*b for an equipped leader;
  omit feedforward for a truck leader
- request max(0, min(V, v + 0.5*clamp(min(a_c,a_f), -4.5, 2.6)))
- with no leader in range use a_c alone

TraCI gap excludes ego minGap, so r-h*v is the correct spacing error for
bumper target minGap+h*v. Keep speedMode 31 and lane-change mode 1621. Missing
state releases native control, is counted separately and fails acceptance.
The command law is deterministic given state; native behavior remains seeded.

## Configuration, provenance and acceptance

Policy is supervised_cacc, backend libsumo 1.27.1, native_handoff_seconds=2.0;
retain all original explicit gains in the controller config. Reject invalid or
unknown settings, unsafe headway/physical limits and invalid handoff intervals
before simulation. Use three isolated worker processes and a fresh experiment
ID. Route XML and complete physical treatment remain byte-identical to H0/M4.
Record actual engine version, per-mode commands, native supervision counts,
quiet-period/maneuver reasons, equipped count, missing states, acceleration
extrema and queried gaps. Report active-command share of passenger samples,
so equipment share is not mistaken for continuous controller operation.

Final AC1–AC7 retain the original plan/spec timing, hand-calculated law/metrics,
configuration and failure checks, small real SUMO deterministic backend replay,
real strategic exit/merge supervision, fresh clean six-run matched matrix,
exact H0 replay, independent raw-output/fleet/pairing audit, full regressions,
and synchronized context/Obsidian/GitHub. All planned safety/clearance gates stay
in force. Preserve failures and avoid gain tuning after outcomes.

The unchanged M4 measurement contract and insertion/scheduled-departure additions
remain. Interpret any outcome only for this supervised policy, one calibration
date and three seeds. M3's held-out fidelity failure remains unchanged.

Primary integration evidence (checked 2026-10-16):
https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/MSVehicle.cpp
https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_27_1/src/microsim/lcmodels/MSLCM_LC2013.cpp
https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html
https://sumo.dlr.de/docs/TraCI/Change_Vehicle_State.html
