#!/usr/bin/env python3
"""
Screenshot a local HTML file at desktop, tablet, and mobile viewports.

For each viewport, captures:
  - a "viewport" shot (just what's visible above the fold)
  - a "fullpage" shot (the entire scrollable page)

Usage:
    python screenshot.py path/to/page.html [output_dir]

Requires:
    pip install playwright
    playwright install chromium
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "tablet": {"width": 820, "height": 1180},
    "mobile": {"width": 390, "height": 844},
}

# Extra pause after networkidle to let CSS animations/transitions settle
ANIMATION_SETTLE_MS = 800


def screenshot_page(html_path: Path, output_dir: Path) -> None:
    file_url = html_path.resolve().as_uri()
    page_name = html_path.stem

    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for device_name, viewport in VIEWPORTS.items():
                page = browser.new_page(viewport=viewport)
                page.goto(file_url, wait_until="load")
                try:
                    # Best-effort: settles faster on simple pages. Pages with
                    # live third-party embeds (e.g. Spotify iframes) keep
                    # network activity going and will never truly idle, so
                    # don't let that block the screenshot.
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
                page.wait_for_timeout(ANIMATION_SETTLE_MS)

                viewport_path = output_dir / f"{page_name}-{device_name}-viewport.png"
                page.screenshot(path=str(viewport_path))
                print(f"Saved {viewport_path}")

                fullpage_path = output_dir / f"{page_name}-{device_name}-fullpage.png"
                page.screenshot(path=str(fullpage_path), full_page=True)
                print(f"Saved {fullpage_path}")

                page.close()
        finally:
            browser.close()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python screenshot.py path/to/page.html [output_dir]")
        sys.exit(1)

    html_path = Path(sys.argv[1])
    if not html_path.is_file():
        print(f"File not found: {html_path}")
        sys.exit(1)

    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("screenshots")
    screenshot_page(html_path, output_dir)


if __name__ == "__main__":
    main()
