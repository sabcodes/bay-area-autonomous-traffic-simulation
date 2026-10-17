# M5 supervised cooperative-following results

**Complete for the supervised comparison, 2026-10-16.** Continuous CACC remains unresolved.

- [Closeout and interpretation](../../docs/m5-cooperative-cacc-report.md)
- [Active specification](../../docs/m5-supervised-cacc-spec.md)
- [Accepted report](report.json), [full metric summary](summary.md), [independent audit](independent_audit.json)
- [Exact H0/M4 replay](h0_m4_replay.json)
- [Paired figure](paired_changes.png)
- [Rejected persistent overlay](rejected_socket_report.json), [rejected full revision 2](rejected_revision2_report.json), [rejection audit](rejected_revision2_audit.json)
- [Rejected native CACC preflight](rejected_native_preflight.json)
- [Clean supervised probes: seed 41](supervised_preflight_seed41.json), [42](supervised_preflight_seed42.json), [43](supervised_preflight_seed43.json)

6/6 runs cleared 22,951 vehicles each without SUMO warnings. All 102 tests and
lint passed; the raw-data audit checked 30 paired metrics and exact exported
fleet/schedule matching. H0 exactly reproduces M4. Code revision: 643d0da;
individual source hashes are in report.json. Large trajectories remain in
ignored local outputs. Frozen M3 profiles/network are local prerequisites.

Reproduce with the command in the closeout and a new experiment ID. The
in-process SUMO 1.27.1 dependency is project-local. The figure script refuses
performance plots for rejected runs. Small-case cross-backend numeric replay
is exact; it is not an exhaustive backend-equivalence proof.

Means ± sample SD across three seeds; differences are paired CACC minus H0.

| Metric | Unit | H0 | Supervised CACC | Paired difference ± SD | Change |
| --- | --- | ---: | ---: | ---: | ---: |
| Network exit throughput | veh/h | 8274.5000 ± 29.4449 | 8250.0000 ± 12.6194 | -24.5000 ± 34.7095 | -0.30% |
| Actual-departure mean travel time | s | 917.5052 ± 8.8885 | 929.9481 ± 2.5037 | +12.4428 ± 10.2283 | +1.36% |
| Actual-departure p95 travel time | s | 2472.7750 ± 39.0675 | 2514.7917 ± 26.8196 | +42.0167 ± 44.2679 | +1.70% |
| Scheduled-cohort total time | s | 1533.9020 ± 6.4881 | 1544.3669 ± 13.5833 | +10.4649 ± 20.0109 | +0.68% |
| Mean stopped vehicles | vehicles | 88.9196 ± 1.2976 | 86.3635 ± 4.9671 | -2.5561 ± 6.0783 | -2.87% |
| Mean entrance-approach stopped vehicles | vehicles | 10.1361 ± 0.1717 | 7.2126 ± 0.6561 | -2.9235 ± 0.5514 | -28.84% |
| Temporal variability of domain mean speed | mph | 6.0551 ± 0.2184 | 5.8711 ± 0.2454 | -0.1840 ± 0.1222 | -3.04% |
| Mean squared acceleration | m²/s⁴ | 0.6636 ± 0.0015 | 0.6531 ± 0.0056 | -0.0105 ± 0.0067 | -1.59% |
| RMS acceleration | m/s² | 0.8146 ± 0.0009 | 0.8081 ± 0.0035 | -0.0065 ± 0.0041 | -0.80% |
| Whole-run mean insertion delay | s | 589.1094 ± 6.1647 | 587.2371 ± 10.8081 | -1.8724 ± 12.2917 | -0.32% |
| Peak insertion backlog | vehicles | 2800.6667 ± 45.7420 | 2815.6667 ± 65.0641 | +15.0000 ± 88.4251 | +0.54% |

| Seed | Equipped passengers | Active CACC requests | Native samples | Active share |
| --- | ---: | ---: | ---: | ---: |
| 41 | 22,018 | 759,189 | 36,088,596 | 2.0603% |
| 42 | 22,030 | 765,666 | 36,405,102 | 2.0599% |
| 43 | 22,060 | 737,775 | 36,263,805 | 1.9939% |

The mixed changes do not demonstrate an overall traffic benefit. Throughput fell
0.30%; scheduled-cohort total time increased 0.68%; RMS acceleration fell 0.80%.
The entrance-approach stopped proxy fell 28.84% (10.14→7.21 vehicles), while
peak insertion backlog rose 0.54%. The entrance proxy excludes vehicles waiting
to insert, so its reduction is not a reduction in all ramp-related delay.
The paired SD exceeds the mean change for throughput and scheduled total time.
No inferential significance test or field validation is claimed from three seeds. Active requests
cover only about 2% of all-run passenger timesteps; the rest use native behavior.
These results qualify this supervised comparison, not continuous CACC.

![Paired seed changes](paired_changes.png)

M3's combined held-out speed MAE remains 14.90 mph. This single-day, three-seed
comparison is not field validation, a string-stability proof or an energy study.
