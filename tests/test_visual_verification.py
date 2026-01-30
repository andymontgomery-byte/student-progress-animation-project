#!/usr/bin/env python3
"""
Visual Verification Tests - Uses Claude's vision to verify screenshots.

This test suite:
1. Takes screenshots at every step
2. Saves them with descriptive names
3. Generates a verification manifest for Claude to review with vision

Run: python3 tests/test_visual_verification.py
Then: Claude reviews screenshots in tests/screenshots/verification/
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'tests', 'screenshots', 'verification')
MANIFEST_PATH = os.path.join(SCREENSHOT_DIR, 'verification_manifest.json')
PORT = 8773

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


class VisualVerificationSuite:
    """Test suite that captures screenshots for vision-based verification."""

    def __init__(self):
        self.screenshots = []
        self.timestamp = datetime.now().isoformat()

    def add_screenshot(self, path: str, description: str, verify: list):
        """Record a screenshot with verification requirements."""
        self.screenshots.append({
            "path": path,
            "description": description,
            "verify": verify,  # List of things to check visually
            "status": "pending"
        })

    def save_manifest(self):
        """Save the verification manifest for Claude to review."""
        manifest = {
            "timestamp": self.timestamp,
            "total_screenshots": len(self.screenshots),
            "screenshots": self.screenshots,
            "instructions": """
VISION VERIFICATION REQUIRED

For each screenshot, Claude must:
1. Read the image file using the Read tool
2. Verify ALL items in the 'verify' list
3. Mark status as 'pass' or 'fail' with details

A test only passes if VISUAL inspection confirms the UI renders correctly.
DOM checks are NOT sufficient - you must LOOK at the image.
"""
        }
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)
        return MANIFEST_PATH


def run_visual_capture():
    """Capture all screenshots needed for visual verification."""
    print("=" * 70)
    print("VISUAL VERIFICATION TEST SUITE")
    print("=" * 70)
    print()
    print("This captures screenshots for Claude to verify with vision.")
    print()

    suite = VisualVerificationSuite()

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
            # Test in multiple browsers
            browsers_to_test = [
                ("chromium", p.chromium),
                ("webkit", p.webkit),  # Safari engine
            ]

            for browser_name, browser_type in browsers_to_test:
                print(f"\n--- Testing in {browser_name} ---")
                browser = browser_type.launch(headless=True)

                # Main webapp tests
                capture_main_webapp(browser, suite, browser_name)

                # Strata webapp tests
                capture_strata_webapp(browser, suite, browser_name)

                # Compare webapp tests
                capture_compare_webapp(browser, suite, browser_name)

                browser.close()

    finally:
        server.terminate()
        server.wait()

    # Save manifest
    manifest_path = suite.save_manifest()

    print()
    print("=" * 70)
    print("SCREENSHOT CAPTURE COMPLETE")
    print("=" * 70)
    print(f"  Screenshots: {len(suite.screenshots)}")
    print(f"  Directory: {SCREENSHOT_DIR}")
    print(f"  Manifest: {manifest_path}")
    print()
    print("NEXT STEP: Claude must review each screenshot with vision.")
    print("Run: /verify-screenshots or have Claude read the manifest and images.")
    print()

    return suite


def capture_main_webapp(browser, suite, browser_name):
    """Capture main webapp screenshots."""
    page = browser.new_page(viewport={'width': 1200, 'height': 900})
    page.goto(f"http://localhost:{PORT}/")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # Initial state
    path = f"{SCREENSHOT_DIR}/{browser_name}_main_01_initial.png"
    page.screenshot(path=path)
    suite.add_screenshot(path, f"Main webapp initial state ({browser_name})", [
        "Page title is visible",
        "Student dropdown is visible and has a label",
        "Chart area is visible (may be empty initially)",
        "No visual glitches or overlapping elements"
    ])
    print(f"  Captured: {browser_name}_main_01_initial.png")

    # Get dropdown options
    dropdown = page.locator("select").first
    options = dropdown.locator("option").all_text_contents()
    num_students = len(options) - 1

    # Test 10 students (or all if fewer)
    test_count = min(10, num_students)
    for i in range(1, test_count + 1):
        dropdown.select_option(index=i)
        time.sleep(0.8)

        student_name = options[i].split(" - ")[0] if " - " in options[i] else f"student_{i}"
        student_name = student_name.replace(" ", "_")[:20]

        path = f"{SCREENSHOT_DIR}/{browser_name}_main_{i+1:02d}_{student_name}.png"
        page.screenshot(path=path)
        suite.add_screenshot(path, f"Main webapp with student {i} selected ({browser_name})", [
            f"Student dropdown shows '{options[i][:30]}...' as selected",
            "Chart displays data points (not empty)",
            "Percentile values are visible on chart (numbers like 46, 81, 95)",
            "Chart labels are readable (Fall, Winter, Spring)",
            "No blank areas where data should be"
        ])
        print(f"  Captured: {browser_name}_main_{i+1:02d}_{student_name}.png")

    page.close()


def capture_strata_webapp(browser, suite, browser_name):
    """Capture strata webapp screenshots."""
    page = browser.new_page(viewport={'width': 1200, 'height': 900})
    page.goto(f"http://localhost:{PORT}/strata/")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # Initial state
    path = f"{SCREENSHOT_DIR}/{browser_name}_strata_01_initial.png"
    page.screenshot(path=path)
    suite.add_screenshot(path, f"Strata webapp initial state ({browser_name})", [
        "Page title is visible",
        "Student dropdown is visible with label",
        "Layout is correct (no overlapping elements)"
    ])
    print(f"  Captured: {browser_name}_strata_01_initial.png")

    # Test students
    dropdown = page.locator("select").first
    options = dropdown.locator("option").all_text_contents()
    num_students = len(options) - 1

    test_count = min(10, num_students)
    for i in range(1, test_count + 1):
        dropdown.select_option(index=i)
        time.sleep(0.8)

        path = f"{SCREENSHOT_DIR}/{browser_name}_strata_{i+1:02d}.png"
        page.screenshot(path=path)
        suite.add_screenshot(path, f"Strata webapp with student {i} selected ({browser_name})", [
            "Student is selected in dropdown",
            "Chart/visualization updates with student data",
            "Data values are visible and readable"
        ])
        print(f"  Captured: {browser_name}_strata_{i+1:02d}.png")

    page.close()


def capture_compare_webapp(browser, suite, browser_name):
    """Capture compare webapp screenshots - the one that had the bug."""
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    page.goto(f"http://localhost:{PORT}/compare/")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # Initial state - CRITICAL: check filter dropdowns
    path = f"{SCREENSHOT_DIR}/{browser_name}_compare_01_initial.png"
    page.screenshot(path=path)
    suite.add_screenshot(path, f"Compare webapp initial state ({browser_name})", [
        "Page title is visible",
        "School filter dropdown is visible WITH READABLE LABELS (not blank)",
        "Subject filter dropdown is visible WITH READABLE LABELS",
        "Grade filter dropdown is visible WITH READABLE LABELS",
        "Student A dropdown is visible",
        "Student B dropdown is visible",
        "Student count shows a number (e.g., '490 students')",
        "NO BLANK CHECKBOXES - this was the Safari bug"
    ])
    print(f"  Captured: {browser_name}_compare_01_initial.png")

    # Open and screenshot each filter dropdown
    school_select = page.locator("#schoolFilter")
    subject_select = page.locator("#subjectFilter")
    grade_select = page.locator("#gradeFilter")

    # Test school filter - click to show options
    school_select.click()
    time.sleep(0.3)
    path = f"{SCREENSHOT_DIR}/{browser_name}_compare_02_school_dropdown.png"
    page.screenshot(path=path)
    suite.add_screenshot(path, f"Compare webapp school dropdown open ({browser_name})", [
        "Dropdown options are visible",
        "Each option has READABLE TEXT (not blank)",
        "Options include school names like 'Alpha Austin', 'Alpha Bluff', etc.",
        "NO BLANK CHECKBOXES OR EMPTY LABELS"
    ])
    print(f"  Captured: {browser_name}_compare_02_school_dropdown.png")

    # Select a school and verify filter works
    school_select.select_option(index=2)
    time.sleep(0.5)
    path = f"{SCREENSHOT_DIR}/{browser_name}_compare_03_school_filtered.png"
    page.screenshot(path=path)
    suite.add_screenshot(path, f"Compare webapp with school filter applied ({browser_name})", [
        "School dropdown shows selected school name (not blank)",
        "Student count has changed from initial (filter working)",
        "Student dropdowns updated with filtered list"
    ])
    print(f"  Captured: {browser_name}_compare_03_school_filtered.png")

    # Reset and test subject filter
    school_select.select_option(value="")
    time.sleep(0.3)
    subject_select.select_option(index=1)
    time.sleep(0.5)
    path = f"{SCREENSHOT_DIR}/{browser_name}_compare_04_subject_filtered.png"
    page.screenshot(path=path)
    suite.add_screenshot(path, f"Compare webapp with subject filter applied ({browser_name})", [
        "Subject dropdown shows selected subject (e.g., 'Reading')",
        "Student count reflects filter",
        "Filter is visually indicated as active"
    ])
    print(f"  Captured: {browser_name}_compare_04_subject_filtered.png")

    # Reset and test grade filter
    subject_select.select_option(value="")
    time.sleep(0.3)
    grade_select.select_option(index=1)
    time.sleep(0.5)
    path = f"{SCREENSHOT_DIR}/{browser_name}_compare_05_grade_filtered.png"
    page.screenshot(path=path)
    suite.add_screenshot(path, f"Compare webapp with grade filter applied ({browser_name})", [
        "Grade dropdown shows selected grade",
        "Student count reflects filter",
        "Filter combination is clear"
    ])
    print(f"  Captured: {browser_name}_compare_05_grade_filtered.png")

    # Test combined filters
    school_select.select_option(index=2)
    subject_select.select_option(index=2)
    time.sleep(0.5)
    path = f"{SCREENSHOT_DIR}/{browser_name}_compare_06_combined_filters.png"
    page.screenshot(path=path)
    suite.add_screenshot(path, f"Compare webapp with multiple filters ({browser_name})", [
        "All three filter dropdowns show their selections",
        "Student count reflects combined filter",
        "No visual glitches from filter combination"
    ])
    print(f"  Captured: {browser_name}_compare_06_combined_filters.png")

    # Select students and verify charts
    student_a = page.locator("#studentSelectA")
    student_b = page.locator("#studentSelectB")

    opts = student_a.locator("option").all_text_contents()
    if len(opts) > 2:
        student_a.select_option(index=1)
        time.sleep(0.5)
        student_b.select_option(index=2)
        time.sleep(0.5)

        path = f"{SCREENSHOT_DIR}/{browser_name}_compare_07_students_selected.png"
        page.screenshot(path=path)
        suite.add_screenshot(path, f"Compare webapp with both students selected ({browser_name})", [
            "Student A dropdown shows selected student name",
            "Student B dropdown shows selected student name",
            "Left chart shows Student A data with visible data points",
            "Right chart shows Student B data with visible data points",
            "Charts have labels and percentile values visible"
        ])
        print(f"  Captured: {browser_name}_compare_07_students_selected.png")

    # Test 10 different student pairs
    grade_select.select_option(value="")
    school_select.select_option(value="")
    subject_select.select_option(value="")
    time.sleep(0.5)

    student_a = page.locator("#studentSelectA")
    opts = student_a.locator("option").all_text_contents()

    for i in range(min(5, (len(opts) - 1) // 2)):
        idx_a = i * 2 + 1
        idx_b = i * 2 + 2
        if idx_b >= len(opts):
            break

        student_a.select_option(index=idx_a)
        time.sleep(0.3)
        student_b.select_option(index=idx_b)
        time.sleep(0.5)

        path = f"{SCREENSHOT_DIR}/{browser_name}_compare_pair_{i+1:02d}.png"
        page.screenshot(path=path)
        suite.add_screenshot(path, f"Compare webapp student pair {i+1} ({browser_name})", [
            "Both student names are visible in dropdowns",
            "Both charts display data",
            "Percentile values are readable on both charts"
        ])
        print(f"  Captured: {browser_name}_compare_pair_{i+1:02d}.png")

    page.close()


def verify_screenshots_with_vision():
    """
    This function is called by Claude to verify screenshots.
    Claude reads each screenshot image and checks the verification items.
    """
    if not os.path.exists(MANIFEST_PATH):
        print("No manifest found. Run capture first.")
        return False

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    print("=" * 70)
    print("VISION VERIFICATION CHECKLIST")
    print("=" * 70)
    print()
    print("Claude must READ each image file and verify the items listed.")
    print()

    for i, screenshot in enumerate(manifest['screenshots']):
        print(f"\n--- Screenshot {i+1}/{len(manifest['screenshots'])} ---")
        print(f"Path: {screenshot['path']}")
        print(f"Description: {screenshot['description']}")
        print("Verify:")
        for item in screenshot['verify']:
            print(f"  [ ] {item}")

    print()
    print("=" * 70)
    print("Claude: Read each .png file and mark pass/fail for each item.")
    print("=" * 70)

    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_screenshots_with_vision()
    else:
        run_visual_capture()
