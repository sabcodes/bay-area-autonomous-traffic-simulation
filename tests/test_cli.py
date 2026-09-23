import gzip
import json
import os
import subprocess
import sys
from pathlib import Path


def test_station_profile_command_exposes_freeway_and_direction_filters() -> None:
    environment = os.environ | {"PYTHONPATH": str(Path("src").resolve())}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bay_area_traffic_sim",
            "summarize-pems-stations",
            "--help",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert "--freeway" in result.stdout
    assert "--direction" in result.stdout


def test_station_profile_command_can_summarize_a_southbound_feeder(tmp_path: Path) -> None:
    source = tmp_path / "station_5min.txt.gz"
    with gzip.open(source, "wt", newline="") as destination:
        destination.write("10/09/2025 07:00:00,402920,4,85,S,OR,,20,100,50,,35\n")
    station_ids = tmp_path / "connector_station_ids.json"
    station_ids.write_text(json.dumps({"station_ids": [402920]}))
    output = tmp_path / "profile.json"
    environment = os.environ | {"PYTHONPATH": str(Path("src").resolve())}

    subprocess.run(
        [
            sys.executable,
            "-m",
            "bay_area_traffic_sim",
            "summarize-pems-stations",
            "--input-glob",
            "station_5min.txt.gz",
            "--station-ids-file",
            str(station_ids),
            "--freeway",
            "85",
            "--direction",
            "S",
            "--lane-types",
            "OR",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
        cwd=tmp_path,
    )

    report = json.loads(output.read_text())
    assert report["filter"]["freeway"] == 85
    assert report["filter"]["direction"] == "S"
    assert report["summary"]["matching_rows"] == 1
    assert report["summary"]["profiles"][0]["station_id"] == 402920
    assert report["summary"]["profiles"][0]["daily_time_profile"][0]["date"] == "2025-10-09"
