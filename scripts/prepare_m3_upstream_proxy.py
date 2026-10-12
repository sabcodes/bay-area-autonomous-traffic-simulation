"""Join a separately labeled 80%-coverage inlet proxy to the 90%-coverage M3 targets."""

from __future__ import annotations

import json

from bay_area_traffic_sim.pems import PemsFilter, summarize_station_profiles
from bay_area_traffic_sim.toy_corridor import repository_root


def main() -> None:
    root = repository_root()
    experiment = json.loads((root / "configs/us101_m3_experiment.json").read_text())
    dates = sorted(set(experiment["calibration_dates"] + experiment["validation_dates"]))
    files = [
        root / f"data/pems/d04_text_station_5min_{day.replace('-', '_')}.txt.gz" for day in dates
    ]
    boundary = summarize_station_profiles(
        files, PemsFilter(station_ids={400790}, minimum_observed_percent=80.0)
    ).as_dict()
    targets = json.loads(
        (root / "outputs/pems_calibration/us101_corridor_m1_station_profiles.json").read_text()
    )
    profiles = targets["summary"]["profiles"] + boundary["profiles"]
    report = {
        "filter": targets["filter"],
        "summary": {
            "profiles": profiles,
            "source_files": targets["summary"]["source_files"],
            "station_count": len(profiles),
            "matching_rows": sum(p["matching_rows"] for p in profiles),
        },
        "boundary_proxy": {
            "station_id": 400790,
            "minimum_observed_percent": 80,
            "source_scan": {k: v for k, v in boundary.items() if k != "profiles"},
            "role": "Input outside analysis corridor; never a scored target.",
        },
        "limitation": "Comparison targets retain 90% coverage. Station 400790 is an "
        "80%-coverage inlet proxy with estimated/imputed contribution and omitted upstream exits.",
    }
    output = root / "outputs/pems_calibration/us101_m3_upstream_proxy_profiles.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    for profile in boundary["profiles"]:
        print([(day["date"], len(day["time_profile"])) for day in profile["daily_time_profile"]])
    print(output)


if __name__ == "__main__":
    main()
