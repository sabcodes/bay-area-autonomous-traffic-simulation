# How traffic research groups build and validate experiments

This is a comparison of **specific published examples**, not a claim that all
labs follow one universal recipe. It separates a deliberately simplified
algorithm benchmark from an evidence-backed real-corridor experiment.

## What the primary sources actually show

| Example | Reported method | Lesson for this project |
| --- | --- | --- |
| UC Berkeley Flow benchmarks | Flow publishes small, configurable ring, figure-eight, bottleneck, and on-ramp-merge environments. Its ring example has a human-only non-RL configuration; the figure-eight benchmark explicitly states its vehicle counts and AV penetration rates. These are controlled **algorithm benchmarks**, not published lane-by-lane reconstructions of a named freeway. [Flow's network documentation](https://flow.readthedocs.io/en/latest/examples.html) | Use a toy corridor to debug control logic, but do not call success there a US-101 result. |
| California PATH I-210 freeway study | The researchers marked freeway features on a composite aerial image, scaled it with Caltrans aerial photographs, and traced links/connectors into VISSIM. They used PeMS for mainline counts and congestion contours, compared ramp data against manual surveys, represented HOV restrictions explicitly, and tuned a limited set of driver parameters until observed bottleneck timing, queue extent, and HOV/mixed-flow response were reasonably reproduced. [PATH report, §§4–5, 10.2, 13](https://horowitz.me.berkeley.edu/Publications_files/All_papers_numbered/Gomes_may_horowitz_PATH_report04.pdf) | Our PeMS cross-sections, ramps, managed lanes, and bottleneck patterns all matter; fitting total vehicle count alone is insufficient. |
| UC Berkeley/Caltrans Connected Corridors I-210 pilot | The team separated network geometry/control/demand inputs from calibration flows/travel times and **independent** validation flows/travel times. Its Phase 1 report documents a 15-day calibration set and a later six-day validation set; it also audited loop-detector quality and called out data gaps. The project calibrated across multiple time periods and day types, rather than treating one average peak as every condition. [AMS Phase 1 report, §§4.5 and 8](https://connected-corridors.berkeley.edu/sites/default/files/ams_phase_1_report_-_version_2.pdf); [I-210 model-calibration page](https://connected-corridors.berkeley.edu/developing-system/ams-analysis-modeling-and-simulation/model-calibration) | Keep M1 quality flags and separate M3 validation days; expand beyond one morning condition before making broad claims. |
| CIRCLES I-24 open-road study | Before its 100-vehicle field experiment, the team built and calibrated background traffic against measured flow and space-time speed patterns, then simulated AV scenarios and checked routes. That is substantially more than proving the simulation executes. [CIRCLES methods paper](https://arxiv.org/abs/2404.15533) | Controller comparisons should follow an observed-traffic baseline and route checks, not precede them. This local project makes no field-deployment or real-vehicle safety claim. |

## What counts as a credible real-corridor model

1. **Check the physical/operational network.** SUMO's own OSM-import guide says
   `netconvert` *guesses* lane-to-lane connections by default, ramp lanes may
   be absent from OSM, and some complex junction clusters need manual review.
   Import success and a connected route therefore do not establish real lane
   markings or lawful managed-lane use. [SUMO OSM-import documentation](https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html)
   The PATH I-210 team's aerial-plus-Caltrans construction is a concrete
   example of using external geometry evidence.
2. **Use observed data to define both demand and behavior targets.** The PATH
   study assessed detector reliability, used manual ramp counts where they
   disagreed with PeMS, and checked bottleneck onset/queue length rather than
   only total flow. [PATH report](https://horowitz.me.berkeley.edu/Publications_files/All_papers_numbered/Gomes_may_horowitz_PATH_report04.pdf)
   FHWA's 2019 guidance calls for at least a speed/travel-time measure and a
   bottleneck-dynamics measure. [FHWA calibration guidance](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter5.htm)
3. **Reserve data for an honest test.** The I-210 pilot explicitly held later
   days out of calibration for validation. [AMS Phase 1 report](https://connected-corridors.berkeley.edu/sites/default/files/ams_phase_1_report_-_version_2.pdf)
   FHWA's 2019 guidance favors a real representative day and a variation
   envelope across comparable days; it warns that an average synthetic day
   can smooth away actual incident/bottleneck behavior. [FHWA calibration
   guidance](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter5.htm)
   This differs from the older PATH I-210 study's composite typical-day
   construction; methodology evolved, and our choice of days must be stated.
4. **Compare policies only after the baseline is credible.** PATH's I-210 ramp
   metering research first constructed/calibrated the freeway model, then
   compared metering strategies. [Berkeley ITS project summary](https://its.berkeley.edu/publications/design-field-implementation-and-evaluation-adaptive-ramp-metering-algorithms)
   FHWA's 2019 alternatives guidance calls for seed replications, statistical
   comparison, and sensitivity tests for uncertain demand/assumptions. A small
   pilot set of seeds is not a final uncertainty analysis. [FHWA alternatives
   guidance](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter6.htm)

## What this means for our milestones

- **M1:** The [sensor audit](us101-sensor-audit.md) and
  [roadmap](project-roadmap.md) document the selected PeMS detectors, missing
  observations, and data-quality caveats. That is consistent with the
  real-corridor examples; do not replace missing observations with zeros or
  infer ramp demand from a mismapped detector.
- **M2:** The [network audit](us101-network-audit.md),
  [40-junction checklist](us101-ramp-review-checklist.md), and
  [acceptance record](us101-m2-acceptance.md) close the corridor network audit
  at the project's practical standard. All 40 branch junctions were reviewed;
  four carry fixed H0 demand and 36 do not. The review establishes plausible
  movement sides and connected lane links, **not** surveyed current striping.
  A later scenario sensitive to a ramp's exact lane operation needs a focused
  route and lane-use check. The 2018 plans and aerial views do not alone prove
  post-2022 as-built striping.
- **M3 and later:** Finish a human baseline that reproduces held-out flows,
  speeds, and bottleneck timing/extent before treating CACC or centralized
  speed/ramp control as a US-101 comparison. Then compare policies on the same
  documented network, demand conditions, and seed sets, and vary unresolved
  lane/demand assumptions explicitly. These are **proposed project gates**
  inferred from the sources above, not a claim that a particular lab published
  our exact M1–M8 roadmap.

The practical answer is that labs do not need perfect knowledge to begin
method development, but published *real-corridor* conclusions require a much
stronger evidence trail than a runnable map. Unknown as-built details should
be named, tested where possible, and excluded from claims they cannot support.
