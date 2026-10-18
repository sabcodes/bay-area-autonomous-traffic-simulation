"""Independently check engine time grid, clearance, fleet and frozen metadata."""

import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    report_path = ROOT / "reports/m7/report.json"
    report = json.loads(report_path.read_text())
    assert report["complete"] and len(report["runs"]) == 54
    base = json.loads((ROOT / "configs/us101_human_baseline_m3_frozen.json").read_text())
    network = ROOT / base["network_file"]
    network_sha = hashlib.sha256(network.read_bytes()).hexdigest()
    assert network_sha == base["expected_input_sha256"][base["network_file"]]
    checked = []
    for run in report["runs"]:
        if "metrics" not in run:
            assert not run["accepted"]
            checked.append(
                {
                    "case": run["case"],
                    "scenario": run["scenario"],
                    "seed": run["seed"],
                    "native_metadata_checked": False,
                    "reason": run["error"],
                }
            )
            continue
        directory = ROOT / run["directory"]
        manifest_path = directory / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        scenario = json.loads((directory / "scenario.json").read_text())
        scenario_hash = hashlib.sha256(json.dumps(scenario, sort_keys=True).encode()).hexdigest()
        assert scenario_hash == run["resolved_scenario_sha256"]
        assert scenario["human_parameters"] == base["human_parameters"]
        assert scenario["warmup_seconds"] == 900 and scenario["clearance_seconds"] == 7200
        assert scenario["expected_input_sha256"] == base["expected_input_sha256"]
        assert manifest["observation_dates"] == ["2025-10-08"] == [run["date"]]
        assert manifest["human_parameters"] == base["human_parameters"]
        assert manifest["truck_share"] == base["truck_share"] == 0.04
        assert manifest["vehicle_types"] == base["frozen_vehicle_types"]
        assert manifest["network_sha256"] == network_sha == run["network_sha256"]
        assert manifest["provenance"] == run["provenance"]
        assert manifest["demand_profile"][0]["begin_seconds"] == 900
        end = manifest["demand_profile"][-1]["end_seconds"]
        assert end == 8100 and manifest["simulation_end_seconds"] == 15300
        assert manifest["simulation_end_seconds"] - end == base["clearance_seconds"] == 7200
        count = 0
        for _, element in ET.iterparse(
            directory / f"h0_summary_seed_{run['seed']}.xml", events=["end"]
        ):
            if element.tag == "step":
                assert float(element.get("time")) == count * 0.5, (
                    run["directory"],
                    count,
                    element.get("time"),
                )
                count += 1
            element.clear()
        assert count == 30600
        checked.append(
            {
                "case": run["case"],
                "scenario": run["scenario"],
                "seed": run["seed"],
                "native_metadata_checked": True,
                "summary_steps": count,
                "step_seconds": 0.5,
                "measurement_begin": 900,
                "measurement_end_exclusive": 8100,
                "clearance_seconds": 7200,
                "frozen_fleet_and_provenance_match": True,
                "scenario_hash_matches": True,
                "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            }
        )
    result = {
        "accepted": True,
        "runs_checked": len(checked),
        "numerically_completed_runs_checked": sum(r["native_metadata_checked"] for r in checked),
        "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
        "auditor_sha256": {
            str(Path(__file__).resolve().relative_to(ROOT)): hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest()
        },
        "runs": checked,
    }
    (ROOT / "reports/m7/native_metadata_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        "Native metadata audit passed:",
        result["numerically_completed_runs_checked"],
        "runs; complete 0.5 s time grids, 7200 s clearance, frozen fleet and provenance.",
    )
