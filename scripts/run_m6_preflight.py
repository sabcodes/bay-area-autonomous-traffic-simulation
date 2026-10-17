"""Retain a 3000-second M6 health/actuation probe without evaluating performance."""

import json
from pathlib import Path
from xml.etree import ElementTree as ET

from bay_area_traffic_sim.centralized import run_controlled
from bay_area_traffic_sim.real_corridor import prepare_human_baseline
from bay_area_traffic_sim.sumo_install import binary

root = Path(__file__).resolve().parents[1]
folder = root / "outputs/us101_corridor/m6/preflight_seed41"
folder.mkdir(parents=True, exist_ok=False)
base = json.loads((root / "configs/us101_human_baseline_m3_frozen.json").read_text())
base.update(
    route_file=str(folder / "h0.rou.xml"),
    manifest_file=str(folder / "manifest.json"),
    aligned_pems_report_file=str(folder / "observed.json"),
)
scenario = folder / "scenario.json"
scenario.write_text(json.dumps(base, indent=2) + "\n")
prepared = prepare_human_baseline(scenario)
config = json.loads((root / "configs/us101_m6_experiment.json").read_text())["scenarios"][-1][
    "controller"
]
log, summary = folder / "sumo.log", folder / "summary.xml"
diag = run_controlled(
    [
        str(binary("sumo")),
        "-n",
        prepared.network_file,
        "-r",
        prepared.route_file,
        "--step-length",
        "0.5",
        "--end",
        "3000",
        "--seed",
        "41",
        "--log",
        str(log),
        "--summary-output",
        str(summary),
        "--no-step-log",
        "true",
        "--duration-log.disable",
        "true",
    ],
    3000,
    config,
    folder / "controller_diagnostics.json",
)
warnings = [
    line
    for line in log.read_text().splitlines()
    if any(
        word in line.lower() for word in ["warning", "error", "teleport", "collision", "emergency"]
    )
]
result = {
    "seed": 41,
    "end_seconds": 3000,
    "warning_lines": warnings,
    "final_summary": ET.parse(summary).getroot().findall("step")[-1].attrib,
    "controller_diagnostics": diag,
    "accepted": not warnings
    and diag["completed"]
    and diag["restored"]
    and diag["commands"] > 0
    and diag["limited_lane_seconds"] > 0,
    "scope": "Truncated health and actuation only; not a clearance/performance acceptance.",
}
(root / "reports/m6").mkdir(exist_ok=True)
(root / "reports/m6/preflight_seed41.json").write_text(json.dumps(result, indent=2) + "\n")
print({key: result[key] for key in ["accepted", "warning_lines", "scope"]})
raise SystemExit(0 if result["accepted"] else 1)
