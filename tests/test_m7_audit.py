"""Presentation contrasts must pass a separate implementation's checks."""

from copy import deepcopy

import pytest

from bay_area_traffic_sim.toy_corridor import repository_root


def test_factor_contrast_audit_rejects_wrong_means_missing_pairs_and_failed_seed(monkeypatch):
    monkeypatch.syspath_prepend(str(repository_root() / "scripts"))
    from audit_m7_results import audit_factor_effects

    metrics = [
        "network_exit_throughput_vehicles_per_hour",
        "scheduled_cohort_mean_total_time_seconds",
        "rms_acceleration_m_per_s2",
        "peak_insertion_backlog_vehicles",
    ]
    report = {
        "campaign": {
            "cases": [
                {"id": "base", "policies": {"CACC": {}}, "seeds": [41, 42]},
                {"id": "half", "policies": {"CACC": {}}, "seeds": [41, 42]},
            ]
        },
        "runs": [
            {
                "case": case,
                "scenario": "CACC",
                "seed": seed,
                "accepted": True,
                "metrics": dict.fromkeys(metrics, value),
            }
            for case, seed, value in [
                ("base", 41, 10),
                ("base", 42, 20),
                ("half", 41, 12),
                ("half", 42, 24),
            ]
        ],
    }
    effects = [
        {
            "case": "half",
            "scenario": "CACC",
            "metric": metric,
            "pairs": [{"seed": 41, "difference": 2}, {"seed": 42, "difference": 4}],
            "mean": 3,
            "sample_standard_deviation": 2**0.5,
        }
        for metric in metrics
    ]
    assert audit_factor_effects(report, effects) == {"accepted": True, "factor_metric_checks": 4}
    for mode in ["wrong_mean", "missing_pair", "failed_seed"]:
        bad_report, bad_effects = deepcopy(report), deepcopy(effects)
        if mode == "wrong_mean":
            bad_effects[0]["mean"] = 100
        elif mode == "missing_pair":
            bad_effects[0]["pairs"].pop()
        else:
            bad_report["runs"][-1]["accepted"] = False
        with pytest.raises(AssertionError):
            audit_factor_effects(bad_report, bad_effects)


def test_raw_audit_cache_invalidates_on_evidence_run_or_auditor_change(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(repository_root() / "scripts"))
    import audit_m7_results as auditor

    folder = tmp_path / "run"
    folder.mkdir()
    (tmp_path / "scripts").mkdir()
    dependency = tmp_path / "scripts/audit_m6_results.py"
    dependency.write_text("first auditor version")
    raw = folder / "trips.xml"
    raw.write_text("original raw data")
    calls = []

    def calculate(job):
        calls.append(job)
        return {"raw_metric_checks": 30}, {"vehicle": ["passenger", 1.0, 900]}

    monkeypatch.setattr(auditor, "_audit_run", calculate)
    run = {"directory": "run", "metrics": {"example": 10}}
    expected = auditor.audit_run((tmp_path, run))
    assert auditor.audit_run((tmp_path, run)) == expected and len(calls) == 1
    raw.write_text("changed raw data")
    auditor.audit_run((tmp_path, run))
    assert len(calls) == 2
    run["metrics"]["example"] = 20
    auditor.audit_run((tmp_path, run))
    assert len(calls) == 3
    dependency.write_text("new auditor version")
    auditor.audit_run((tmp_path, run))
    assert len(calls) == 4
