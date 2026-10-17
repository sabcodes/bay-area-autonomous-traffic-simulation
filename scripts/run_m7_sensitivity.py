"""Run the frozen M7 sensitivity campaign; preserve all failures and inactive controls."""

import argparse
from pathlib import Path

from bay_area_traffic_sim.sensitivity import run_campaign

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/us101_m7_sensitivity.json"))
    args = parser.parse_args()
    result = run_campaign(args.config)
    print(
        f"M7 complete={result['complete']}, "
        f"accepted={sum(r['accepted'] for r in result['runs'])}/{len(result['runs'])}"
    )
