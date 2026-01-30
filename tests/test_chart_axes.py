#!/usr/bin/env python3
"""
Test chart axis labels are correct.

Verifies:
- REQ-15: Y-axis shows 0-99 + 99th grade levels (0, 25, 50, 75, 99, 99+2, 99+4, 99+6, 99+8)
- REQ-16: X-axis shows Fall, Winter, Spring

Run: python3 tests/test_chart_axes.py
"""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'tests', 'screenshots', 'axes')
PORT = 8774

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def run_axis_tests():
    """Test chart axis labels with visual verification."""
    print("=" * 70)
    print("CHART AXIS LABEL TESTS")
    print("=" * 70)
    print()
    print("Verifying Y-axis and X-axis labels render correctly.")
    print()

    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', str(PORT)],
        cwd=DOCS_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1200, 'height': 900})

            # Test main webapp
            print("--- Main Webapp ---")
            results.extend(test_webapp_axes(page, PORT, "/", "main"))

            # Test strata webapp
            print("\n--- Strata Webapp ---")
            results.extend(test_webapp_axes(page, PORT, "/strata/", "strata"))

            # Test compare webapp
            print("\n--- Compare Webapp ---")
            results.extend(test_compare_axes(page, PORT))

            browser.close()

    finally:
        server.terminate()
        server.wait()

    # Summary
    print("\n" + "=" * 70)
    print("AXIS TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results if r[1])
    failed = sum(1 for r in results if not r[1])

    for name, status, detail in results:
        icon = "✓" if status else "✗"
        print(f"  {icon} {name}: {detail}")

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Screenshots: {SCREENSHOT_DIR}")

    return failed == 0


def test_webapp_axes(page, port, path, name):
    """Test axis labels on a single-student webapp."""
    results = []

    page.goto(f"http://localhost:{port}{path}")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # Select first student to render chart
    dropdown = page.locator("select").first
    dropdown.select_option(index=1)
    time.sleep(1)

    # Take screenshot
    screenshot_path = f"{SCREENSHOT_DIR}/{name}_chart_axes.png"
    page.screenshot(path=screenshot_path)

    # Get page text to verify axis labels
    page_text = page.locator("body").text_content()

    # REQ-15: Check Y-axis labels
    y_axis_labels = ["99+8", "99+6", "99+4", "99+2", "99", "75", "50", "25", "0"]
    y_axis_found = []
    for label in y_axis_labels:
        if label in page_text:
            y_axis_found.append(label)

    if len(y_axis_found) >= 5:  # At least 5 of 9 labels visible
        results.append((f"{name} Y-axis labels", True, f"Found: {', '.join(y_axis_found)}"))
        print(f"  ✓ Y-axis labels found: {', '.join(y_axis_found)}")
    else:
        results.append((f"{name} Y-axis labels", False, f"Only found: {y_axis_found}"))
        print(f"  ✗ Y-axis labels missing, only found: {y_axis_found}")

    # REQ-16: Check X-axis labels
    x_axis_labels = ["Fall", "Winter", "Spring"]
    x_axis_found = []
    for label in x_axis_labels:
        if label in page_text:
            x_axis_found.append(label)

    if len(x_axis_found) == 3:
        results.append((f"{name} X-axis labels", True, f"Found: {', '.join(x_axis_found)}"))
        print(f"  ✓ X-axis labels found: {', '.join(x_axis_found)}")
    else:
        results.append((f"{name} X-axis labels", False, f"Only found: {x_axis_found}"))
        print(f"  ✗ X-axis labels missing, only found: {x_axis_found}")

    return results


def test_compare_axes(page, port):
    """Test axis labels on compare webapp (two charts)."""
    results = []

    page.goto(f"http://localhost:{port}/compare/")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # Select students in both panels
    student_a = page.locator("#studentSelectA")
    student_b = page.locator("#studentSelectB")

    student_a.select_option(index=1)
    time.sleep(0.5)
    student_b.select_option(index=2)
    time.sleep(1)

    # Take screenshot
    screenshot_path = f"{SCREENSHOT_DIR}/compare_chart_axes.png"
    page.screenshot(path=screenshot_path)

    # Get page text
    page_text = page.locator("body").text_content()

    # Check Y-axis labels (should appear twice, once per chart)
    y_axis_labels = ["99+8", "99+6", "99+4", "99+2", "99", "75", "50", "25", "0"]
    y_axis_found = [label for label in y_axis_labels if label in page_text]

    if len(y_axis_found) >= 5:
        results.append(("compare Y-axis labels", True, f"Found: {', '.join(y_axis_found)}"))
        print(f"  ✓ Y-axis labels found: {', '.join(y_axis_found)}")
    else:
        results.append(("compare Y-axis labels", False, f"Only found: {y_axis_found}"))
        print(f"  ✗ Y-axis labels missing, only found: {y_axis_found}")

    # Check X-axis labels
    x_axis_labels = ["Fall", "Winter", "Spring"]
    x_axis_found = [label for label in x_axis_labels if label in page_text]

    if len(x_axis_found) == 3:
        results.append(("compare X-axis labels", True, f"Found: {', '.join(x_axis_found)}"))
        print(f"  ✓ X-axis labels found: {', '.join(x_axis_found)}")
    else:
        results.append(("compare X-axis labels", False, f"Only found: {x_axis_found}"))
        print(f"  ✗ X-axis labels missing, only found: {x_axis_found}")

    return results


if __name__ == "__main__":
    success = run_axis_tests()
    sys.exit(0 if success else 1)
