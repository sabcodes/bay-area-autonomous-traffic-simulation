"""M8 saved-evidence contracts, malformed populations and package integrity."""

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("m8", ROOT / "scripts/build_m8_package.py")
m8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m8)


@pytest.fixture
def evidence(tmp_path):
    paths = [
        "reports/m7/report.json",
        "reports/m7/independent_audit.json",
        "configs/us101_m7_sensitivity.json",
        "configs/us101_human_baseline_m3_frozen.json",
        "reports/m3/calibration_report.json",
        "reports/m3/validation_report.json",
        "reports/m3/freeze.json",
    ]
    paths += list(m8.read(ROOT, "reports/m7/independent_audit.json")["source_sha256"])
    for name in paths:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return tmp_path


def save(root, name, value):
    (root / name).write_text(json.dumps(value))


def update_report(root, mutate):
    report = m8.read(root, "reports/m7/report.json")
    mutate(report)
    save(root, "reports/m7/report.json", report)
    audit = m8.read(root, "reports/m7/independent_audit.json")
    audit["report_sha256"] = m8.sha(root / "reports/m7/report.json")
    save(root, "reports/m7/independent_audit.json", audit)


def test_actual_results_and_exact_seed_denominator():
    data = m8.headline_results(ROOT)
    assert len(data["m7_paired_metrics"]) == 52
    central = next(
        r
        for r in data["m7_paired_metrics"]
        if r["case"] == "base"
        and r["scenario"] == "CENTRAL"
        and r["metric"] == next(iter(m8.METRICS))
    )
    assert central["mean"] == pytest.approx(43.2)
    assert central["sample_standard_deviation"] == pytest.approx(91.49767756615573)
    assert central["h0_mean"] == 8266
    subset = next(r for r in data["m7_paired_metrics"] if r["case"] == "range_050")
    assert subset["h0_mean"] == 8274.5
    validation = data["m3_scores"][-3:]
    assert [r["mean_station_flow_mape_percent"] for r in validation] == pytest.approx(
        [29.95478496716808, 8.793262950283607, 19.374023958725843]
    )
    assert validation[-1]["mean_station_speed_mae_mph"] == pytest.approx(14.904101819627746)
    for record in data["m7_paired_metrics"]:
        if record["case"] == "penetration_000" or (
            record["case"] == "demand_080" and record["scenario"] == "CENTRAL"
        ):
            assert record["mean"] == record["sample_standard_deviation"] == 0


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r["runs"].pop(),
        lambda r: r["runs"].append(r["runs"][0]),
        lambda r: r["runs"][0].update(accepted=False),
        lambda r: r["runs"][0].update(date="2025-10-16"),
        lambda r: r["groups"].pop(),
        lambda r: r["groups"].append(r["groups"][0]),
        lambda r: r.update(complete=False),
    ],
)
def test_rejects_incomplete_or_incorrect_population(evidence, mutation):
    update_report(evidence, mutation)
    with pytest.raises(ValueError):
        m8.headline_results(evidence)
    assert not (evidence / "reports/m8").exists()


@pytest.mark.parametrize("value", [None, True, "1", float("nan"), float("inf"), float("-inf")])
def test_rejects_nonfinite_and_nonnumeric_metrics(evidence, value):
    update_report(
        evidence, lambda r: r["runs"][0]["metrics"].update({next(iter(m8.METRICS)): value})
    )
    with pytest.raises(ValueError):
        m8.headline_results(evidence)


def test_rejects_incorrect_saved_aggregate(evidence):
    def mutate(report):
        group = next(g for g in report["groups"] if g["scenario"] == "CACC")
        group["paired_metrics"][next(iter(m8.METRICS))]["mean"] += 1

    update_report(evidence, mutate)
    with pytest.raises(ValueError, match="Statistic mismatch"):
        m8.headline_results(evidence)


def test_rejects_unbound_audit_or_changed_simulator(evidence):
    audit = m8.read(evidence, "reports/m7/independent_audit.json")
    audit["report_sha256"] = "wrong"
    save(evidence, "reports/m7/independent_audit.json", audit)
    with pytest.raises(ValueError, match="Audit/report"):
        m8.headline_results(evidence)
    shutil.copyfile(
        ROOT / "reports/m7/independent_audit.json", evidence / "reports/m7/independent_audit.json"
    )
    source = evidence / next(iter(audit["source_sha256"]))
    source.write_text("changed")
    with pytest.raises(ValueError, match="Frozen simulator changed"):
        m8.headline_results(evidence)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r["runs"].pop(),
        lambda r: r["runs"][0].update(treatment_sha256="wrong"),
        lambda r: r["runs"][0].update(clean_and_cleared=False),
        lambda r: r["runs"][0]["station_comparisons"].pop(0),
        lambda r: r["summary"][0].update(mean_station_flow_mape_percent=0),
    ],
)
def test_rejects_m3_population_score_or_freeze_changes(evidence, mutation):
    data = m8.read(evidence, "reports/m3/validation_report.json")
    mutation(data)
    save(evidence, "reports/m3/validation_report.json", data)
    with pytest.raises(ValueError):
        m8.headline_results(evidence)


def test_manifest_tamper_missing_artifact_and_read_only_check(evidence):
    subprocess.run(["git", "init", "-q", str(evidence)], check=True)
    (evidence / "docs").mkdir()
    doc = evidence / "docs/methods.md"
    doc.write_text("Frozen methods\n")
    subprocess.run(["git", "add", "."], cwd=evidence, check=True)
    m8.package(evidence)
    outputs = [evidence / p for p in (*m8.OUTPUTS, "reports/m8/manifest.json")]
    original = [(p.read_bytes(), p.stat().st_mtime_ns) for p in outputs]
    m8.package(evidence, check=True)
    assert original == [(p.read_bytes(), p.stat().st_mtime_ns) for p in outputs]
    m8.package(evidence)
    assert [b for b, _ in original] == [p.read_bytes() for p in outputs]
    doc.write_text("Tampered methods\n")
    with pytest.raises(ValueError, match="Stale package artifact"):
        m8.package(evidence, check=True)
    doc.unlink()
    with pytest.raises(FileNotFoundError):
        m8.package(evidence, check=True)
    doc.write_text("Frozen methods\n")
    outputs[0].unlink()
    with pytest.raises(FileNotFoundError):
        m8.package(evidence, check=True)


def test_missing_and_mismatched_local_prerequisites(evidence):
    with pytest.raises(ValueError, match="Missing:"):
        m8.local_inputs(evidence)
    path = evidence / "configs/fixture.json"
    path.write_text("original")
    save(
        evidence,
        "configs/us101_human_baseline_m3_frozen.json",
        {"expected_input_sha256": {"configs/fixture.json": m8.sha(path)}},
    )
    assert m8.local_inputs(evidence) == 1
    path.write_text("changed")
    with pytest.raises(ValueError, match="Hash mismatch:"):
        m8.local_inputs(evidence)


def test_final_report_headline_table_matches_computed_data():
    data = m8.headline_results(ROOT)
    report = (ROOT / "docs/final-research-report.md").read_text()
    for policy in ("CACC", "CENTRAL"):
        rows = [
            r for r in data["m7_paired_metrics"] if r["case"] == "base" and r["scenario"] == policy
        ]
        expected = (
            f"| {policy} | 5 | "
            + " | ".join(f"{r['percent_of_reference_mean']:+.3f}%" for r in rows)
            + " |"
        )
        assert expected in report
