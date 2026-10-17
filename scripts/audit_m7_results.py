"""Independent M7 raw audit; no production metric or controller imports."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import mean, stdev
from xml.etree import ElementTree as ET

import numpy as np
from audit_m6_results import equal, trajectory_audit


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ledger_audit(d, network, config):
    assert d["completed"] and d["restored"]
    assert d["controller"] == config
    native, observed = {}, []
    for edge in ET.parse(network).getroot().findall("edge"):
        if edge.get("id") in config["control_edge_ids"]:
            native.update(
                {lane.get("id"): float(lane.get("speed")) for lane in edge.findall("lane")}
            )
        if edge.get("id") in config["observation_edge_ids"]:
            observed.extend(lane.get("id") for lane in edge.findall("lane"))
    assert native == d["native_lane_limits"] and sorted(observed) == d["observation_lane_ids"]
    limits, mode, commands, exposure = dict(native), False, 0, 0
    for i, row in enumerate(d["ledger"], 1):
        assert row["time_seconds"] == i * config["update_seconds"]
        exposure += config["update_seconds"] * sum(limits[k] < native[k] for k in native)
        n, total = row["vehicle_samples"], row["speed_sum_m_per_s"]
        assert type(n) is int and n >= 0 and math.isfinite(total) and total >= 0
        speed = total / n if n else None
        equal(row["mean_speed_m_per_s"], speed)
        if row["time_seconds"] >= config["control_end_seconds"] or speed is None:
            mode = False
        elif speed < config["activate_below_m_per_s"]:
            mode = True
        elif speed > config["release_above_m_per_s"]:
            mode = False
        if row["time_seconds"] > config["control_end_seconds"]:
            assert n == total == 0
        assert mode == row["congested"] and row["lane_limits"].keys() == native.keys()
        for lane, original in native.items():
            target = min(original, config["congested_limit_m_per_s"]) if mode else original
            value = limits[lane] + np.clip(
                target - limits[lane], -config["max_change_m_per_s"], config["max_change_m_per_s"]
            )
            equal(row["lane_limits"][lane], value)
            commands += value != limits[lane]
            limits[lane] = value
    assert len(d["ledger"]) == d["updates"] == 510
    assert commands == d["commands"]
    equal(exposure, d["limited_lane_seconds"])
    return {"updates": 510, "commands": int(commands), "limited_lane_seconds": exposure}


def audit_run(job):
    root, run = job
    directory, seed = root / run["directory"], run["seed"]
    if "metrics" not in run:
        assert not run["accepted"] and run.get("error")
        return {
            "case": run["case"],
            "scenario": run["scenario"],
            "seed": seed,
            "raw_metric_checks": 0,
            "exception": run["error"],
        }, None
    trips = [
        t.attrib
        for t in ET.parse(directory / f"h0_human_baseline_seed_{seed}.tripinfo.xml")
        .getroot()
        .findall("tripinfo")
    ]
    actual = [t for t in trips if 900 <= float(t["depart"]) < 8100]
    done = [t for t in actual if float(t["arrival"]) >= 0]
    inserted = [t for t in trips if float(t["depart"]) >= 0 and float(t["departDelay"]) >= 0]
    scheduled = [
        t for t in inserted if 900 <= round(float(t["depart"]) - float(t["departDelay"]), 2) < 8100
    ]
    scheduled_done = [t for t in scheduled if float(t["arrival"]) >= 0]
    unknown = len(trips) - len(inserted)

    def avg(xs):
        return mean(xs) if xs else None

    exits = sum(900 <= float(t["arrival"]) < 8100 for t in trips)
    values = {
        "window_exit_vehicles": exits,
        "network_exit_throughput_vehicles_per_hour": exits / 2,
        "cohort_completed_vehicles": len(done),
        "cohort_unfinished_vehicles": len(actual) - len(done),
        "cohort_mean_travel_time_seconds": avg([float(t["duration"]) for t in done]),
        "cohort_p95_travel_time_seconds": float(
            np.percentile([float(t["duration"]) for t in done], 95)
        )
        if done
        else None,
        "cohort_mean_waiting_time_seconds": avg([float(t["waitingTime"]) for t in done]),
        "cohort_mean_time_loss_seconds": avg([float(t["timeLoss"]) for t in done]),
        "window_actual_departures": len(actual),
        "unreconstructed_scheduled_departures": unknown,
        "scheduled_cohort_vehicles": len(scheduled) if not unknown else None,
        "scheduled_cohort_completed_vehicles": len(scheduled_done) if not unknown else None,
        "scheduled_cohort_mean_depart_delay_seconds": avg(
            [float(t["departDelay"]) for t in scheduled]
        )
        if not unknown
        else None,
        "scheduled_cohort_mean_total_time_seconds": avg(
            [float(t["duration"]) + float(t["departDelay"]) for t in scheduled_done]
        )
        if not unknown
        else None,
        "whole_run_mean_depart_delay_seconds": avg([float(t["departDelay"]) for t in inserted]),
        "whole_run_max_depart_delay_seconds": max(
            [float(t["departDelay"]) for t in inserted], default=None
        ),
    }
    steps = ET.parse(directory / f"h0_summary_seed_{seed}.xml").getroot().findall("step")
    values["peak_insertion_backlog_vehicles"] = max(int(s.get("waiting")) for s in steps)
    values["window_peak_insertion_backlog_vehicles"] = max(
        int(s.get("waiting")) for s in steps if 900 <= float(s.get("time")) < 8100
    )
    final = steps[-1].attrib
    assert final == run["health"]["final_summary"]
    log = (directory / f"h0_human_baseline_seed_{seed}.log").read_text().splitlines()
    warnings = [
        line
        for line in log
        if any(
            w in line.lower() for w in ["warning", "error", "teleport", "collision", "emergency"]
        )
    ]
    assert warnings == run["health"]["warning_lines"]
    healthy = (
        not warnings
        and all(
            float(final[k]) == 0
            for k in ["running", "waiting", "discarded", "collisions", "teleports"]
        )
        and float(final["loaded"]) == float(final["inserted"]) == float(final["ended"])
    )
    route = directory / "h0.rou.xml"
    assert sha(route) == run["route_sha256"]
    routes = {
        r.get("id"): r.get("edges").split() for r in ET.parse(route).getroot().findall("route")
    }
    through, ramps = set(routes["us101_northbound"]), set()
    for edges in routes.values():
        if edges[0] not in through:
            for edge in edges:
                if edge in through:
                    break
                ramps.add(edge)
    assert sorted(ramps) == run["measurement"]["ramp_approach_edge_ids"]
    values.update(trajectory_audit(directory / "trajectory.fcd.xml.gz", ramps))
    assert values.keys() == run["metrics"].keys()
    for key, value in values.items():
        equal(run["metrics"][key], value)
    controller = run.get("controller")
    policy = None
    valid = True
    if controller:
        d = json.loads((directory / "controller_diagnostics.json").read_text())
        assert d == run["controller_diagnostics"] and d["controller"] == controller
        valid = (
            d["completed"]
            and d["engine_version"].split()[-1] == run["provenance"]["sumo_version"].split()[-1]
        )
        if controller["policy"] == "central_vsl":
            valid = valid and d["restored"] and d["updates"] > 0
            policy = ledger_audit(
                d, root / "outputs/us101_corridor/us101_corridor.net.xml", controller
            )
        else:
            valid = valid and d["native_fallbacks"] == 0
            passengers = [t["id"] for t in inserted if t["vType"] == "human_passenger"]
            equipped = sorted(
                v
                for v in passengers
                if int(hashlib.sha256(f"equipment|{v}".encode()).hexdigest()[:16], 16) / (1 << 64)
                < controller.get("penetration", 1)
            )
            assert d["eligible_vehicles"] == len(passengers)
            assert d["controlled_vehicles"] == len(equipped)
            assert (
                d["equipped_ids_sha256"] == hashlib.sha256("\n".join(equipped).encode()).hexdigest()
            )
            assert (
                d["commands"]
                == d["cooperative_commands"] + d["acc_commands"] + d["cruise_commands"]
            )
            assert (
                d["message_opportunities"]
                == d["messages_delivered"] + d["messages_lost"] + d["messages_unavailable"]
            )
            assert d["messages_delivered"] == d["cooperative_commands"]
            assert (
                d["equipped_samples"]
                == d["commands"] + d["supervised_native_samples"] + d["native_fallbacks"]
            )
            assert 0 <= d["equipped_samples"] <= d["passenger_samples"]
            policy = {
                "equipped_vehicles": len(equipped),
                "eligible_vehicles": len(passengers),
                "commands": d["commands"],
                "messages_delivered": d["messages_delivered"],
                "messages_lost": d["messages_lost"],
            }
    assert run["accepted"] == bool(healthy and valid)
    fleet = {
        t["id"]: (
            t["vType"],
            t["speedFactor"],
            round(float(t["depart"]) - float(t["departDelay"]), 2),
        )
        for t in inserted
    }
    print(f"Audited {run['case']}/{run['scenario']}/{seed}: {len(values)} raw metrics", flush=True)
    return {
        "case": run["case"],
        "scenario": run["scenario"],
        "seed": seed,
        "raw_metric_checks": len(values),
        "accepted": run["accepted"],
        "policy": policy,
        "fleet_complete": unknown == 0,
        "raw_file_sha256": {
            p.name: sha(p)
            for p in sorted(directory.iterdir())
            if p.suffix in {".xml", ".gz", ".log"} or p.name == "controller_diagnostics.json"
        },
    }, fleet


def audit(root, report_path, config_path, workers=3):
    report, config = json.loads(report_path.read_text()), json.loads(config_path.read_text())
    assert (
        report["complete"]
        and report["campaign"] == config
        and report["completed_cases"] == len(config["cases"])
    )
    assert report["campaign_config_sha256"] == sha(config_path)
    expected = {(c["id"], p, s) for c in config["cases"] for p in c["policies"] for s in c["seeds"]}
    runs = report["runs"]
    index = {(r["case"], r["scenario"], r["seed"]): r for r in runs}
    assert len(runs) == len(index) == len(expected) == 54 and set(index) == expected
    assert report["all_runs_accepted"] == all(r["accepted"] for r in runs)
    hashes = {
        str(p.relative_to(root)): sha(p)
        for p in sorted((root / "src/bay_area_traffic_sim").glob("*.py"))
    }
    baseline = json.loads((root / config["baseline_config"]).read_text())
    for path in report["experiment_reports"]:
        child = json.loads((root / path).read_text())
        assert child["source_sha256"] == hashes
        artifact = (
            root / path
        ).parent.parent / f"{child['experiment']['experiment_id']}_experiment.json"
        assert child["experiment_config_sha256"] == sha(artifact)
        for r in child["runs"]:
            assert {
                k: v
                for k, v in index[
                    child["experiment"]["experiment_id"], r["scenario"], r["seed"]
                ].items()
                if k not in {"case", "demand_scale"}
            } == r
    for path, value in baseline["expected_input_sha256"].items():
        assert sha(root / path) == value
    with ProcessPoolExecutor(max_workers=workers) as pool:
        checked = list(pool.map(audit_run, [(root, r) for r in runs]))
    fleets = {(r["case"], r["scenario"], r["seed"]): f for r, f in checked}
    reference_routes = ET.parse(
        root / index["base", "H0", 41]["directory"] / "h0.rou.xml"
    ).getroot()
    flow_reference = {f.get("id"): f.attrib for f in reference_routes.findall("flow")}
    fleet_checks, replay_checks = [], []
    m6 = json.loads((root / "reports/m6/report.json").read_text())
    old = {(r["scenario"], r["seed"]): r for r in m6["runs"]}
    for key, run in index.items():
        case, name, seed = key
        case_config = next(c for c in config["cases"] if c["id"] == case)
        assert run["demand_scale"] == case_config["demand_scale"]
        expected_controller = (
            {**config["controllers"][name], **case_config["policies"][name]}
            if name != "H0"
            else None
        )
        scenario = json.loads((root / run["directory"] / "scenario.json").read_text())
        assert scenario.get("controller") == expected_controller
        if "metrics" not in run:
            continue
        assert run.get("controller") == expected_controller
        reference_case = case if case.startswith("demand_") else "base"
        ref = index[reference_case, "H0", seed]
        assert run["route_sha256"] == ref["route_sha256"]
        assert (
            run["network_sha256"] == ref["network_sha256"]
            and run["provenance"] == ref["provenance"]
        )
        if fleets[key] is not None and fleets[reference_case, "H0", seed] is not None:
            a, b = fleets[key], fleets[reference_case, "H0", seed]
            assert all(a[v] == b[v] for v in a.keys() & b.keys())
            complete = (
                run["metrics"]["unreconstructed_scheduled_departures"]
                == ref["metrics"]["unreconstructed_scheduled_departures"]
                == 0
            )
            if complete:
                assert a == b
            fleet_checks.append(
                {"case": case, "scenario": name, "seed": seed, "complete_match": complete}
            )
        generated = ET.parse(root / run["directory"] / "h0.rou.xml").getroot()
        assert [t.attrib for t in generated.iter("vType")] == [
            t.attrib for t in reference_routes.iter("vType")
        ]
        for flow in generated.findall("flow"):
            attrs, before = flow.attrib, flow_reference[flow.get("id")]
            assert {k: v for k, v in attrs.items() if k != "vehsPerHour"} == {
                k: v for k, v in before.items() if k != "vehsPerHour"
            }
            # Route files export rates at two decimal places.
            assert (
                abs(
                    float(attrs["vehsPerHour"]) - float(before["vehsPerHour"]) * run["demand_scale"]
                )
                <= 0.011
            )
        if case == "base" and seed <= 43:
            assert run["metrics"] == old[name, seed]["metrics"]
            assert run["route_sha256"] == old[name, seed]["route_sha256"]
            replay_checks.append(f"M6/{name}/{seed}")
        if case == "penetration_000":
            assert run["metrics"] == ref["metrics"]
            assert run["legacy_whole_run_metrics"] == ref["legacy_whole_run_metrics"]
            assert sha(root / run["detector_summary_file"]) == sha(
                root / ref["detector_summary_file"]
            )
            replay_checks.append(f"zero-equipment/H0/{seed}")
    expected_groups = {(c["id"], p) for c in config["cases"] for p in c["policies"]}
    assert len(report["groups"]) == len(expected_groups)
    assert {(g["case"], g["scenario"]) for g in report["groups"]} == expected_groups
    checks = 0
    for group in report["groups"]:
        case, name, seeds = group["case"], group["scenario"], group["planned_seeds"]
        expected_case = next(c for c in config["cases"] if c["id"] == case)
        assert seeds == expected_case["seeds"] and name in expected_case["policies"]
        rows = [index[case, name, s] for s in seeds]
        assert group["accepted"] == all(r["accepted"] for r in rows)
        reference_case = case if "H0" in expected_case["policies"] else "base"
        assert group["reference_case"] == reference_case and group["reference_scenario"] == "H0"
        assert (
            group["metrics"].keys()
            == group["paired_metrics"].keys()
            == next(r["metrics"] for r in runs if "metrics" in r).keys()
        )
        for metric in group["metrics"]:
            values = [r.get("metrics", {}).get(metric) if r["accepted"] else None for r in rows]
            refs = [index[reference_case, "H0", s] for s in seeds]
            before = [r.get("metrics", {}).get(metric) if r["accepted"] else None for r in refs]
            differences = [
                a - b
                if a is not None and b is not None and math.isfinite(a) and math.isfinite(b)
                else None
                for a, b in zip(values, before, strict=True)
            ]
            for saved, items in [
                (group["metrics"][metric], values),
                (group["paired_metrics"][metric], differences),
            ]:
                good = [x for x in items if x is not None and math.isfinite(x)]
                complete = len(good) == len(seeds)
                assert saved["valid_seed_count"] == len(good)
                for key, calculated in [
                    ("mean", mean(good) if complete else None),
                    ("sample_standard_deviation", stdev(good) if complete else None),
                    ("minimum", min(good) if complete else None),
                    ("maximum", max(good) if complete else None),
                ]:
                    equal(saved[key], calculated)
            saved = group["paired_metrics"][metric]
            assert saved["pairs"] == [
                {"seed": s, "difference": d} for s, d in zip(seeds, differences, strict=True)
            ]
            complete = all(d is not None for d in differences)
            for label, predicate in [
                ("positive", lambda x: x > 0),
                ("negative", lambda x: x < 0),
                ("zero", lambda x: x == 0),
            ]:
                assert saved[f"{label}_count"] == (
                    sum(predicate(d) for d in differences) if complete else None
                )
            equal(
                saved["percent_of_reference_mean"],
                100 * mean(differences) / mean(before) if complete and mean(before) else None,
            )
            checks += 1
    return {
        "accepted": True,
        "report_sha256": sha(report_path),
        "source_sha256": hashes,
        "experiment_reports_sha256": {p: sha(root / p) for p in report["experiment_reports"]},
        "auditor_sha256": {
            str(p.relative_to(root)): sha(p)
            for p in [Path(__file__).resolve(), root / "scripts/audit_m6_results.py"]
        },
        "campaign_config_sha256": sha(config_path),
        "runs": [r for r, _ in checked],
        "raw_metric_checks": sum(r["raw_metric_checks"] for r, _ in checked),
        "aggregate_and_paired_metric_checks": checks,
        "fleet_checks": fleet_checks,
        "exact_replays": replay_checks,
        "limitations": [
            "VSL observations checked from interval totals, not an independent live sensor feed.",
            "Equipment selection and message accounting independently checked; "
            "full-corridor packet histories are not exported. Message semantics "
            "and deterministic replay are integration-tested.",
            "FCD uses 1 s sampling and default two-decimal precision. Incomplete "
            "fleet schedules permit common-ID checks only, and suppress "
            "scheduled-cohort aggregates.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("outputs/us101_corridor/m7/m7_ofat_2025_10_08/report.json"),
    )
    parser.add_argument("--config", type=Path, default=Path("configs/us101_m7_sensitivity.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/m7/independent_audit.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = audit(root, root / args.report, root / args.config)
    (root / args.output).parent.mkdir(parents=True, exist_ok=True)
    (root / args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"M7 audit accepted: {result['raw_metric_checks']} raw and "
        f"{result['aggregate_and_paired_metric_checks']} group/paired metrics."
    )
