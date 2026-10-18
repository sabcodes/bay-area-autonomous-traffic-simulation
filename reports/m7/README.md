# M7 sensitivity and uncertainty results

Complete campaign: True. Valid runs: 54/54.

Frozen OFAT screen on 2025-10-08. Base seeds 41-45; sensitivities 41-43.
All differences below pair against H0 at matching demand, date and seed.
The original three-seed base summary remains in [M6 results](../m6/README.md); compare it with the five-seed base groups below.
Means +/- sample SD describe simulation seed spread, not confidence intervals.

![Paired sensitivity](paired_sensitivity.png)

| Case/policy | Metric | Mean difference +/- SD | Min..max | % H0 | +/-/zero seeds |
| --- | --- | ---: | ---: | ---: | --- |
| base/CACC | All-exit throughput (veh/h) | -17.5000 +/- 42.9680 | -55.5000..41.0000 | -0.2117 | 2/3/0 |
| base/CACC | Scheduled-cohort total time (s) | 10.9255 +/- 18.0144 | -10.4306..29.4549 | 0.7092 | 3/2/0 |
| base/CACC | RMS acceleration (m/s²) | -0.0063 +/- 0.0034 | -0.0090..-0.0017 | -0.7749 | 0/5/0 |
| base/CACC | Peak insertion backlog (vehicles) | 22.8000 +/- 71.1245 | -87.0000..80.0000 | 0.8102 | 3/2/0 |
| base/CENTRAL | All-exit throughput (veh/h) | 43.2000 +/- 91.4977 | -35.5000..163.0000 | 0.5226 | 3/2/0 |
| base/CENTRAL | Scheduled-cohort total time (s) | -17.6473 +/- 38.2434 | -60.3046..21.4589 | -1.1456 | 2/3/0 |
| base/CENTRAL | RMS acceleration (m/s²) | 0.0040 +/- 0.0062 | -0.0029..0.0113 | 0.4866 | 3/2/0 |
| base/CENTRAL | Peak insertion backlog (vehicles) | -65.6000 +/- 102.5685 | -171.0000..68.0000 | -2.3310 | 1/4/0 |
| demand_080/CACC | All-exit throughput (veh/h) | -9.6667 +/- 19.9646 | -32.5000..4.5000 | -0.1196 | 1/2/0 |
| demand_080/CACC | Scheduled-cohort total time (s) | 8.4240 +/- 4.0423 | 5.5739..13.0503 | 1.5950 | 3/0/0 |
| demand_080/CACC | RMS acceleration (m/s²) | -0.0055 +/- 0.0039 | -0.0082..-0.0010 | -0.5831 | 0/3/0 |
| demand_080/CACC | Peak insertion backlog (vehicles) | -16.0000 +/- 15.0000 | -31.0000..-1.0000 | -5.9333 | 0/3/0 |
| demand_080/CENTRAL | All-exit throughput (veh/h) | 0.0000 +/- 0.0000 | 0.0000..0.0000 | 0.0000 | 0/0/3 |
| demand_080/CENTRAL | Scheduled-cohort total time (s) | 0.0000 +/- 0.0000 | 0.0000..0.0000 | 0.0000 | 0/0/3 |
| demand_080/CENTRAL | RMS acceleration (m/s²) | 0.0000 +/- 0.0000 | 0.0000..0.0000 | 0.0000 | 0/0/3 |
| demand_080/CENTRAL | Peak insertion backlog (vehicles) | 0.0000 +/- 0.0000 | 0.0000..0.0000 | 0.0000 | 0/0/3 |
| demand_120/CACC | All-exit throughput (veh/h) | -32.6667 +/- 71.7327 | -107.5000..35.5000 | -0.3853 | 1/2/0 |
| demand_120/CACC | Scheduled-cohort total time (s) | 7.1093 +/- 55.5950 | -28.1044..71.2005 | 0.2698 | 1/2/0 |
| demand_120/CACC | RMS acceleration (m/s²) | -0.0061 +/- 0.0065 | -0.0132..-0.0004 | -0.7409 | 0/3/0 |
| demand_120/CACC | Peak insertion backlog (vehicles) | 31.6667 +/- 117.3641 | -56.0000..165.0000 | 0.4458 | 1/2/0 |
| demand_120/CENTRAL | All-exit throughput (veh/h) | -7.8333 +/- 38.7857 | -35.5000..36.5000 | -0.0924 | 1/2/0 |
| demand_120/CENTRAL | Scheduled-cohort total time (s) | 2.4542 +/- 18.7237 | -15.2768..22.0336 | 0.0932 | 2/1/0 |
| demand_120/CENTRAL | RMS acceleration (m/s²) | -0.0001 +/- 0.0033 | -0.0034..0.0031 | -0.0154 | 1/2/0 |
| demand_120/CENTRAL | Peak insertion backlog (vehicles) | -23.0000 +/- 61.2209 | -81.0000..41.0000 | -0.3238 | 1/2/0 |
| penetration_000/CACC | All-exit throughput (veh/h) | 0.0000 +/- 0.0000 | 0.0000..0.0000 | 0.0000 | 0/0/3 |
| penetration_000/CACC | Scheduled-cohort total time (s) | 0.0000 +/- 0.0000 | 0.0000..0.0000 | 0.0000 | 0/0/3 |
| penetration_000/CACC | RMS acceleration (m/s²) | 0.0000 +/- 0.0000 | 0.0000..0.0000 | 0.0000 | 0/0/3 |
| penetration_000/CACC | Peak insertion backlog (vehicles) | 0.0000 +/- 0.0000 | 0.0000..0.0000 | 0.0000 | 0/0/3 |
| penetration_050/CACC | All-exit throughput (veh/h) | -40.8333 +/- 111.9568 | -146.5000..76.5000 | -0.4935 | 1/2/0 |
| penetration_050/CACC | Scheduled-cohort total time (s) | 28.0797 +/- 48.7496 | -26.8695..66.1357 | 1.8306 | 2/1/0 |
| penetration_050/CACC | RMS acceleration (m/s²) | -0.0072 +/- 0.0094 | -0.0169..0.0018 | -0.8782 | 1/2/0 |
| penetration_050/CACC | Peak insertion backlog (vehicles) | 86.6667 +/- 125.7869 | -57.0000..177.0000 | 3.0945 | 2/1/0 |
| range_050/CACC | All-exit throughput (veh/h) | 0.1667 +/- 65.9779 | -75.0000..48.5000 | 0.0020 | 2/1/0 |
| range_050/CACC | Scheduled-cohort total time (s) | 0.4472 +/- 33.2157 | -24.3308..38.1901 | 0.0292 | 1/2/0 |
| range_050/CACC | RMS acceleration (m/s²) | -0.0037 +/- 0.0070 | -0.0117..0.0006 | -0.4524 | 2/1/0 |
| range_050/CACC | Peak insertion backlog (vehicles) | -22.3333 +/- 120.4007 | -148.0000..92.0000 | -0.7974 | 1/2/0 |
| delay_1000/CACC | All-exit throughput (veh/h) | -4.1667 +/- 59.6329 | -72.0000..40.0000 | -0.0504 | 2/1/0 |
| delay_1000/CACC | Scheduled-cohort total time (s) | 18.6097 +/- 29.9902 | -6.9699..51.6153 | 1.2132 | 2/1/0 |
| delay_1000/CACC | RMS acceleration (m/s²) | -0.0043 +/- 0.0022 | -0.0067..-0.0022 | -0.5268 | 0/3/0 |
| delay_1000/CACC | Peak insertion backlog (vehicles) | 19.0000 +/- 90.8350 | -56.0000..120.0000 | 0.6784 | 1/2/0 |
| loss_020/CACC | All-exit throughput (veh/h) | -31.3333 +/- 87.0235 | -103.0000..65.5000 | -0.3787 | 1/2/0 |
| loss_020/CACC | Scheduled-cohort total time (s) | 21.7951 +/- 41.0123 | -24.6657..52.9664 | 1.4209 | 2/1/0 |
| loss_020/CACC | RMS acceleration (m/s²) | -0.0104 +/- 0.0064 | -0.0155..-0.0033 | -1.2739 | 0/3/0 |
| loss_020/CACC | Peak insertion backlog (vehicles) | 77.0000 +/- 133.0000 | -76.0000..165.0000 | 2.7493 | 2/1/0 |
| headway_2000/CACC | All-exit throughput (veh/h) | 30.5000 +/- 23.4467 | 5.5000..52.0000 | 0.3686 | 3/0/0 |
| headway_2000/CACC | Scheduled-cohort total time (s) | -9.5069 +/- 16.2138 | -25.9896..6.4239 | -0.6198 | 1/2/0 |
| headway_2000/CACC | RMS acceleration (m/s²) | -0.0003 +/- 0.0021 | -0.0027..0.0013 | -0.0422 | 2/1/0 |
| headway_2000/CACC | Peak insertion backlog (vehicles) | -3.3333 +/- 15.5027 | -21.0000..8.0000 | -0.1190 | 2/1/0 |
| vsl_220/CENTRAL | All-exit throughput (veh/h) | 20.8333 +/- 73.6212 | -36.0000..104.0000 | 0.2518 | 1/2/0 |
| vsl_220/CENTRAL | Scheduled-cohort total time (s) | -9.0805 +/- 32.7058 | -41.6647..23.7455 | -0.5920 | 1/2/0 |
| vsl_220/CENTRAL | RMS acceleration (m/s²) | 0.0022 +/- 0.0043 | -0.0008..0.0071 | 0.2701 | 2/1/0 |
| vsl_220/CENTRAL | Peak insertion backlog (vehicles) | -67.6667 +/- 105.3107 | -168.0000..42.0000 | -2.4161 | 1/2/0 |

## Run validity and activity

Zero-equipment and nonactivating controls remain valid if healthy and complete.
Active share uses all-run passenger timesteps, including native supervision.

| Case | Policy | Seed | Valid | Equipped/eligible | Active passenger % | Message lost/opportunities | VSL lane-s | Warnings | Reason |
| --- | --- | ---: | --- | --- | ---: | --- | ---: | ---: | --- |
| base | CACC | 41 | True | 22018/22018 | 2.0603 | 0/663625 | null | 0 |  |
| base | CACC | 42 | True | 22030/22030 | 2.0599 | 0/670598 | null | 0 |  |
| base | CACC | 43 | True | 22060/22060 | 1.9939 | 0/644025 | null | 0 |  |
| base | CACC | 44 | True | 22035/22035 | 2.0327 | 0/657105 | null | 0 |  |
| base | CACC | 45 | True | 22032/22032 | 2.0925 | 0/673967 | null | 0 |  |
| base | CENTRAL | 41 | True | n/a | null | n/a | 65940.0000 | 0 |  |
| base | CENTRAL | 42 | True | n/a | null | n/a | 69300.0000 | 0 |  |
| base | CENTRAL | 43 | True | n/a | null | n/a | 68880.0000 | 0 |  |
| base | CENTRAL | 44 | True | n/a | null | n/a | 68040.0000 | 0 |  |
| base | CENTRAL | 45 | True | n/a | null | n/a | 68460.0000 | 0 |  |
| base | H0 | 41 | True | n/a | null | n/a | null | 0 |  |
| base | H0 | 42 | True | n/a | null | n/a | null | 0 |  |
| base | H0 | 43 | True | n/a | null | n/a | null | 0 |  |
| base | H0 | 44 | True | n/a | null | n/a | null | 0 |  |
| base | H0 | 45 | True | n/a | null | n/a | null | 0 |  |
| demand_080 | CACC | 41 | True | 17641/17641 | 2.1492 | 0/272253 | null | 0 |  |
| demand_080 | CACC | 42 | True | 17635/17635 | 2.1350 | 0/275673 | null | 0 |  |
| demand_080 | CACC | 43 | True | 17672/17672 | 2.1933 | 0/277885 | null | 0 |  |
| demand_080 | CENTRAL | 41 | True | n/a | null | n/a | 0.0000 | 0 |  |
| demand_080 | CENTRAL | 42 | True | n/a | null | n/a | 0.0000 | 0 |  |
| demand_080 | CENTRAL | 43 | True | n/a | null | n/a | 0.0000 | 0 |  |
| demand_080 | H0 | 41 | True | n/a | null | n/a | null | 0 |  |
| demand_080 | H0 | 42 | True | n/a | null | n/a | null | 0 |  |
| demand_080 | H0 | 43 | True | n/a | null | n/a | null | 0 |  |
| demand_120 | CACC | 41 | True | 26415/26415 | 2.1239 | 0/837461 | null | 0 |  |
| demand_120 | CACC | 42 | True | 26424/26424 | 2.1095 | 0/854927 | null | 0 |  |
| demand_120 | CACC | 43 | True | 26461/26461 | 2.1391 | 0/823454 | null | 0 |  |
| demand_120 | CENTRAL | 41 | True | n/a | null | n/a | 63420.0000 | 0 |  |
| demand_120 | CENTRAL | 42 | True | n/a | null | n/a | 63000.0000 | 0 |  |
| demand_120 | CENTRAL | 43 | True | n/a | null | n/a | 64260.0000 | 0 |  |
| demand_120 | H0 | 41 | True | n/a | null | n/a | null | 0 |  |
| demand_120 | H0 | 42 | True | n/a | null | n/a | null | 0 |  |
| demand_120 | H0 | 43 | True | n/a | null | n/a | null | 0 |  |
| penetration_000 | CACC | 41 | True | 0/22018 | 0.0000 | 0/0 | null | 0 |  |
| penetration_000 | CACC | 42 | True | 0/22030 | 0.0000 | 0/0 | null | 0 |  |
| penetration_000 | CACC | 43 | True | 0/22060 | 0.0000 | 0/0 | null | 0 |  |
| penetration_050 | CACC | 41 | True | 10986/22018 | 1.0267 | 0/177269 | null | 0 |  |
| penetration_050 | CACC | 42 | True | 11033/22030 | 1.0359 | 0/171311 | null | 0 |  |
| penetration_050 | CACC | 43 | True | 11062/22060 | 1.0686 | 0/179621 | null | 0 |  |
| range_050 | CACC | 41 | True | 22018/22018 | 2.0303 | 0/561746 | null | 0 |  |
| range_050 | CACC | 42 | True | 22030/22030 | 2.0620 | 0/564046 | null | 0 |  |
| range_050 | CACC | 43 | True | 22060/22060 | 2.0388 | 0/553526 | null | 0 |  |
| delay_1000 | CACC | 41 | True | 22018/22018 | 2.0971 | 0/660572 | null | 0 |  |
| delay_1000 | CACC | 42 | True | 22030/22030 | 2.0723 | 0/677164 | null | 0 |  |
| delay_1000 | CACC | 43 | True | 22060/22060 | 2.0934 | 0/663392 | null | 0 |  |
| loss_020 | CACC | 41 | True | 22018/22018 | 2.0382 | 130842/655469 | null | 0 |  |
| loss_020 | CACC | 42 | True | 22030/22030 | 2.0427 | 132855/667806 | null | 0 |  |
| loss_020 | CACC | 43 | True | 22060/22060 | 2.0989 | 133014/664476 | null | 0 |  |
| headway_2000 | CACC | 41 | True | 22018/22018 | 2.1190 | 0/662353 | null | 0 |  |
| headway_2000 | CACC | 42 | True | 22030/22030 | 2.1106 | 0/673545 | null | 0 |  |
| headway_2000 | CACC | 43 | True | 22060/22060 | 2.0444 | 0/657860 | null | 0 |  |
| vsl_220 | CENTRAL | 41 | True | n/a | null | n/a | 67200.0000 | 0 |  |
| vsl_220 | CENTRAL | 42 | True | n/a | null | n/a | 70560.0000 | 0 |  |
| vsl_220 | CENTRAL | 43 | True | n/a | null | n/a | 70140.0000 | 0 |  |

## Factor minus base policy (same seeds)

These isolate each non-demand factor against the base CACC or CENTRAL treatment on seeds 41-43.
Demand cases change the operating condition and are interpreted against their own H0.

| Case/policy | Metric | Factor minus base mean +/- SD |
| --- | --- | ---: |
| penetration_000/CACC | All-exit throughput | 24.5000 +/- 34.7095 |
| penetration_000/CACC | Scheduled-cohort total time | -10.4649 +/- 20.0109 |
| penetration_000/CACC | RMS acceleration | 0.0065 +/- 0.0041 |
| penetration_000/CACC | Peak insertion backlog | -15.0000 +/- 88.4251 |
| penetration_050/CACC | All-exit throughput | -16.3333 +/- 91.0526 |
| penetration_050/CACC | Scheduled-cohort total time | 17.6148 +/- 35.1490 |
| penetration_050/CACC | RMS acceleration | -0.0007 +/- 0.0065 |
| penetration_050/CACC | Peak insertion backlog | 71.6667 +/- 42.5245 |
| range_050/CACC | All-exit throughput | 24.6667 +/- 63.9420 |
| range_050/CACC | Scheduled-cohort total time | -10.0177 +/- 34.0624 |
| range_050/CACC | RMS acceleration | 0.0028 +/- 0.0060 |
| range_050/CACC | Peak insertion backlog | -37.3333 +/- 59.1636 |
| delay_1000/CACC | All-exit throughput | 20.3333 +/- 33.9939 |
| delay_1000/CACC | Scheduled-cohort total time | 8.1448 +/- 23.8044 |
| delay_1000/CACC | RMS acceleration | 0.0022 +/- 0.0027 |
| delay_1000/CACC | Peak insertion backlog | 4.0000 +/- 106.7146 |
| loss_020/CACC | All-exit throughput | -6.8333 +/- 62.4547 |
| loss_020/CACC | Scheduled-cohort total time | 11.3302 +/- 27.6021 |
| loss_020/CACC | RMS acceleration | -0.0039 +/- 0.0025 |
| loss_020/CACC | Peak insertion backlog | 62.0000 +/- 44.7996 |
| headway_2000/CACC | All-exit throughput | 55.0000 +/- 31.4325 |
| headway_2000/CACC | Scheduled-cohort total time | -19.9718 +/- 31.8925 |
| headway_2000/CACC | RMS acceleration | 0.0061 +/- 0.0062 |
| headway_2000/CACC | Peak insertion backlog | -18.3333 +/- 94.4052 |
| vsl_220/CENTRAL | All-exit throughput | -8.6667 +/- 5.2520 |
| vsl_220/CENTRAL | Scheduled-cohort total time | 5.9980 +/- 4.8727 |
| vsl_220/CENTRAL | RMS acceleration | -0.0016 +/- 0.0012 |
| vsl_220/CENTRAL | Peak insertion backlog | -22.0000 +/- 19.3132 |

## Audit and limitations

Independent audit: 1620 raw metrics; 480 group/paired metric records; 12 exact M6/null-control replays.

M3 failed held-out fidelity remains (combined speed MAE 14.90 mph). M5 remains low-engagement supervised control. This single-date OFAT screen cannot estimate interactions or total uncertainty. Communication degradation affects acceleration feedforward; current local sensing remains. The range case also changes sensed-leader following. VSL sensing/actuation remain ideal.

All-exit throughput is not mainline capacity; stopped counts are queue proxies; temporal speed variability is not wave stability; acceleration is not energy. No field safety or deployment inference follows.

See the closeout and specification in docs/ for acceptance traceability, commands and interpretation.
