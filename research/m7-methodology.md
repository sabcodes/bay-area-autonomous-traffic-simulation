# M7 methodology notes, 2026-10-17

Primary sources checked before implementation:

- [SUMO vehicle retrieval](https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html): acceleration is from the previous step; leader gap excludes ego minGap. M7 adds explicit message age to acceleration only, while preserving current sensing. Leader lookup may return beyond requested range, so retain the explicit cutoff.
- [SUMO randomness](https://sumo.dlr.de/docs/Simulation/Randomness.html): fixed seeds give deterministic random sequences; separate random streams serve loading, dynamics and devices. M7 hash selection avoids consuming them, but matching seeds cannot guarantee matched realized maneuvers.
- [SUMO flow definitions](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html): vehsPerHour defines equally spaced flows. Scaling requested rates is not an exact proportional scaling of rounded emitted vehicle counts. Compare generated route rates and actual counts separately.

Project choices, not empirically estimated distributions: demand 0.8/1.2,
penetration 0/0.5, 50 m range, 1 s extra delay, 20% loss, 2 s requested headway
and 22 m/s VSL target. They form an OFAT screen; interactions and full model
uncertainty remain unmeasured. Seed range and sample SD are descriptive.
No new traffic-calibration, field-validation or safety claim follows.
