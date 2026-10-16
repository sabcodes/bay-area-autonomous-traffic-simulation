# m4_h0_2025_10_08

Accepted: True. Seeds: [41, 42, 43].

Means and sample standard deviations are across seeds within each scenario/date.

| Scenario | Date | Metric | Mean | Sample SD | Valid seeds |
| --- | --- | --- | ---: | ---: | ---: |
| H0 | 2025-10-08 | window_exit_vehicles | 16549.0 | 58.889727 | 3 |
| H0 | 2025-10-08 | network_exit_throughput_vehicles_per_hour | 8274.5 | 29.444864 | 3 |
| H0 | 2025-10-08 | cohort_completed_vehicles | 17707.666667 | 49.90324 | 3 |
| H0 | 2025-10-08 | cohort_unfinished_vehicles | 0.0 | 0.0 | 3 |
| H0 | 2025-10-08 | cohort_mean_travel_time_seconds | 917.505247 | 8.888538 | 3 |
| H0 | 2025-10-08 | cohort_p95_travel_time_seconds | 2472.775 | 39.067498 | 3 |
| H0 | 2025-10-08 | cohort_mean_waiting_time_seconds | 41.346098 | 1.288684 | 3 |
| H0 | 2025-10-08 | cohort_mean_time_loss_seconds | 569.650513 | 8.756656 | 3 |
| H0 | 2025-10-08 | trajectory_timesteps | 7200.0 | 0.0 | 3 |
| H0 | 2025-10-08 | populated_timesteps | 7200.0 | 0.0 | 3 |
| H0 | 2025-10-08 | vehicle_samples | 14754138.333333 | 67099.853177 | 3 |
| H0 | 2025-10-08 | mean_stopped_vehicles | 88.91963 | 1.297591 | 3 |
| H0 | 2025-10-08 | peak_stopped_vehicles | 211.0 | 29.206164 | 3 |
| H0 | 2025-10-08 | stopped_vehicle_seconds | 640221.333333 | 9342.652639 | 3 |
| H0 | 2025-10-08 | mean_ramp_stopped_vehicles | 10.136111 | 0.171672 | 3 |
| H0 | 2025-10-08 | peak_ramp_stopped_vehicles | 41.666667 | 2.081666 | 3 |
| H0 | 2025-10-08 | mean_timestep_speed_mph | 25.990126 | 0.107854 | 3 |
| H0 | 2025-10-08 | temporal_mean_speed_stddev_mph | 6.055111 | 0.218369 | 3 |
| H0 | 2025-10-08 | mean_squared_acceleration_m2_per_s4 | 0.663636 | 0.001499 | 3 |
| H0 | 2025-10-08 | rms_acceleration_m_per_s2 | 0.814638 | 0.00092 | 3 |

## Runs

- H0 2025-10-08 seed 41: accepted=True; measured.
- H0 2025-10-08 seed 42: accepted=True; measured.
- H0 2025-10-08 seed 43: accepted=True; measured.

## Metric contract

- `window_exit_vehicles` (vehicles): arrivals in window, all modeled exits.
- `network_exit_throughput_vehicles_per_hour` (veh/h): window arrivals / window hours.
- `cohort_completed_vehicles` (vehicles): window departures completed by run end.
- `cohort_unfinished_vehicles` (vehicles): window departures unfinished at run end.
- `cohort_mean_travel_time_seconds` (s): completed departure cohort, arithmetic mean.
- `cohort_p95_travel_time_seconds` (s): completed departure cohort, linear p95.
- `cohort_mean_waiting_time_seconds` (s): completed departure cohort, mean waitingTime.
- `cohort_mean_time_loss_seconds` (s): completed departure cohort, mean SUMO timeLoss.
- `trajectory_timesteps` (samples): all expected window timesteps including empty.
- `populated_timesteps` (samples): window timesteps with vehicles.
- `vehicle_samples` (samples): all vehicle observations in window.
- `mean_stopped_vehicles` (vehicles): time mean, speed < stop threshold.
- `peak_stopped_vehicles` (vehicles): time maximum, speed < stop threshold.
- `stopped_vehicle_seconds` (vehicle s): sum stopped counts times sample period.
- `mean_ramp_stopped_vehicles` (vehicles): time mean on entrance approach edges.
- `peak_ramp_stopped_vehicles` (vehicles): time maximum on entrance approach edges.
- `mean_timestep_speed_mph` (mph): mean of nonempty timestep mean speeds.
- `temporal_mean_speed_stddev_mph` (mph): population stddev of timestep mean speeds.
- `mean_squared_acceleration_m2_per_s4` (m^2/s^4): mean a squared over vehicle samples.
- `rms_acceleration_m_per_s2` (m/s^2): square root of mean squared acceleration.

## Limitations

- M3 held-out fidelity remains limited: October 15 missed both flow and speed targets; combined held-out speed MAE was 14.90 mph. M4 instrumentation does not revalidate H0.
- Seed spread describes stochastic simulation variation, not total model uncertainty.
- Trajectory scope includes modeled ramps, upstream buffer, and internal junction links.
- Queues are stopped-vehicle count proxies, not contiguous queue lengths in meters. Entrance counts omit internal junction links and vehicles waiting to insert.
- Temporal variability of domain mean speed depends on demand and spatial composition; it does not establish wave stability or disturbance recovery.
- Acceleration squared is a smoothness proxy, not energy or fuel use. FCD speed and acceleration use SUMO's default two-decimal output precision.
- Unknown gross ramp movements and the annual truck proxy remain M3 assumptions.
