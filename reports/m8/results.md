# Final research result tables

Generated from saved per-run evidence. Differences are policy minus matching-demand, matching-seed H0. SD is sample seed spread, not a confidence interval.

## M3 fidelity

| Phase / date | Runs | Flow MAPE (%) | Speed MAE (mph) |
| --- | ---: | ---: | ---: |
| calibration / 2025-10-07 | 3 | 10.21 | 7.25 |
| calibration / 2025-10-08 | 3 | 8.22 | 5.85 |
| calibration / 2025-10-09 | 3 | 7.78 | 6.79 |
| calibration / 2025-10-10 | 3 | 7.18 | 13.43 |
| calibration / 2025-10-14 | 3 | 8.22 | 7.45 |
| calibration / combined | 15 | 8.32 | 8.15 |
| validation / 2025-10-15 | 3 | 29.95 | 21.50 |
| validation / 2025-10-16 | 3 | 8.79 | 8.30 |
| validation / combined | 6 | 19.37 | 14.90 |

## M7 paired effects

All 13 comparisons and four headline metrics. Percent = 100 * mean paired difference / mean of the exact H0 seed subset.

| Case / policy | Metric | n | Difference +/- SD | Range | % of H0 | + / - / 0 |
| --- | --- | ---: | ---: | --- | ---: | --- |
| base / CACC | Throughput (veh/h) | 5 | -17.5000 +/- 42.9680 | -55.5000..41.0000 | -0.2117 | 2/3/0 |
| base / CACC | Scheduled total time (s) | 5 | 10.9255 +/- 18.0144 | -10.4306..29.4549 | +0.7092 | 3/2/0 |
| base / CACC | RMS acceleration (m/s^2) | 5 | -0.0063 +/- 0.0034 | -0.0090..-0.0017 | -0.7749 | 0/5/0 |
| base / CACC | Peak insertion backlog (vehicles) | 5 | 22.8000 +/- 71.1245 | -87.0000..80.0000 | +0.8102 | 3/2/0 |
| base / CENTRAL | Throughput (veh/h) | 5 | 43.2000 +/- 91.4977 | -35.5000..163.0000 | +0.5226 | 3/2/0 |
| base / CENTRAL | Scheduled total time (s) | 5 | -17.6473 +/- 38.2434 | -60.3046..21.4589 | -1.1456 | 2/3/0 |
| base / CENTRAL | RMS acceleration (m/s^2) | 5 | 0.0040 +/- 0.0062 | -0.0029..0.0113 | +0.4866 | 3/2/0 |
| base / CENTRAL | Peak insertion backlog (vehicles) | 5 | -65.6000 +/- 102.5685 | -171.0000..68.0000 | -2.3310 | 1/4/0 |
| demand_080 / CACC | Throughput (veh/h) | 3 | -9.6667 +/- 19.9646 | -32.5000..4.5000 | -0.1196 | 1/2/0 |
| demand_080 / CACC | Scheduled total time (s) | 3 | 8.4240 +/- 4.0423 | 5.5739..13.0503 | +1.5950 | 3/0/0 |
| demand_080 / CACC | RMS acceleration (m/s^2) | 3 | -0.0055 +/- 0.0039 | -0.0082..-0.0010 | -0.5831 | 0/3/0 |
| demand_080 / CACC | Peak insertion backlog (vehicles) | 3 | -16.0000 +/- 15.0000 | -31.0000..-1.0000 | -5.9333 | 0/3/0 |
| demand_080 / CENTRAL | Throughput (veh/h) | 3 | 0.0000 +/- 0.0000 | 0.0000..0.0000 | +0.0000 | 0/0/3 |
| demand_080 / CENTRAL | Scheduled total time (s) | 3 | 0.0000 +/- 0.0000 | 0.0000..0.0000 | +0.0000 | 0/0/3 |
| demand_080 / CENTRAL | RMS acceleration (m/s^2) | 3 | 0.0000 +/- 0.0000 | 0.0000..0.0000 | +0.0000 | 0/0/3 |
| demand_080 / CENTRAL | Peak insertion backlog (vehicles) | 3 | 0.0000 +/- 0.0000 | 0.0000..0.0000 | +0.0000 | 0/0/3 |
| demand_120 / CACC | Throughput (veh/h) | 3 | -32.6667 +/- 71.7327 | -107.5000..35.5000 | -0.3853 | 1/2/0 |
| demand_120 / CACC | Scheduled total time (s) | 3 | 7.1093 +/- 55.5950 | -28.1044..71.2005 | +0.2698 | 1/2/0 |
| demand_120 / CACC | RMS acceleration (m/s^2) | 3 | -0.0061 +/- 0.0065 | -0.0132..-0.0004 | -0.7409 | 0/3/0 |
| demand_120 / CACC | Peak insertion backlog (vehicles) | 3 | 31.6667 +/- 117.3641 | -56.0000..165.0000 | +0.4458 | 1/2/0 |
| demand_120 / CENTRAL | Throughput (veh/h) | 3 | -7.8333 +/- 38.7857 | -35.5000..36.5000 | -0.0924 | 1/2/0 |
| demand_120 / CENTRAL | Scheduled total time (s) | 3 | 2.4542 +/- 18.7237 | -15.2768..22.0336 | +0.0932 | 2/1/0 |
| demand_120 / CENTRAL | RMS acceleration (m/s^2) | 3 | -0.0001 +/- 0.0033 | -0.0034..0.0031 | -0.0154 | 1/2/0 |
| demand_120 / CENTRAL | Peak insertion backlog (vehicles) | 3 | -23.0000 +/- 61.2209 | -81.0000..41.0000 | -0.3238 | 1/2/0 |
| penetration_000 / CACC | Throughput (veh/h) | 3 | 0.0000 +/- 0.0000 | 0.0000..0.0000 | +0.0000 | 0/0/3 |
| penetration_000 / CACC | Scheduled total time (s) | 3 | 0.0000 +/- 0.0000 | 0.0000..0.0000 | +0.0000 | 0/0/3 |
| penetration_000 / CACC | RMS acceleration (m/s^2) | 3 | 0.0000 +/- 0.0000 | 0.0000..0.0000 | +0.0000 | 0/0/3 |
| penetration_000 / CACC | Peak insertion backlog (vehicles) | 3 | 0.0000 +/- 0.0000 | 0.0000..0.0000 | +0.0000 | 0/0/3 |
| penetration_050 / CACC | Throughput (veh/h) | 3 | -40.8333 +/- 111.9568 | -146.5000..76.5000 | -0.4935 | 1/2/0 |
| penetration_050 / CACC | Scheduled total time (s) | 3 | 28.0797 +/- 48.7496 | -26.8695..66.1357 | +1.8306 | 2/1/0 |
| penetration_050 / CACC | RMS acceleration (m/s^2) | 3 | -0.0072 +/- 0.0094 | -0.0169..0.0018 | -0.8782 | 1/2/0 |
| penetration_050 / CACC | Peak insertion backlog (vehicles) | 3 | 86.6667 +/- 125.7869 | -57.0000..177.0000 | +3.0945 | 2/1/0 |
| range_050 / CACC | Throughput (veh/h) | 3 | 0.1667 +/- 65.9779 | -75.0000..48.5000 | +0.0020 | 2/1/0 |
| range_050 / CACC | Scheduled total time (s) | 3 | 0.4472 +/- 33.2157 | -24.3308..38.1901 | +0.0292 | 1/2/0 |
| range_050 / CACC | RMS acceleration (m/s^2) | 3 | -0.0037 +/- 0.0070 | -0.0117..0.0006 | -0.4524 | 2/1/0 |
| range_050 / CACC | Peak insertion backlog (vehicles) | 3 | -22.3333 +/- 120.4007 | -148.0000..92.0000 | -0.7974 | 1/2/0 |
| delay_1000 / CACC | Throughput (veh/h) | 3 | -4.1667 +/- 59.6329 | -72.0000..40.0000 | -0.0504 | 2/1/0 |
| delay_1000 / CACC | Scheduled total time (s) | 3 | 18.6097 +/- 29.9902 | -6.9699..51.6153 | +1.2132 | 2/1/0 |
| delay_1000 / CACC | RMS acceleration (m/s^2) | 3 | -0.0043 +/- 0.0022 | -0.0067..-0.0022 | -0.5268 | 0/3/0 |
| delay_1000 / CACC | Peak insertion backlog (vehicles) | 3 | 19.0000 +/- 90.8350 | -56.0000..120.0000 | +0.6784 | 1/2/0 |
| loss_020 / CACC | Throughput (veh/h) | 3 | -31.3333 +/- 87.0235 | -103.0000..65.5000 | -0.3787 | 1/2/0 |
| loss_020 / CACC | Scheduled total time (s) | 3 | 21.7951 +/- 41.0123 | -24.6657..52.9664 | +1.4209 | 2/1/0 |
| loss_020 / CACC | RMS acceleration (m/s^2) | 3 | -0.0104 +/- 0.0064 | -0.0155..-0.0033 | -1.2739 | 0/3/0 |
| loss_020 / CACC | Peak insertion backlog (vehicles) | 3 | 77.0000 +/- 133.0000 | -76.0000..165.0000 | +2.7493 | 2/1/0 |
| headway_2000 / CACC | Throughput (veh/h) | 3 | 30.5000 +/- 23.4467 | 5.5000..52.0000 | +0.3686 | 3/0/0 |
| headway_2000 / CACC | Scheduled total time (s) | 3 | -9.5069 +/- 16.2138 | -25.9896..6.4239 | -0.6198 | 1/2/0 |
| headway_2000 / CACC | RMS acceleration (m/s^2) | 3 | -0.0003 +/- 0.0021 | -0.0027..0.0013 | -0.0422 | 2/1/0 |
| headway_2000 / CACC | Peak insertion backlog (vehicles) | 3 | -3.3333 +/- 15.5027 | -21.0000..8.0000 | -0.1190 | 2/1/0 |
| vsl_220 / CENTRAL | Throughput (veh/h) | 3 | 20.8333 +/- 73.6212 | -36.0000..104.0000 | +0.2518 | 1/2/0 |
| vsl_220 / CENTRAL | Scheduled total time (s) | 3 | -9.0805 +/- 32.7058 | -41.6647..23.7455 | -0.5920 | 1/2/0 |
| vsl_220 / CENTRAL | RMS acceleration (m/s^2) | 3 | 0.0022 +/- 0.0043 | -0.0008..0.0071 | +0.2701 | 2/1/0 |
| vsl_220 / CENTRAL | Peak insertion backlog (vehicles) | 3 | -67.6667 +/- 105.3107 | -168.0000..42.0000 | -2.4161 | 1/2/0 |
