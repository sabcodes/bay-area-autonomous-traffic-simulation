# M4 experiment harness specification

Version: 1. Written 2026-10-16 before implementation.
Implemented and accepted; see the [closeout](m4-experiment-harness-report.md).

## Scope and command

`PYTHONPATH=src .venv/bin/python -m bay_area_traffic_sim run-us101-experiment`
runs `configs/us101_m4_experiment.json`. `--config` selects another explicit
experiment document. The document declares a unique experiment ID, named
scenarios referencing baseline configs, ISO observation dates, at least two
unique integer SUMO seeds, measurement period, stop threshold, and output paths.
M4 ships one H0 scenario and one representative calibration date (2025-10-08).
Future treatments can use the same harness once their scenario support exists.
The current milestone adds measurement and reporting, with no policy changes.

Invalid settings fail before simulation: empty/duplicate identifiers, dates or
seeds; invalid ISO dates; nonfinite or negative thresholds; a sampling period
that is not a positive multiple of the 0.5 s simulation step; and unsafe or
colliding output paths. Scenario IDs use letters, digits, underscores, or dashes.
Outputs must live under `outputs/`; refuse existing experiment directories to
prevent stale results and accidental overwrite. A different experiment ID or
output directory permits a new run.

## Frozen treatment and provenance

The shipped scenario references the frozen M3 baseline and its representative
day. Keep its network, source hashes, driving parameters, truck share, demand,
warmup, clearance, and 0.5 s step unchanged. Honor inherited configs and their
existing frozen-input checks. M4 output flags must not change driving outcomes.

Each run gets its own scenario/date/seed directory containing a resolved config,
route, manifest, trip records, FCD trace, station outputs, and run health.
Record the experiment config and hash, resolved scenario config and hash,
network and input hashes, SUMO version, route hash, seed, measurement settings,
source revision and source-file hashes. Group reports by scenario/date; never
pool different days into seed uncertainty. Repeated runs share dates, seeds,
measurement settings, network, demand, fleet, warmup, and clearance; driving
behavior may differ in a later scenario. Refuse a mismatched comparison.

## Populations and windows

The observation window is `[warmup_seconds, last demand interval end)`;
for the shipped case this is `[900, 8100)` simulation seconds, corresponding
to 07:00–09:00. Simulate the full warmup and clearance for trip completion.

Trajectory metrics cover all simulated vehicles, including ramps, the existing
upstream buffer, and internal junction links, sampled at a declared fixed
period (default 1 s). This is the modeled network domain, not just the US-101
through lanes. Empty timesteps count as zero vehicles for queue metrics and
supply no speed or acceleration observations. Require every expected timestep;
missing/truncated trajectory output fails measurement instead of implying zero.
Stream the XML and release processed timesteps to bound memory.

Travel-time metrics use vehicles that actually depart during the observation
window, followed through clearance. Trips completing during the observation
window also contribute to exit throughput even if they departed during warmup.
Report whole-run legacy trip metrics separately. Incomplete trips are excluded
from completed-trip means and counted explicitly; queued departures remain
visible in run health. A failed or uncleared run cannot qualify as accepted.

## Metric definitions

All values are per run before seed aggregation.

| Metric | Definition |
| --- | --- |
| Exit throughput | Count all route completions with arrival in the observation window, divided by window hours; units veh/h. Includes modeled ramp exits, so this is network exit throughput, not a bottleneck capacity claim. |
| Cohort travel time | Mean and 95th percentile of completed trip durations for vehicles departing in the window; units seconds. Quantile uses linear interpolation at `(n-1)*0.95`. Also report cohort completed and unfinished counts. |
| Cohort delay | Mean SUMO `timeLoss` and `waitingTime` for that same completed cohort; units seconds. |
| Stopped queue proxy | Vehicles with speed strictly below the configured threshold (default 0.1 m/s) at each sampled timestep. Report mean and maximum count, and stopped vehicle-seconds = sum(count * sample period). This is a stopped-vehicle count across the modeled domain, not contiguous queue length in meters. |
| Ramp queue proxy | The same stopped-count mean and peak restricted to entrance-route edges before their first shared mainline edge. Report combined entrances; shared mainline and exit edges are excluded. |
| Speed variability | Population standard deviation in mph of the per-timestep mean vehicle speed, over nonempty samples. Also report mean speed, populated timestep count, and vehicle sample count. It measures temporal variation of domain mean speed; changing demand/spatial composition can affect it. It does not measure wave amplification or disturbance recovery. |
| Smoothness | Mean squared longitudinal acceleration over vehicle samples in m²/s⁴, with RMS acceleration in m/s². Use SUMO's exported acceleration, not a difference of rounded speeds. This is a smoothness proxy, not energy or fuel use. |

No eligible trips or vehicle samples yields JSON null for the corresponding
mean/quantile rather than zero. Empty traffic gives queue mean/peak zero.
One populated speed timestep gives population standard deviation zero.
Every metric has a documented population and units in the report contract.

## Summary and failures

For each scenario/date metric, report count of valid numeric seeds, mean, and
sample standard deviation (`n-1` denominator). Require all planned seeds for
an aggregate mean; a missing/null seed value produces a null aggregate rather
than silently reducing the seed set. At least two seeds are required. Seed
spread describes stochastic simulation variation, not a confidence interval
for observed traffic or all model assumptions.

Keep all run records, warnings, errors, and health evidence. Clean-and-cleared
requires no warning/error/teleport/collision/emergency messages, zero running,
waiting, collisions, teleports, and discarded vehicles at the final step, and
loaded = inserted = ended. Missing health attributes fail closed. Exceptions
produce explicit failed run records; continue remaining jobs, write the final
report, and exit nonzero if any run fails. Aggregates for failed groups are
null. Write a JSON report (schema version 1) and a readable Markdown summary.
The report carries the M3 held-out fidelity limitation and metric caveats.

## Acceptance criteria and evidence

- AC1: plan and this specification exist before implementation; each criterion
  maps to a check or real-run evidence in the closeout.
- AC2: hand-calculated trajectory/trip fixtures verify window boundaries,
  mixed arrivals/departures, incomplete/empty traffic, threshold equality,
  ramp filtering, speed population standard deviation, acceleration squares,
  95th percentile interpolation, and missing timestep rejection.
- AC3: configuration checks reject invalid/duplicate dates and seeds, invalid
  periods/thresholds, unsafe names/outputs, and incompatible comparisons before
  launching SUMO. Seed summaries verify sample spread and null propagation.
- AC4: runner checks verify isolated outputs, deterministic report order,
  provenance, report writing, preservation of failures, and nonzero CLI failure.
- AC5: the default command executes all three real H0 seeds, produces both
  reports and all five metric families, and all runs are clean and cleared.
- AC6: compare each M4 seed's completed count and legacy trip means to its
  corresponding M3 calibration record. Any difference is investigated and
  recorded; instrumentation cannot silently change the frozen traffic model.
- AC7: relevant automated checks and repository lint pass. The closeout records
  commands, exact results, limitations, and any deviations from this spec.

## Primary implementation reference

SUMO native FCD output supports configurable sampling, acceleration, selected
attributes, and gzip output:
[SUMO FCD output documentation](https://sumo.dlr.de/docs/Simulation/Output/FCDOutput.html)
