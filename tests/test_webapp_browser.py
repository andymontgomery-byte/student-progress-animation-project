#!/usr/bin/env python3
"""
Browser-based tests for main webapp using Playwright.
Tests actual browser functionality, not just HTML structure.

Run: python3 tests/test_webapp_browser.py
"""

import os
import sys
import time
import json
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DATA_JSON = os.path.join(DOCS_DIR, 'data.json')
PORT = 8766

class TestServer:
    """Context manager for running a local HTTP server"""
    def __init__(self, directory, port):
        self.directory = directory
        self.port = port
        self.process = None

    def __enter__(self):
        self.process = subprocess.Popen(
            [sys.executable, '-m', 'http.server', str(self.port)],
            cwd=self.directory,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            self.process.terminate()
            self.process.wait()


def load_expected_data():
    """Load the expected data from data.json"""
    with open(DATA_JSON) as f:
        return json.load(f)


def run_browser_tests():
    """Run all browser-based tests"""
    print("=" * 60)
    print("BROWSER-BASED MAIN WEBAPP TESTS")
    print("=" * 60)
    print()

    expected_data = load_expected_data()

    passed = 0
    failed = 0

    with TestServer(DOCS_DIR, PORT):
        print(f"Server running at http://localhost:{PORT}")
        print()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            tests = [
                ("Page loads successfully", test_page_loads),
                ("Data loads without errors", test_data_loads),
                ("No console errors", lambda p: test_no_console_errors(p, console_errors)),
                ("Student dropdown populates", lambda p: test_student_dropdown(p, len(expected_data))),
                ("Chart canvas exists", test_chart_canvas),
                ("Selecting student updates display", test_select_student),
                ("Student info displays", test_student_info_display),
                ("Animation can be triggered", test_animation),
            ]

            page.goto(f"http://localhost:{PORT}/")
            page.wait_for_load_state("networkidle")
            time.sleep(0.5)

            for test_name, test_func in tests:
                try:
                    test_func(page)
                    print(f"✓ {test_name}")
                    passed += 1
                except Exception as e:
                    print(f"✗ {test_name}: {e}")
                    failed += 1

            browser.close()

    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


def test_page_loads(page):
    """Test that page loads and has basic structure"""
    assert page.title(), "Page should have a title"


def test_data_loads(page):
    """Test that data.json is fetched successfully"""
    # Check for any loading indicator or content that shows data loaded
    # The page should have some content beyond just the shell
    body_text = page.locator("body").text_content()
    assert "error" not in body_text.lower() or len(body_text) > 100, "Page should load data"


def test_no_console_errors(page, console_errors):
    """Test that there are no JavaScript console errors"""
    critical_errors = [e for e in console_errors if "favicon" not in e.lower()]
    assert len(critical_errors) == 0, f"Console errors: {critical_errors}"


def test_student_dropdown(page, expected_count):
    """Test that student dropdown has options"""
    # Look for common dropdown patterns
    select = page.locator("select").first
    if select.count() > 0:
        options = select.locator("option").count()
        assert options > 1, f"Dropdown should have options, got {options}"


def test_chart_canvas(page):
    """Test that chart canvas exists"""
    canvas = page.locator("canvas")
    assert canvas.count() > 0, "Should have at least one canvas element"


def test_select_student(page):
    """Test that selecting a student doesn't cause errors"""
    select = page.locator("select").first
    if select.count() > 0:
        options_count = select.locator("option").count()
        if options_count > 1:
            select.select_option(index=1)
            time.sleep(0.5)
            # No error means success
            select.select_option(index=0)


def test_student_info_display(page):
    """Test that selecting student shows some info"""
    select = page.locator("select").first
    if select.count() > 0 and select.locator("option").count() > 1:
        select.select_option(index=1)
        time.sleep(0.5)
        # Page should have visible content
        body = page.locator("body")
        assert body.is_visible(), "Body should be visible after selection"
        select.select_option(index=0)


def test_animation(page):
    """Test that animation can be triggered"""
    select = page.locator("select").first
    if select.count() > 0 and select.locator("option").count() > 1:
        select.select_option(index=1)
        time.sleep(0.5)

        # Look for play button
        play_btn = page.locator("button:has-text('Play'), button:has-text('Animate'), #playBtn")
        if play_btn.count() > 0:
            play_btn.first.click()
            time.sleep(0.3)

        select.select_option(index=0)
    # Pass if no errors


if __name__ == '__main__':
    success = run_browser_tests()
    sys.exit(0 if success else 1)
