"""Capture dashboard screenshots from a running Streamlit server.

Usage:
    python scripts/capture_screenshots.py --url http://127.0.0.1:8510
"""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8510")
    parser.add_argument("--chrome", default=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    args = parser.parse_args()
    ASSETS.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=args.chrome,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1080}, device_scale_factor=1)
        errors: list[str] = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(args.url, wait_until="domcontentloaded", timeout=120000)
        page.wait_for_selector("text=Every review", timeout=120000)
        page.wait_for_timeout(15000)
        page.screenshot(path=str(ASSETS / "dashboard_top.png"))
        page.locator(".verdict-card").scroll_into_view_if_needed()
        page.wait_for_timeout(900)
        page.screenshot(path=str(ASSETS / "verdict.png"))

        tabs = page.get_by_role("tab")
        print("tabs:", tabs.all_inner_texts())
        page.locator("div[data-testid='stTabs']").scroll_into_view_if_needed()
        page.wait_for_timeout(800)
        page.screenshot(path=str(ASSETS / "overview_top.png"))

        for name, filename, wait_ms in [
            ("Overview", "tab_overview.png", 1200),
            ("Model comparison", "tab_models.png", 1400),
            ("Language lab", "tab_language.png", 2800),
            ("Corpus", "tab_corpus.png", 1200),
        ]:
            page.get_by_role("tab", name=name).click()
            page.wait_for_timeout(wait_ms)
            page.locator("div[data-testid='stTabs']").scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            page.screenshot(path=str(ASSETS / filename))
            print("saved", filename)

        # Verify that choosing another fixed film updates the dashboard.
        page.locator("[data-testid='stButtonGroup'] button").filter(has_text="Cats").click()
        page.wait_for_timeout(15000)
        page.get_by_role("tab", name="Overview").click()
        page.wait_for_timeout(700)
        page.locator(".verdict-card").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=str(ASSETS / "dashboard_cats.png"))
        print("saved dashboard_cats.png")
        print("cats visible:", "Cats" in page.inner_text("body"))

        page.screenshot(path=str(ASSETS / "dashboard_full.png"), full_page=True)
        print("console errors:", errors[:5])

        mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        mobile.goto(args.url, wait_until="domcontentloaded", timeout=120000)
        mobile.wait_for_selector("text=Every review", timeout=120000)
        mobile.wait_for_timeout(10000)
        mobile.screenshot(path=str(ASSETS / "dashboard_mobile.png"))
        print("saved dashboard_mobile.png")
        browser.close()


if __name__ == "__main__":
    main()
