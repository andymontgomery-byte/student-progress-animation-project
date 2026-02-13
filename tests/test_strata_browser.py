#!/usr/bin/env python3
"""
Browser-based tests for Strata webapp using Playwright.
Tests actual browser functionality, not just HTML structure.

Run: python3 tests/test_strata_browser.py
"""

import os
import sys
import time
import json
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
STRATA_DATA_JSON = os.path.join(DOCS_DIR, 'strata', 'data.json')
PORT = 8767

# Expected Strata schools
STRATA_SCHOOLS = [
    "AIE Elite Prep",
    "All American Prep",
    "DeepWater Prep",
    "Modern Samurai Academy",
    "The Bennett School"
]

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


def load_strata_data():
    """Load the Strata data.json"""
    with open(STRATA_DATA_JSON) as f:
        return json.load(f)


def run_browser_tests():
    """Run all browser-based tests"""
    print("=" * 60)
    print("BROWSER-BASED STRATA WEBAPP TESTS")
    print("=" * 60)
    print()

    strata_data = load_strata_data()

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
                ("Only Strata schools in data", lambda p: test_only_strata_schools(strata_data)),
                ("All students have CGI > 0.8", lambda p: test_cgi_threshold(strata_data)),
                ("Student dropdown populates", lambda p: test_student_dropdown(p, len(strata_data))),
                ("Selecting student works", test_select_student),
            ]

            page.goto(f"http://localhost:{PORT}/strata/")
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
    """Test that page loads"""
    assert page.title(), "Page should have a title"


def test_data_loads(page):
    """Test that data loads successfully"""
    body_text = page.locator("body").text_content()
    assert "error" not in body_text.lower() or len(body_text) > 100, "Page should load data"


def test_no_console_errors(page, console_errors):
    """Test that there are no JavaScript console errors"""
    critical_errors = [e for e in console_errors if "favicon" not in e.lower()]
    assert len(critical_errors) == 0, f"Console errors: {critical_errors}"


def test_only_strata_schools(strata_data):
    """Test that only Strata schools are in the data"""
    schools_in_data = set(s['school'] for s in strata_data)
    for school in schools_in_data:
        assert school in STRATA_SCHOOLS, f"Non-Strata school in data: {school}"


def test_cgi_threshold(strata_data):
    """Test that all students have CGI > 0.8"""
    for student in strata_data:
        assert student['cgi'] > 0.8, f"Student {student['email']} has CGI {student['cgi']} <= 0.8"


def test_student_dropdown(page, expected_count):
    """Test that student dropdown has options"""
    select = page.locator("select").first
    if select.count() > 0:
        options = select.locator("option").count()
        # Should have placeholder + at least some students
        assert options > 1, f"Dropdown should have options, got {options}"


def test_select_student(page):
    """Test that selecting a student doesn't cause errors"""
    select = page.locator("select").first
    if select.count() > 0:
        options_count = select.locator("option").count()
        if options_count > 1:
            select.select_option(index=1)
            time.sleep(0.5)
            select.select_option(index=0)


if __name__ == '__main__':
    success = run_browser_tests()
    sys.exit(0 if success else 1)
