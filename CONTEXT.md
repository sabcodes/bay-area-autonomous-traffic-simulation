# US-101 Traffic Simulation Language

This glossary names the project-specific concepts used in the corridor model,
observed-data audit, and scenario comparisons.

As of 2026-10-16, M0–M4 are complete at their documented practical standards.
M3 retains its held-out fidelity limitation. The next milestone is M5
cooperative CACC. See [project memory](docs/project-memory.md), the
[roadmap](docs/project-roadmap.md), and the [M4 closeout](docs/m4-experiment-harness-report.md)
for current evidence and the resume point.

## Network and movements

**Study corridor**:
The US-101 northbound roadway from SR-237 to the Oregon Expressway/Page Mill
Road connection, together with the nearby ramp movements needed to model it.
_Avoid_: Bay Area network

**Through route**:
A directed path that stays on US-101 through the study area. Northbound is the
experiment route; southbound is also audited for network consistency.

**Branch junction**:
A point where a ramp or connector joins or leaves an audited through route.
Several branch junctions can belong to one interchange or ramp system.
_Avoid_: Ramp count

**Ramp movement**:
A directed entrance, exit, or connector path associated with a branch
junction. A movement may pass through several road segments.

**Auxiliary lane**:
A lane that serves a merge, exit, or weaving movement for a limited distance
rather than continuing along the US-101 mainline.
_Avoid_: Through lane

**Express connector**:
A separate managed-lane path connecting an express/HOV lane with another
roadway; its access rules may differ from general-purpose ramps.

## Evidence and experiments

**PeMS station**:
A Caltrans detector location supplying observed traffic measurements.

**PeMS channel**:
One lane-level measurement feed at a PeMS station. Its physical lane assignment
can remain uncertain even when the station's location is known.
_Avoid_: Physical lane

**Detector-to-lane alignment**:
The working correspondence between PeMS channels and modeled lane positions
for a comparison. A statistical match alone does not establish field wiring.

**H0**:
The human-like traffic scenario used as the calibration and comparison
baseline for later autonomous-vehicle scenarios.

**M2 network acceptance**:
The decision that the versioned corridor network is sufficiently plausible,
connected, and documented for this project's simulation work. It is not an
as-built certification or a traffic calibration result.

**M3 calibration**:
The process of tuning H0 demand and driving behavior against observed traffic,
then checking performance on separate days.

**Modeling approximation**:
A retained network choice whose real-world details are uncertain, with the
uncertainty and its impact recorded for later scenario interpretation.

## M4 measurement language

**Experiment harness**:
The command and explicit configuration that run a scenario/date/seed matrix,
isolate runtime files, retain failures and provenance, and summarize metrics
across seeds within each scenario and date.

**Measurement window**:
The half-open observation interval after warmup. The shipped M4 experiment uses
simulation seconds `[900, 8100)`, corresponding to 07:00–09:00; clearance follows.

**Departure cohort**:
Vehicles that actually enter the simulation during the measurement window,
followed through clearance for travel-time and delay statistics. This excludes
insertion delay and differs from a cohort selected by scheduled departure.

**Network exit throughput**:
All modeled route completions during the measurement window divided by window
hours, including ramp exits and vehicles that departed during warmup.
_Avoid_: Mainline bottleneck capacity

**Stopped-vehicle queue proxy**:
The mean or peak count of on-road vehicles with exported speed below the
configured stop threshold (M4 default: 0.1 m/s). Vehicles waiting to insert are
excluded. Entrance-approach counts also exclude shared mainline and internal links.
_Avoid_: Contiguous queue length in meters

**Temporal variability of domain mean speed**:
The population standard deviation of the mean vehicle speed at each nonempty
sampled timestep. The domain includes modeled ramps, buffer, and internal links;
demand and spatial composition affect this measure.
_Avoid_: Proven wave stability

**Acceleration smoothness**:
Mean squared exported longitudinal acceleration (m²/s⁴) and its square root,
RMS acceleration (m/s²), over vehicle samples in the measurement window.
_Avoid_: Energy or fuel consumption

**Seed spread**:
The sample standard deviation across random seeds for a fixed scenario and
date. It describes stochastic variation, not total model uncertainty or a
confidence interval for observed traffic.

**M4 run acceptance**:
Complete measurement output and a clean, cleared simulation: no SUMO warnings,
loaded = inserted = ended, and zero remaining running/waiting/discarded vehicles,
collisions, or teleports. Acceptance does not remove M3's traffic-fidelity limit.
