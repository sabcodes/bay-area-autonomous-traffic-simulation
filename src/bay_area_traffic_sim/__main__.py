"""Commands for running local traffic-simulation experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bay_area_traffic_sim.calibration import compare_detector_profiles
from bay_area_traffic_sim.experiments import repeat
from bay_area_traffic_sim.network_audit import audit_network
from bay_area_traffic_sim.osm_import import download_osm, import_osm, load_corridor_config
from bay_area_traffic_sim.pems import (
    PemsFilter,
    summarize_station_files,
    summarize_station_profiles,
)
from bay_area_traffic_sim.pems_metadata import load_station_ids, select_corridor_stations
from bay_area_traffic_sim.real_corridor import (
    prepare_human_baseline as prepare_real_human_baseline,
)
from bay_area_traffic_sim.real_corridor import run_human_baseline as run_real_human_baseline
from bay_area_traffic_sim.toy_corridor import (
    build_network,
    metrics_as_dict,
    run_cacc_sensitivity,
    run_human_baseline,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Bay Area traffic-simulation experiments.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("build-toy-network", help="Build the small starter freeway network.")
    baseline = subcommands.add_parser(
        "run-toy-baseline", help="Run the uncalibrated human-like toy freeway baseline."
    )
    baseline.add_argument("--seed", type=int, default=42, help="SUMO random seed (default: 42).")
    cacc = subcommands.add_parser(
        "run-toy-cacc", help="Run the deterministic CACC toy sensitivity scenario."
    )
    cacc.add_argument("--seed", type=int, default=42, help="SUMO random seed (default: 42).")
    compare = subcommands.add_parser(
        "compare-toy", help="Run the human and CACC toy scenarios across multiple seeds."
    )
    compare.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[41, 42, 43],
        help="One or more SUMO random seeds (default: 41 42 43).",
    )
    osm_import = subcommands.add_parser(
        "import-us101-osm", help="Convert a local OSM extract into a SUMO network for auditing."
    )
    osm_import.add_argument(
        "--config",
        type=str,
        default="configs/us101_corridor.json",
        help="Corridor import configuration (default: configs/us101_corridor.json).",
    )
    download = subcommands.add_parser(
        "download-us101-osm", help="Download a public OSM road extract and record its provenance."
    )
    download.add_argument(
        "--config",
        type=str,
        default="configs/us101_corridor.json",
        help="Corridor import configuration (default: configs/us101_corridor.json).",
    )
    calibrate = subcommands.add_parser(
        "summarize-pems",
        help="Summarize PeMS observations as an auditable, initial calibration target.",
    )
    calibrate.add_argument(
        "--input-glob",
        default="data/pems/d04_text_station_5min_*.txt.gz",
        help=(
            "PeMS Station 5-Minute input files "
            "(default: data/pems/d04_text_station_5min_*.txt.gz)."
        ),
    )
    calibrate.add_argument("--start-hour", type=int, default=7, help="Inclusive local hour.")
    calibrate.add_argument("--end-hour", type=int, default=9, help="Exclusive local hour.")
    calibrate.add_argument(
        "--minimum-observed-percent",
        type=float,
        default=90.0,
        help="Discard rows below this detector-observation percentage (default: 90).",
    )
    calibrate.add_argument(
        "--output",
        default="outputs/pems_calibration/us101_northbound_d4_morning_peak.json",
        help="JSON report path.",
    )
    calibrate.add_argument(
        "--station-ids-file",
        help="Optional JSON config/report containing the PeMS station_ids to retain.",
    )
    calibrate.add_argument(
        "--station-ids-key",
        default="station_ids",
        help=(
            "Name of the detector-ID list in --station-ids-file "
            "(default: station_ids)."
        ),
    )
    station_profiles = subcommands.add_parser(
        "summarize-pems-stations",
        help="Build separate five-minute profiles for selected PeMS stations.",
    )
    station_profiles.add_argument(
        "--input-glob",
        default="data/pems/d04_text_station_5min_*.txt.gz",
        help="PeMS Station 5-Minute input files.",
    )
    station_profiles.add_argument(
        "--station-ids-file",
        default="configs/us101_ramp_station_ids.json",
        help="JSON config containing selected station IDs.",
    )
    station_profiles.add_argument(
        "--station-ids-key",
        default="station_ids",
        help="Name of the detector-ID list in --station-ids-file.",
    )
    station_profiles.add_argument(
        "--lane-types",
        nargs="+",
        default=["OR", "FR"],
        help="PeMS lane types to retain (default: OR FR).",
    )
    station_profiles.add_argument("--start-hour", type=int, default=7)
    station_profiles.add_argument("--end-hour", type=int, default=9)
    station_profiles.add_argument(
        "--minimum-observed-percent", type=float, default=90.0
    )
    station_profiles.add_argument(
        "--output",
        default="outputs/pems_calibration/us101_ramp_station_profiles.json",
        help="JSON station-profile report path.",
    )
    select_stations = subcommands.add_parser(
        "select-us101-stations",
        help="Select US-101 northbound mainline PeMS stations inside the study boundary.",
    )
    select_stations.add_argument(
        "--metadata-glob",
        default="data/pems/metadata/d04_text_meta_*.txt",
        help="PeMS Station Metadata text files (default: data/pems/metadata/d04_text_meta_*.txt).",
    )
    select_stations.add_argument(
        "--config",
        default="configs/us101_corridor.json",
        help="Study-boundary configuration (default: configs/us101_corridor.json).",
    )
    select_stations.add_argument(
        "--output",
        default="outputs/pems_calibration/us101_corridor_station_selection.json",
        help="JSON selection report path.",
    )
    audit = subcommands.add_parser(
        "audit-us101-network",
        help="Match candidate PeMS stations to the draft SUMO network for manual audit.",
    )
    audit.add_argument(
        "--metadata-glob",
        default="data/pems/metadata/d04_text_meta_*.txt",
        help="PeMS Station Metadata text files (default: data/pems/metadata/d04_text_meta_*.txt).",
    )
    audit.add_argument(
        "--config",
        default="configs/us101_corridor.json",
        help="Study-boundary configuration (default: configs/us101_corridor.json).",
    )
    audit.add_argument(
        "--network",
        default="outputs/us101_corridor/us101_corridor.net.xml",
        help="Draft SUMO network path.",
    )
    audit.add_argument(
        "--output",
        default="outputs/us101_corridor/station_network_audit.json",
        help="JSON audit report path.",
    )
    prepare_real = subcommands.add_parser(
        "prepare-us101-human-baseline",
        help="Create the PeMS-driven draft human-only route and manifest.",
    )
    prepare_real.add_argument(
        "--config",
        default="configs/us101_human_baseline.json",
        help="Draft human baseline configuration.",
    )
    run_real = subcommands.add_parser(
        "run-us101-human-baseline",
        help="Run the PeMS-driven draft human-only scenario on the real network.",
    )
    run_real.add_argument(
        "--config",
        default="configs/us101_human_baseline.json",
        help="Draft human baseline configuration.",
    )
    run_real.add_argument("--seed", type=int, default=42, help="SUMO random seed (default: 42).")
    compare_detectors = subcommands.add_parser(
        "compare-us101-detectors",
        help="Compare observed PeMS station profiles with SUMO virtual detectors.",
    )
    compare_detectors.add_argument(
        "--observed",
        default="outputs/pems_calibration/us101_mainline_station_profiles.json",
    )
    compare_detectors.add_argument(
        "--simulated",
        default="outputs/us101_corridor/h0_virtual_detectors_seed_42.json",
    )
    compare_detectors.add_argument("--warmup-seconds", type=int, default=900)
    compare_detectors.add_argument(
        "--output",
        default="outputs/us101_corridor/h0_detector_comparison_seed_42.json",
    )
    args = parser.parse_args()

    if args.command == "build-toy-network":
        print(build_network())
    elif args.command == "run-toy-baseline":
        print(json.dumps(metrics_as_dict(run_human_baseline(args.seed)), indent=2))
    elif args.command == "run-toy-cacc":
        print(json.dumps(metrics_as_dict(run_cacc_sensitivity(args.seed)), indent=2))
    elif args.command == "compare-toy":
        human_runs, human_summary = repeat(run_human_baseline, args.seeds)
        cacc_runs, cacc_summary = repeat(run_cacc_sensitivity, args.seeds)
        print(
            json.dumps(
                {
                    "seeds": args.seeds,
                    "human_baseline": {
                        "runs": [metrics_as_dict(run) for run in human_runs],
                        "summary": human_summary,
                    },
                    "cacc_sensitivity": {
                        "runs": [metrics_as_dict(run) for run in cacc_runs],
                        "summary": cacc_summary,
                    },
                },
                indent=2,
            )
        )
    elif args.command == "import-us101-osm":
        print(import_osm(Path(args.config), Path("outputs/us101_corridor")))
    elif args.command == "download-us101-osm":
        source, provenance = download_osm(Path(args.config))
        print(json.dumps({"osm_source": str(source), "provenance": str(provenance)}, indent=2))
    elif args.command == "summarize-pems":
        station_ids = (
            load_station_ids(Path(args.station_ids_file), args.station_ids_key)
            if args.station_ids_file
            else None
        )
        criteria = PemsFilter(
            start_hour=args.start_hour,
            end_hour=args.end_hour,
            minimum_observed_percent=args.minimum_observed_percent,
            station_ids=station_ids,
        )
        summary = summarize_station_files(sorted(Path().glob(args.input_glob)), criteria)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        limitation = (
            "This uses a provisional manually reviewed detector subset. It excludes the two "
            "unresolved Moffett locations and newly added northern locations, so it is not yet "
            "a final calibration target."
            if args.station_ids_key == "provisionally_reviewed_station_ids"
            else (
                "This is an automatic candidate-corridor filter. Confirm selected stations and "
                "their ramp/interchange context during the manual network audit."
            )
            if args.station_ids_file
            else (
                "This is district-wide US-101 northbound data. Add PeMS station metadata "
                "before treating it as the SR-237 to Page Mill Road corridor."
            )
        )
        report = {
            "filter": {
                "district": criteria.district,
                "freeway": criteria.freeway,
                "direction": criteria.direction,
                "lane_type": criteria.lane_type,
                "start_hour": criteria.start_hour,
                "end_hour": criteria.end_hour,
                "minimum_observed_percent": criteria.minimum_observed_percent,
                "station_ids_file": args.station_ids_file,
                "station_ids_key": args.station_ids_key if args.station_ids_file else None,
                "station_id_count": len(criteria.station_ids) if criteria.station_ids else None,
            },
            "summary": summary.as_dict(),
            "limitation": limitation,
        }
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    elif args.command == "summarize-pems-stations":
        station_ids = load_station_ids(Path(args.station_ids_file), args.station_ids_key)
        criteria = PemsFilter(
            start_hour=args.start_hour,
            end_hour=args.end_hour,
            minimum_observed_percent=args.minimum_observed_percent,
            station_ids=station_ids,
            lane_types=set(args.lane_types),
        )
        summary = summarize_station_profiles(
            sorted(Path().glob(args.input_glob)), criteria
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "filter": {
                "start_hour": criteria.start_hour,
                "end_hour": criteria.end_hour,
                "minimum_observed_percent": criteria.minimum_observed_percent,
                "station_ids_file": args.station_ids_file,
                "station_ids_key": args.station_ids_key,
                "lane_types": sorted(criteria.lane_types or []),
            },
            "summary": summary.as_dict(),
            "limitation": (
                "These are observed ramp targets. SUMO ramp edges require manual audit before "
                "the profiles are used to inject or remove vehicles."
            ),
        }
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    elif args.command == "select-us101-stations":
        corridor = load_corridor_config(Path(args.config))
        selection = select_corridor_stations(
            sorted(Path().glob(args.metadata_glob)), corridor.bounding_box
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "corridor": corridor.name,
            "bounding_box": corridor.bounding_box,
            "selection": selection.as_dict(),
            "limitation": (
                "This is an automatic geographic filter. Confirm selected stations and their "
                "ramp/interchange context during the manual network audit."
            ),
        }
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    elif args.command == "audit-us101-network":
        corridor = load_corridor_config(Path(args.config))
        audit_result = audit_network(
            Path(args.network), sorted(Path().glob(args.metadata_glob)), corridor.bounding_box
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "corridor": corridor.name,
            "audit": audit_result.as_dict(),
            "limitation": (
                "Closest-edge matching does not prove a detector belongs to the desired route. "
                "Review ramps, collector-distributor roads, and complex interchanges manually."
            ),
        }
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    elif args.command == "prepare-us101-human-baseline":
        prepared = prepare_real_human_baseline(Path(args.config))
        print(json.dumps(prepared.as_dict(), indent=2))
    elif args.command == "run-us101-human-baseline":
        prepared, metrics, detector_summary_file = run_real_human_baseline(
            Path(args.config), args.seed
        )
        print(
            json.dumps(
                {
                    "scenario": prepared.scenario,
                    "seed": args.seed,
                    "expected_input_vehicles": prepared.expected_input_vehicles,
                    "metrics": metrics_as_dict(metrics),
                    "manifest_file": prepared.manifest_file,
                    "virtual_detector_summary_file": str(detector_summary_file),
                },
                indent=2,
            )
        )
    elif args.command == "compare-us101-detectors":
        report = compare_detector_profiles(
            Path(args.observed),
            Path(args.simulated),
            args.warmup_seconds,
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
