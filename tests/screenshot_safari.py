#!/usr/bin/env python3
"""Screenshot using WebKit (Safari engine)."""

import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')

with sync_playwright() as p:
    browser = p.webkit.launch(headless=True)  # Safari engine
    page = browser.new_page(viewport={'width': 1400, 'height': 900})

    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(f"{msg.type}: {msg.text}"))

    print("Loading with WebKit (Safari)...")
    page.goto("https://andymontgomery-byte.github.io/student-progress-animation-project/compare/")
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    path = os.path.join(SCREENSHOT_DIR, "safari_initial.png")
    page.screenshot(path=path, full_page=True)
    print(f"Saved: {path}")

    page.locator("#studentSelectA").select_option(index=1)
    time.sleep(1)
    path2 = os.path.join(SCREENSHOT_DIR, "safari_student_selected.png")
    page.screenshot(path=path2, full_page=True)
    print(f"Saved: {path2}")

    print("\nConsole messages:")
    for msg in console_msgs:
        print(f"  {msg}")

    browser.close()
