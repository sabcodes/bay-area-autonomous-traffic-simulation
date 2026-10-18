"""Review regressions: audit binding and complete-population factor reporting."""

import json
from copy import deepcopy

import pytest

from bay_area_traffic_sim.toy_corridor import repository_root


def test_m6_rejects_stale_audit_before_writing(tmp_path, monkeypatch):
    root = repository_root()
    monkeypatch.syspath_prepend(str(root / "scripts"))
    from summarize_m6_results import summarize

    report = json.loads((root / "reports/m6/report.json").read_text())
    report["groups"][0]["metric_summary"]["network_exit_throughput_vehicles_per_hour"]["mean"] = (
        9999
    )
    changed = tmp_path / "changed.json"
    changed.write_text(json.dumps(report))
    output = tmp_path / "presentation"
    with pytest.raises(ValueError, match="does not match"):
        summarize(changed, root / "reports/m6/independent_audit.json", output)
    assert not output.exists()


@pytest.mark.parametrize("side", ["half", "base"])
@pytest.mark.parametrize(
    "mode",
    [
        "null",
        "nan",
        "inf",
        "missing_metric",
        "missing_seed",
        "failed",
        "bool",
        "string",
        "overflow",
    ],
)
def test_factor_reporting_suppresses_incomplete_population(side, mode, monkeypatch):
    root = repository_root()
    monkeypatch.syspath_prepend(str(root / "scripts"))
    from audit_m7_results import audit_factor_effects
    from summarize_m7_results import METRICS, factor_effects

    report = {
        "campaign": {"cases": [{"id": "half", "policies": {"CACC": {}}, "seeds": [41, 42]}]},
        "groups": [{"case": "half", "scenario": "CACC", "planned_seeds": [41, 42]}],
        "runs": [
            {
                "case": case,
                "scenario": "CACC",
                "seed": seed,
                "accepted": True,
                "metrics": dict.fromkeys(METRICS, value),
            }
            for case, seed, value in [
                ("base", 41, 10),
                ("base", 42, 20),
                ("half", 41, 12),
                ("half", 42, 24),
            ]
        ],
    }
    good = factor_effects(report)
    assert all(
        e["mean"] == 3 and e["sample_standard_deviation"] == pytest.approx(2**0.5) for e in good
    )
    changed = deepcopy(report)
    row = next(r for r in changed["runs"] if r["case"] == side and r["seed"] == 42)
    if mode == "missing_seed":
        changed["runs"].remove(row)
    elif mode == "failed":
        row["accepted"] = False
    elif mode == "missing_metric":
        row["metrics"].clear()
    elif mode == "overflow":
        row["metrics"] = dict.fromkeys(METRICS, 1e308)
        other = next(r for r in changed["runs"] if r["case"] != side and r["seed"] == 42)
        other["metrics"] = dict.fromkeys(METRICS, -1e308)
    else:
        row["metrics"] = dict.fromkeys(
            METRICS,
            {
                "null": None,
                "nan": float("nan"),
                "inf": float("inf"),
                "bool": True,
                "string": "invalid",
            }[mode],
        )
    effects = factor_effects(changed)
    assert all(
        e["pairs"] == [{"seed": 41, "difference": 2}, {"seed": 42, "difference": None}]
        for e in effects
    )
    assert all(e["mean"] is None and e["sample_standard_deviation"] is None for e in effects)
    json.dumps(effects, allow_nan=False)
    assert audit_factor_effects(changed, effects)["factor_metric_checks"] == 4
    with pytest.raises(AssertionError):
        audit_factor_effects(changed, good)


def test_m7_render_preserves_null_factor_in_published_file(tmp_path, monkeypatch):
    import hashlib

    from bay_area_traffic_sim.sensitivity import summarize

    root = repository_root()
    monkeypatch.syspath_prepend(str(root / "scripts"))
    from audit_m7_results import audit_factor_effects
    from summarize_m7_results import render

    report = json.loads((root / "reports/m7/report.json").read_text())
    row = next(r for r in report["runs"] if r["case"] == "headway_2000" and r["seed"] == 42)
    metric = "network_exit_throughput_vehicles_per_hour"
    row["metrics"][metric] = None
    report["groups"] = summarize(report["campaign"], report["runs"])
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report, allow_nan=False))
    audit = json.loads((root / "reports/m7/independent_audit.json").read_text())
    audit["report_sha256"] = hashlib.sha256(report_path.read_bytes()).hexdigest()
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(audit))
    output = tmp_path / "presentation"
    render(report_path, audit_path, output)
    effects = json.loads((output / "factor_effects.json").read_text())
    effect = next(e for e in effects if e["case"] == "headway_2000" and e["metric"] == metric)
    assert effect["mean"] is None and effect["sample_standard_deviation"] is None
    assert effect["pairs"][1] == {"seed": 42, "difference": None}
    assert audit_factor_effects(report, effects)["factor_metric_checks"] == 28
