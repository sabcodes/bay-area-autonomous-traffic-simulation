# Local feasibility research: Bay Area AV traffic simulation

**Scope.** This note assesses the supplied specification as a proposal, not as an
instruction source. Findings are based on official project and agency sources,
accessed 2026-09-21. It does not claim that a SUMO experiment predicts deployed
AV behaviour.

## Verdict

A useful local **12-mile US-101 prototype is feasible** on Apple Silicon: use
SUMO for the network and traffic dynamics, a small Python controller through
TraCI, and begin with deterministic or rule-based baseline policies. It can
support credible *comparative simulation experiments* after calibration. It is
not yet a credible basis for a real-world claim such as “4,500 veh/hr/lane,” a
zero shockwave-recovery target, or a regional system-optimum result. Those
claims require an explicit calibration/validation protocol, sensitivity
analysis, and much stronger assumptions about automation, communications,
demand, and incident response.

The recommended first milestone is a one-corridor, morning-peak scenario with
observed demand and speeds, then compare (1) human-like SUMO traffic, (2) an
idealized CACC/platoon parameter set, and (3) a centralized speed-advisory or
ramp-metering controller. Add RL only after those scenarios reproduce selected
PeMS observations reasonably well.

## Stack assessment

| Component | What current official sources support | Practical constraint / decision |
|---|---|---|
| SUMO + TraCI | TraCI provides lock-step simulation control, state queries, online vehicle/traffic-light intervention, subscriptions, and Python bindings. It directly supports a custom Gymnasium-style environment. [SUMO TraCI](https://sumo.dlr.de/docs/TraCI/), [Python interface](https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html) | Per-vehicle calls at 0.1-second steps add material overhead. Use context subscriptions, avoid all-pairs Python distance scans, and benchmark first. SUMO recommends API-compatible `libsumo` rather than TraCI when GUI is unnecessary and performance matters. [SUMO Python interface](https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html), [libsumo](https://sumo.dlr.de/docs/Libsumo.html) |
| OSM network | `netconvert` natively imports OSM into SUMO; the prescribed `--ramps.guess` and `--junctions.join` are documented import heuristics. [SUMO OSM import](https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html), [netconvert](https://sumo.dlr.de/docs/netconvert.html) | OSM often lacks added highway ramp lanes; junction joining can both miss and wrongly join cases. Manually audit every US-101 interchange, ramp connection, lane count, and permitted movement before using it for results. |
| CACC/platooning | SUMO includes ACC/CACC car-following models and safety-related `tau`/step-length parameters. [CACC](https://sumo.dlr.de/docs/Car-Following-Models/CACC.html), [safety](https://sumo.dlr.de/docs/Simulation/Safety.html), [basic definition](https://sumo.dlr.de/docs/Simulation/Basic_Definition.html) | A 0.25-second headway is an idealized controller assumption, not a result. Treat it as a sensitivity case; model communication delay/loss and verify string stability. SUMO’s own ACC documentation notes experimentally observed string instability in the original controller. [ACC](https://sumo.dlr.de/docs/Car-Following-Models/ACC.html) |
| PyTorch MPS | PyTorch documents the `mps` device for GPU training/inference on macOS and the standard availability check. [MPS backend](https://docs.pytorch.org/docs/2.14/notes/mps.html) | Use `float32`: MPS does not support `float64` or `complex128`. Benchmark the actual policy/environment mix and retain CPU fallback, since simulator stepping remains CPU-bound. [MPS limitations](https://docs.pytorch.org/docs/2.14/notes/mps.html) |
| Ray + RLlib | Current Ray docs list Apple Silicon and macOS arm64 wheels as supported and provide the `ray[rllib]` extra. [Ray installation](https://docs.ray.io/en/latest/ray-overview/installation.html) | Ray’s accelerator documentation lists NVIDIA, AMD, Intel and other accelerators, but not Apple MPS. Do not assume RLlib will schedule MPS as a Ray GPU resource; validate an explicit Torch-MPS learner separately and keep the initial RLlib run CPU-only. [Ray accelerator support](https://docs.ray.io/en/latest/ray-core/scheduling/accelerators.html) |
| RL problem shape | RLlib has a beta multi-agent API and supports distributed environment runners. [MultiAgentEnv](https://docs.ray.io/en/latest/rllib/package_ref/env/multi_agent_env.html), [scaling guide](https://docs.ray.io/en/latest/rllib/scaling-guide.html) | RLlib currently says multi-agent environments cannot be vectorized. A per-vehicle MAPPO setup at corridor scale is therefore a poor first local target. Start with a centralized controller, shared policy over a limited controlled fleet, or a small set of bottleneck/ramp agents. [scaling guide](https://docs.ray.io/en/latest/rllib/scaling-guide.html) |

## Data that is appropriate for the 12-mile prototype

1. **Caltrans PeMS (primary observed traffic data).** PeMS supplies real-time
   and historical freeway detector data, with nearly 40,000 detectors statewide;
   registration is free but an account is required. Use Station 4 data around
   the US-101 corridor to select representative non-holiday weekdays and derive
   5-minute mainline volumes/speeds (and ramp volumes where available). Preserve
   detector IDs, completeness filters, date selection, and the PeMS version.
   PeMS 14 reprocessed historical data with updated speed algorithms, so do not
   mix results from earlier PeMS releases without noting it. [Caltrans PeMS data
   source](https://dot.ca.gov/programs/traffic-operations/mpr/pems-source),
   [Caltrans PeMS data description](https://dot.ca.gov/programs/traffic-operations/mpr/pems-data)

2. **MTC Travel Model One (demand structure, not ground truth).** MTC publishes
   Travel Model One source and identifies the `TM1.5` branch specifically;
   MTC’s official work program identifies the same repository as the public
   model-code location. Use it to understand TAZ, trip-table, and time-period
   conventions and to build plausible origin/destination proportions. Aggregate
   those flows to US-101 entry/exit ramps and reconcile the totals to PeMS; do
   not inject a regional matrix directly into a short corridor. [MTC Travel
   Model One repository](https://github.com/BayAreaMetro/travel-model-one),
   [MTC work program](https://mtc.ca.gov/sites/default/files/meetings/attachments/5974/8d_24_0372_MTC_Resolution_4577_Attachment_A_0.pdf)

3. **OpenStreetMap (geometry seed).** Use a timestamped export and preserve
   attribution/licensing metadata. OSM is enough to bootstrap geometry, but it
   cannot validate lane operations or observed demand. SUMO explicitly flags
   that some OSM-imported infrastructure needs modification and manual checking.
   [SUMO OSM import limitations](https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html)

## Methodological corrections to the proposal

- The pseudo-controller computes every pairwise vehicle distance in Python each
  step. That is quadratic and unsuitable for dense traffic. Use TraCI context
  subscriptions with a radius/filter, SUMO leader/follower queries, or spatial
  indexing instead. [TraCI context subscriptions](https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html)
- `setSpeed` changes a vehicle-level outcome; it is not an implementation of
  steering, V2V radio, perception, or a safety-certified CACC controller. Model
  the desired abstraction explicitly: ideal instantaneous coordination versus
  latency/loss/noise cases.
- A 100% AV scenario should be one sensitivity endpoint, not the sole baseline.
  Include mixed penetrations and a no-coordination AV case, while holding demand,
  network, and vehicle parameters fixed.
- Separate **calibration** (match observed speed/flow/queue patterns) from
  **evaluation** (unseen days or scenarios). Report confidence intervals over
  demand seeds and controller parameters. Compare throughput only at matched
  bottlenecks; raw exit counts can hide diversion or delayed departures.
- “Fuel/energy” cannot be inferred robustly from acceleration squared alone.
  Call it a smoothness proxy unless an explicitly documented powertrain/energy
  model is added.

## Local readiness check

This workspace’s command-line environment is Apple Silicon/macOS 15.6.1 but
currently does **not** expose `sumo`, `traci`, `sumolib`, `torch`, or `ray` on
the default PATH/Python installation. The proposal can be implemented locally,
but dependency installation and a reproducible environment file are first
required. This is an environment observation, not a claim about system support.

## Go/no-go sequence

1. Install/version-pin SUMO, Python, `traci`/`sumolib`, and test a one-minute
   headless run; install PyTorch and test `torch.backends.mps.is_available()`.
2. Import and manually inspect the SR-237-to-Page-Mill network; keep a patch
   layer for corrected lanes/ramps.
3. Build PeMS-derived entry, exit, and mainline calibration targets for a small
   set of typical weekdays, then validate a human-driver baseline.
4. Implement rule-based coordination, log reproducible KPIs, and conduct
   sensitivity runs before introducing RL.
5. If RL remains valuable, train only a constrained controller first; make
   large-scale per-vehicle MARL a separately budgeted research phase.
