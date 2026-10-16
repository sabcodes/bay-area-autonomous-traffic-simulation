# M4 experiment harness plan

Status: complete. Written before specification and implementation on 2026-10-16.
The [closeout](m4-experiment-harness-report.md) records acceptance evidence.

## Objective

Finish roadmap milestone M4: one command runs an explicit human-baseline
experiment over repeated seeds and produces comparable throughput, travel-time,
queue, speed-variability, and acceleration-smoothness results with provenance
and run-health checks.

## Existing evidence and constraints

- M3 selected and froze the human baseline. Its October 15 held-out bottleneck
  failure remains a limitation of later results.
- The existing real-corridor runner already generates routes, trip records,
  virtual detectors, provenance, and a health file. Reuse it.
- The existing seed-summary utility supplies sample means and standard deviations.
- Use the frozen October 8, 2025 representative calibration day and seeds 41–43
  for M4 acceptance. These runs exercise instrumentation; they do not recalibrate
  or revalidate H0.
- Preserve M2 geometry and all M3 frozen inputs and reports. Write runtime files
  in an isolated M4 directory.

## Sequence

1. Write `docs/m4-experiment-harness-spec.md` with metric formulas, measurement
   populations, reproducibility rules, failure behavior, and acceptance checks.
2. Implement optional trajectory output in the existing SUMO runner and streaming
   metric extraction. Use SUMO's native compressed FCD output and the standard
   library rather than a second simulation loop or a new dependency.
3. Add an explicit M4 experiment configuration and one CLI command. Isolate each
   scenario/date/seed, retain individual results, and summarize seeds within each
   scenario/date. Record configuration, source, engine, input, and route hashes.
4. Check the metric formulas on small hand-calculated data and the orchestration
   on controlled runs. Run relevant existing tests and lint.
5. Run the actual three-seed experiment, compare its traffic outcomes with M3's
   corresponding runs, and retain a compact versioned report and closeout.
6. Update README, roadmap, and project memory with the implemented command,
   measured results, acceptance evidence, and remaining limitations.

## Completion rule

All acceptance criteria in the specification have evidence. Runtime or metric
failures remain in the report and fail the command. Mark M4 complete only after
successful real three-seed execution; distinguish implementation status from
traffic fidelity. M5–M8 require subsequent work.
