# M3 human baseline: closeout and interpretation

**Status:** M3 experiment complete; held-out fidelity target missed.

**Closed:** 2026-10-12. The baseline remains provisional for traffic fidelity.

The [staged plan](m3-human-baseline-plan.md) defines M3.1–M3.6 and its completion
rule. The [results package](../reports/m3/README.md) contains station tables,
five-minute profiles, congestion figures, seed variation, and run health.

## Selected model

The accepted M2 network is unchanged. The selected `buffer_exit_tau15` case
uses an existing 1,007.33 m upstream motorway buffer, station 400790 as an
80%-coverage inlet proxy, the four audited measured ramp movements, two
net-entry groups (700 and 2,000 veh/h), and a downstream net-exit group
(1,500 veh/h). These groups represent unresolved aggregate movements; their
chosen edges do not turn them into measured ramp counts. See the
[demand ledger](m3-demand-ledger.md) for every northbound branch disposition.

Human vehicles use Krauss following, 1.5 s headway, sigma 0.5, desired-speed
factor 1.0 with deviation 0.1, and default lane changing. A generic truck type
represents 4% of generated traffic, using an annual local count proxy.
Two fleet shares, two demand scales, and the alternative 402377 lane subset
are reported as sensitivity cases. Failed trials remain visible.

## Calibration and validation design

The five calibration weekdays are October 7–10 and 14, 2025. October 8 was
selected by median upstream flow before simulation fitting. The bounded search
has 12 candidates. Final calibration uses three seeds (41–43) on all five days.
October 15 and 16 are reserved for separate-day validation with the same seeds.
No validation error changes the selected settings or removes a poor-fit day.

The six full-cross-section targets retain at least 90% reported coverage.
Station 402377 uses four of five SUMO lanes and is reported separately;
401948's five observed channels against four modeled lanes are excluded from
aggregate scoring. Station 400790 supplies demand and is not a scored target.
Observed speed is an outcome target, never a vehicle speed command.

Performance targets are mean five-minute flow MAPE ≤20% and speed MAE ≤10 mph
across the six full-cross-section stations. The results report evaluates each
held-out day. Run health requires no SUMO warnings and all loaded vehicles
inserted and ended, with zero remaining queues, collisions, or teleports.
The treatment hash must match between calibration and validation.

Final calibration completed 15/15 runs cleanly, with mean flow MAPE **8.32%**
and speed MAE **8.15 mph**. The freeze record was written before validation.
The high-demand sensitivity left 1,357 vehicles waiting to insert and 100
still running after clearance; it produced no SUMO warnings, but fails the
cleared-demand requirement. A good speed fit there does not make it an
acceptable baseline. The working 402377 subset (1–4) gave 8.61% flow MAPE
and 3.01 mph speed MAE on October 8, seed 42, versus 23.05% and 4.07 mph
for the alternative (0–3). No validation result selected this mapping.

## Held-out result and acceptance decision

All six held-out runs were clean and cleared, using the exact frozen treatment
hash `bd41772cb9e78b03f91bf239b039eb84fd96e1d6ebe840b4b883768d8203c7aa`.
The mean errors across the six full-cross-section stations were:

| Validation day | Flow MAPE | Speed MAE | Fidelity targets |
| --- | ---: | ---: | --- |
| 2025-10-15 | 29.95% | 21.50 mph | Both missed |
| 2025-10-16 | 8.79% | 8.30 mph | Both met |
| Both days, equal weight | 19.37% | 14.90 mph | Flow met; speed missed |

October 15 exposes a major upstream congestion mismatch. At station 402370,
observed mean speed was about 27.5 mph versus 54.1 mph modeled; at 402372 it
was about 15.2 versus 42.7 mph. The model did not reproduce that day's severe
upstream bottleneck. This is not explained away by good Shoreline speed fit
or clean simulation health. An incident or another missing constraint is
possible, but no evidence here identifies the cause.

**Decision:** close M3 at the documented practical experiment standard: demand
assumptions, fleet, bounded calibration, frozen separate-day evaluation,
sensitivities, and reproducible evidence are complete. Do not label H0 as
successfully field-validated. Retain both validation days and the failed
sensitivity. Later policy comparisons must carry this fidelity limit; these
held-out errors must not become a new tuning target disguised as validation.
No further M3 parameter search or M4 implementation is started here.

## Limits to carry forward

- **Conditional demand validation:** each held-out day's measured inlet and
  four reporting-ramp flows are inputs. This checks traffic propagation under
  observed demand; it does not predict future demand.
- **Unknown gross movements:** net-entry/exit groups and omitted ramps can
  change individual trips, queues, and control effects even when station
  totals fit. The 50%/150% cases are scenario bounds, not confidence intervals.
- **Inlet quality and warmup:** the inlet proxy contains estimated/imputed
  contribution and may include omitted exits upstream of the analysis start.
  Warmup lasts 15 minutes and repeats the first analysis flow; it does not
  reconstruct the preceding hour's traffic state. Clearance lasts two hours.
- **Lane assignment:** SUMO numbers from right to left starting at zero.
  Station 402377's working subset is 1–4; 0–3 is the alternative. Statistical
  fit cannot prove PeMS field wiring. Moffett's missing fifth modeled lane
  also limits station-level inference there.
- **Fleet and managed lanes:** annual both-direction truck shares are not
  study-day directional classification. Truck dynamics and passenger
  eligibility/toll behavior are simplified. The truck-share sensitivity
  brackets a proxy, rather than establishing its true value.
- **Existing ramp controls:** exact October 2025 meter settings are unknown.
  The baseline represents delivered ramp flow, not upstream meter queues or
  a reconstructed controller. Later metering claims need that baseline defined.
- **Congestion precision:** five-minute observations and three driving seeds
  do not quantify all structural uncertainty. The onset threshold of 45 mph
  is descriptive. Station plots and timing rows should accompany mean errors.
- **Scope and time:** two held-out weekdays cannot establish general seasonal
  performance. The saved network snapshot is newer than the October 2025
  observations. This is a local simulation baseline, not field certification.

## Reproduction and stopping point

Use the source tree with `PYTHONPATH=src`; an older installed package copy may
omit the new settings. The frozen scenario, experiment settings, source hashes,
commands, and derived five-minute series are versioned. PeMS downloads and
large SUMO runtime files remain local under ignored directories.

M3 ends with the frozen model, calibration/validation/sensitivity reports,
and updated repository and Obsidian context. **Stop here after closeout.
M4 and autonomous-policy experiments require a new user instruction.**
