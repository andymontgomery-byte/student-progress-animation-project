#!/usr/bin/env python3
"""Take screenshots of the compare page to see what the user sees."""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'tests', 'screenshots')
PORT = 8768

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Start server
server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', str(PORT)],
    cwd=DOCS_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(1)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1400, 'height': 900})

        # Capture console messages
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"{msg.type}: {msg.text}"))

        print("Loading compare page...")
        page.goto(f"http://localhost:{PORT}/compare/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Screenshot 1: Initial load
        path1 = os.path.join(SCREENSHOT_DIR, "01_initial_load.png")
        page.screenshot(path=path1, full_page=True)
        print(f"Saved: {path1}")

        # Screenshot 2: After selecting a school filter
        print("Selecting school filter...")
        page.locator("#schoolFilter").select_option(index=1)
        time.sleep(0.5)
        path2 = os.path.join(SCREENSHOT_DIR, "02_school_filtered.png")
        page.screenshot(path=path2, full_page=True)
        print(f"Saved: {path2}")

        # Screenshot 3: After selecting student A
        print("Selecting student A...")
        page.locator("#studentSelectA").select_option(index=1)
        time.sleep(1)
        path3 = os.path.join(SCREENSHOT_DIR, "03_student_a_selected.png")
        page.screenshot(path=path3, full_page=True)
        print(f"Saved: {path3}")

        # Screenshot 4: After selecting student B
        print("Selecting student B...")
        page.locator("#studentSelectB").select_option(index=2)
        time.sleep(1)
        path4 = os.path.join(SCREENSHOT_DIR, "04_both_students.png")
        page.screenshot(path=path4, full_page=True)
        print(f"Saved: {path4}")

        print("\nConsole messages:")
        for msg in console_msgs:
            print(f"  {msg}")

        browser.close()

finally:
    server.terminate()
    server.wait()

print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
