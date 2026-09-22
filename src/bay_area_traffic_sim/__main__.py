"""Commands for running local traffic-simulation experiments."""

from __future__ import annotations

import argparse
import json

from bay_area_traffic_sim.toy_corridor import build_network, metrics_as_dict, run_human_baseline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Bay Area traffic-simulation experiments.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("build-toy-network", help="Build the small starter freeway network.")
    baseline = subcommands.add_parser(
        "run-toy-baseline", help="Run the uncalibrated human-like toy freeway baseline."
    )
    baseline.add_argument("--seed", type=int, default=42, help="SUMO random seed (default: 42).")
    args = parser.parse_args()

    if args.command == "build-toy-network":
        print(build_network())
    elif args.command == "run-toy-baseline":
        print(json.dumps(metrics_as_dict(run_human_baseline(args.seed)), indent=2))


if __name__ == "__main__":
    main()
