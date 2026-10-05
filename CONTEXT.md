# US-101 Traffic Simulation Language

This glossary names the project-specific concepts used in the corridor model,
observed-data audit, and scenario comparisons.

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
