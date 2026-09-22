"""Commands for running local traffic-simulation experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bay_area_traffic_sim.experiments import repeat
from bay_area_traffic_sim.osm_import import download_osm, import_osm
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


if __name__ == "__main__":
    main()
