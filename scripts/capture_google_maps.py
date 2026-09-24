"""Capture a dated Google Maps satellite view for a manual network audit.

Screenshots are local research notes, not source data or proof of lane count.
Keep them under ignored outputs/ rather than committing third-party imagery.
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument("--zoom", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not -90 <= args.latitude <= 90 or not -180 <= args.longitude <= 180:
        parser.error("latitude or longitude is outside its valid range")
    if not 1 <= args.zoom <= 22:
        parser.error("zoom must be between 1 and 22")
    if args.output.suffix.lower() != ".png":
        parser.error("output must be a .png file")

    url = (
        f"https://www.google.com/maps/@{args.latitude:.7f},"
        f"{args.longitude:.7f},{args.zoom}z/data=!3m1!1e3"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        try:
            page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(8000)
            page.screenshot(path=str(args.output), full_page=False)
            metadata = {
                "captured_at_utc": datetime.now(UTC).isoformat(),
                "requested_url": url,
                "final_url": page.url,
                "page_title": page.title(),
                "latitude": args.latitude,
                "longitude": args.longitude,
                "zoom": args.zoom,
                "note": "Aerial imagery is visual context, not a surveyed lane count.",
            }
            args.output.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
            print(json.dumps({"screenshot": str(args.output), **metadata}, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
