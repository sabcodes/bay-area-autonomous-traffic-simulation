# Human-driven freeway baseline: current design versus research practice

## Bottom line

The current H0 scenario is a sound **first runnable baseline**, but it is not yet a
research-grade representation of Bay Area human traffic. It already follows one crucial rule:
observed PeMS speeds are an outcome to reproduce, not a speed command given to simulated cars.
The next calibration milestone should add ramp/OD demand, a measured vehicle mix, virtual
detectors, held-out-day checks, and multi-seed uncertainty before any automated-vehicle result is
treated as evidence.

## What the current scenario does

The implementation in `src/bay_area_traffic_sim/real_corridor.py` and
`configs/us101_human_baseline.json` currently:

- runs one 12.24 km northbound US-101 route through audited freeway checkpoints;
- converts the provisional PeMS five-minute profile into changing mainline entry flow;
- uses one passenger-car type with SUMO's stochastic Krauss car-following model (`tau=1.2`,
  `sigma=0.5`, and a 10% desired-speed deviation) and the default lane-changing model;
- warms the network for 15 minutes, runs with a 0.5-second simulation step, and supports a fixed
  random seed; and
- records completed-trip measures and SUMO's log.

That is enough to prove the map, route, demand importer, and simulator work together. It is not
enough to claim that simulated human traffic behaves like real US-101 traffic: the draft has no
on-ramp/off-ramp OD matrix, no truck/bus mix, no calibrated driver-behavior distribution, no
PeMS-like virtual detector comparison, and no independent validation-day or multi-seed report.

## What transportation laboratories normally establish

| Part of the baseline | Research/agency practice | What we should do next |
|---|---|---|
| Geometry and controls | Audit lane counts, ramp and gore geometry, auxiliary lanes, speed limits, and ramp controls. Caltrans lists these as normal simulation inputs, alongside bottleneck and queue locations.[^caltrans] | Finish the ramp/interchange audit and encode any ramp meters or lane restrictions that existed on the chosen observation day. |
| Demand and routes | Use time-varying OD demand and counts on the mainline **and ramps**. FHWA's freeway calibration example treats the mainline and ramps as critical elements, and SUMO recommends `routeSampler.py` for constructing demand from edge/turn counts.[^fhwa2014][^sumoroutes] | Add every meaningful on/off ramp as an origin or destination. Reconcile flows so vehicles do not appear or disappear between detectors. Use MTC/OD structure to constrain routes and PeMS mainline/ramp counts to scale them. |
| Vehicle population | Represent observed classifications such as passenger cars, trucks, and buses rather than one identical class.[^caltrans] SUMO supports probabilistic `vTypeDistribution` fleets.[^sumorandom] | Estimate fleet shares from PeMS lane/class data or another documented local source; give classes realistic lengths, acceleration, deceleration, and desired-speed distributions. |
| Human behavior | Calibrate a small, defensible set of car-following and lane-changing parameters. In SUMO these include desired headway (`tau`), imperfection (`sigma`), acceleration/deceleration and desired-speed variation, plus lane-changing cooperation and speed-gain behavior.[^sumovtype][^sumosafety] FHWA recommends calibrating capacity, then route choice, then overall system performance.[^fhwa2014] | First match bottleneck discharge/throughput using headway and lane-changing behavior; then adjust OD/route timing; finally check speed, travel time, queues, and bottleneck timing. Keep bounds and rationales in the experiment manifest. |
| Detector validation | Compare equivalent simulated and field quantities at the same places and time bins. SUMO supplies virtual detector and edge outputs, plus tools that compare detected and simulated flows.[^sumohighway] Original freeway research has calibrated and validated microscopic models against double-loop detector data.[^brockfeld] | Place virtual loops at the audited PeMS stations and report 5-minute flow, speed, and occupancy where available. Compare the full space-time profile, not only one corridor-wide average. |
| Calibration versus validation | Fit parameters on designated calibration data, then freeze them and test on data not used for fitting. Brockfeld et al. validated parameters calibrated on one freeway data set by applying them to other data sets.[^brockfeld] FHWA's newer practice also avoids a synthetic averaged day: it selects a real representative day and judges results against day-to-day variation envelopes.[^fhwa2019] | Select one incident-free representative weekday for calibration. Freeze all behavior parameters, then run several held-out weekdays. This held-out check is stricter than merely matching the same averaged profile used to tune the model. Report both representative-day fit and held-out performance. |
| Random uncertainty | Use several known seeds and report a mean, spread, and confidence interval. FHWA recommends an initial 5–10 runs with different seeds and then a statistically sufficient run count; SUMO provides explicit seeds and `runSeeds.py`.[^fhwa2014][^sumorandom] | Start with at least 10 seeds for each frozen scenario, then calculate whether more are needed for the chosen precision. Use the same seed set for human, CACC, and control alternatives so comparisons are fair. |
| Warmup and boundaries | Exclude the initialization period, when an initially empty network is filling, from results. FHWA says to choose the warmup by observing when system accumulation reaches a stable condition, rather than assuming a universal duration.[^fhwa2004] | Keep 15 minutes only provisionally. Plot vehicles-in-network and detector flow/speed, then lengthen the pre-period until the analysis window is not affected by initial loading. Ensure queues do not spill beyond spatial or temporal boundaries. |
| Simulation health and safety | Teleports can hide wrong-lane, yield, jam, weaving, or collision problems; a teleported vehicle is temporarily removed from the physical road.[^sumoteleport] SUMO also warns that step/action time, headway, and braking choices can create unsafe behavior.[^sumosafety] | Fail or prominently flag runs with teleports, collisions, emergency braking, insertion failures, or unfinished queues. Inspect every recurring location in the GUI. Later add surrogate-safety measures, but do not call “no teleports” a safety validation. |

## Why PeMS speed must not be directly commanded

The scientific question is whether realistic **demand + road geometry + human behavior** naturally
produce the observed slowdown. If the model is told “drive 45 mph here,” it can reproduce 45 mph
even when its demand, capacity, merging, or driver behavior is wrong. SUMO documents that a
speed-only calibrator behaves like a variable-speed sign, while a flow/speed calibrator can insert
or remove vehicles and adjust edge speed.[^sumocalibrator] That is an intervention, not an
independent prediction.

Therefore:

1. PeMS **flow** may constrain demand entering and moving through the corridor.
2. Geometry, ramp interaction, vehicle mix, and human parameters generate traffic dynamics.
3. PeMS **speed**, travel time, queue extent, and bottleneck onset/duration judge whether those
   dynamics are believable.

This follows FHWA's definition of calibration: change model parameters until simulated performance
measures reproduce field performance within a predetermined tolerance.[^fhwa2014] The 2019 guidance
specifically requires at least one travel-time or speed profile and another bottleneck-dynamics
measure, rather than fitting a single average speed.[^fhwa2019]

## Recommended acceptance gate before CACC experiments

The human baseline should be frozen only after it can:

1. reproduce 5-minute mainline and ramp flows at audited detector locations;
2. reproduce where and when congestion begins, its duration, and its recovery;
3. reproduce detector speed profiles and corridor travel time without commanding those speeds;
4. meet written error tolerances on a calibration day and remain credible on held-out days;
5. show uncertainty across multiple seeds; and
6. complete without unexplained teleports, collisions, emergency-braking warnings, or boundary
   truncation.

At that point, changing only the vehicle/control treatment gives a defensible comparison: any
improvement can be attributed to CACC or centralized control rather than to an unrealistic human
baseline.

## Sources

[^caltrans]: California Department of Transportation, [Simulation FAQs](https://dot.ca.gov/programs/transportation-planning/division-of-transportation-planning/state-planning/statewide-modeling/faq), especially the geometry, classification-count, bottleneck, travel-time, and OD data requirements.
[^fhwa2014]: Federal Highway Administration, [*Guidance on the Level of Effort Required to Conduct Traffic Analysis Using Microsimulation*, Chapter 6: Model Calibration](https://www.fhwa.dot.gov/publications/research/operations/13026/007.cfm), FHWA-HRT-13-026, 2014.
[^fhwa2019]: Federal Highway Administration, [*Traffic Analysis Toolbox Volume III*, Chapter 5: Model Calibration](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter5.htm), FHWA-HOP-18-036, 2019.
[^fhwa2004]: Federal Highway Administration, [*Traffic Analysis Toolbox Volume III: Guidelines for Applying Traffic Microsimulation Modeling Software*](https://ops.fhwa.dot.gov/trafficanalysistools/tat_vol3/Vol3_Guidelines.pdf), FHWA-HRT-04-040, especially sections 6.4.2 and Appendix C.
[^sumoroutes]: Eclipse SUMO, [Routes from Observation Points](https://sumo.dlr.de/docs/Demand/Routes_from_Observation_Points.html).
[^sumorandom]: Eclipse SUMO, [Randomness](https://sumo.dlr.de/docs/Simulation/Randomness.html).
[^sumovtype]: Eclipse SUMO, [Definition of Vehicles, Vehicle Types, and Routes](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html).
[^sumosafety]: Eclipse SUMO, [Safety](https://sumo.dlr.de/docs/Simulation/Safety.html).
[^sumohighway]: Eclipse SUMO, [Highway detector tutorial](https://sumo.dlr.de/docs/Tutorials/HighwayDetector.html).
[^sumoteleport]: Eclipse SUMO, [Why vehicles are teleporting](https://sumo.dlr.de/docs/Simulation/Why_Vehicles_are_teleporting.html).
[^sumocalibrator]: Eclipse SUMO, [Calibrator](https://sumo.dlr.de/docs/Simulation/Calibrator.html).
[^brockfeld]: E. Brockfeld, R. D. Kühne, and P. Wagner, [“Calibration and Validation of Microscopic Models of Traffic Flow”](https://doi.org/10.1177/0361198105193400119), *Transportation Research Record*, 1934(1), 2005.
