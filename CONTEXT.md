# US-101 Traffic Simulation Language

This glossary names the project-specific concepts used in the corridor model,
observed-data audit, and scenario comparisons.

M0-M8 are complete at the documented practical experiment standard as of
2026-10-18. The [final research report](docs/final-research-report.md),
[data-derived tables](reports/m8/results.md), and
[reproduction guide](docs/reproduction.md) are the final package entry points.
M3's held-out fidelity failure, about 2% supervised CACC engagement and the M7
one-day OFAT limits remain. The evidence establishes no consistent overall
traffic benefit. M8 adds packaging checks without changing the simulator.

M7 is merged at ad33a7f; M8 is prepared on codex/m8-research-package for review.

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

## M5 cooperative-control language

**Supervised CACC overlay**:
A deterministic longitudinal command law using gap error, relative speed and
passenger-leader acceleration feedforward within the unchanged native Krauss
safety envelope. It engages only after 2 s of quiet native maneuver state and
hands speed authority back for native lane changes/cooperation. Report its
active command fraction; equipped passengers are not continuously controlled.
The policy differs from SUMO's native CACC model, which failed a separate probe.

**Cooperative leader**:
A passenger leader whose previous-step acceleration is available in the same
subscription snapshot. Trucks do not broadcast; passenger followers behind
trucks use ACC without acceleration feedforward.

**Ideal communication**:
No packet loss or additional network latency within the declared leader-query
range. The 0.5 s simulation/control timing and previous-step acceleration still
apply. The 250 m cutoff uses the TraCI gap, which excludes ego minGap.

**Scheduled-departure cohort**:
Trips whose intended departure falls in the measurement window, reconstructed
from actual departure minus insertion delay at native output precision. This
population differs from actual-window departures. Uninserted trips make the
schedule reconstruction incomplete and the scheduled metrics null.

**Scheduled-cohort total time**:
Completed trip duration plus SUMO departDelay, measured from intended departure
to arrival. This includes insertion delay that actual-departure travel time
excludes; it is not delay relative to a field-observed free-flow trip.

**Insertion backlog**:
SUMO summary vehicles waiting to enter the modeled network. Report its peak
separately from on-road stopped-vehicle queue proxies.

**Paired seed difference**:
CACC minus H0 for matching date and seed, followed by the mean and sample SD of
those differences. Matching seeds and generated inputs do not make the two
scenarios' realized lane changes or actual departure cohorts identical.

**M5 acceptance**:
A clean, matched H0/supervised-CACC comparison with explicit active command share
(about 2% of all-run passenger timesteps). It does not accept the rejected
continuous variants, establish a traffic benefit, or remove M3's fidelity limit.

## M6 centralized-control language

**Centralized VSL**:
An illustrative central feedback policy that observes simulated lane traffic
downstream and changes native lane speed limits on the existing upstream buffer.
It retains human-like following and lane changing, independently of CACC.

**Vehicle-timestep-weighted speed**:
Sum of lane vehicle count times last-step mean speed divided by the sum of counts
across observed lanes and simulation steps. Empty lanes carry zero weight.

**VSL hysteresis**:
The frozen policy activates below 15 m/s and releases above 20 m/s; it retains
mode at equality/in the band and releases on an empty interval.

**Limited-lane seconds**:
Time-integrated number of controlled lanes below their original native limit.
This measures actuation exposure, not vehicle compliance or distance controlled.

**M6 acceptance**:
A clean, fully cleared H0/CACC/CENTRAL comparison with nonzero central actuation,
restored native limits, matching inputs/fleets/schedules, exact reference replay
and an independent metric/decision audit. Acceptance does not establish a
traffic benefit, field compliance or an optimized controller.

## M7 sensitivity language

**OFAT screen**: A bounded one-factor-at-a-time sensitivity evaluation around
M6. It varies demand, equipment, communication and controller settings without
estimating interactions or total model uncertainty.

**Passenger equipment penetration**: A target fraction of passenger IDs selected
by a stable SHA-256 rule. Trucks remain native. Equipment does not imply active
control: the native maneuver supervisor still decides whether commands engage.

**Extra message age**: Added delay for a same-leader acceleration message beyond
SUMO's previous-step acceleration semantics. Current local gap and speed remain
available. Missing/dropped messages use ACC, without stale-message hold.

**M7 execution validity**: Clean clearance, complete outputs and completed native
controller operation. Unlike M5/M6 actuation acceptance, M7 intentionally retains
valid inactive/null controls. Activity, exposure, failures and all planned seeds
are reported separately. See docs/m7-sensitivity-uncertainty-spec.md.

## M8 packaging language

**Saved-evidence package verification**: Recompute headline pairs and station
scores from versioned evidence, verify the accepted report/audit/source binding,
and compare content hashes and deterministic generated bytes. This check does
not rerun raw trajectory reconstruction or establish field validity.

**Reproduction tiers**: Clone-only saved-package verification, separate frozen
local-input hash checks, and full fresh-ID runtime replay requiring local PeMS
sources and storage. Passing one does not imply the others were performed.

**M8 acceptance**: A complete reproducible methods/results/caveat/source package
at the project's practical standard. It preserves M3 fidelity, supervised CACC
exposure and OFAT uncertainty limits; it does not add a field-benefit claim.
