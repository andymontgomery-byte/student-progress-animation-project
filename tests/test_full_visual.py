#!/usr/bin/env python3
"""
Comprehensive visual testing of ALL webapps.
Tests every user interaction and takes screenshots for verification.
"""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'tests', 'screenshots', 'full_visual')
PORT = 8771

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_all_visual_tests():
    print("=" * 70)
    print("COMPREHENSIVE VISUAL TESTING - ALL WEBAPPS")
    print("=" * 70)
    print()

    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', str(PORT)],
        cwd=DOCS_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    all_results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # Test all three webapps
            print("\n" + "=" * 70)
            print("TESTING: Main Webapp (/)")
            print("=" * 70)
            results = test_main_webapp(browser, PORT)
            all_results.extend([("Main: " + r[0], r[1], r[2]) for r in results])

            print("\n" + "=" * 70)
            print("TESTING: Strata Webapp (/strata/)")
            print("=" * 70)
            results = test_strata_webapp(browser, PORT)
            all_results.extend([("Strata: " + r[0], r[1], r[2]) for r in results])

            print("\n" + "=" * 70)
            print("TESTING: Compare Webapp (/compare/)")
            print("=" * 70)
            results = test_compare_webapp(browser, PORT)
            all_results.extend([("Compare: " + r[0], r[1], r[2]) for r in results])

            browser.close()

    finally:
        server.terminate()
        server.wait()

    # Final summary
    print("\n" + "=" * 70)
    print("FULL VISUAL TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0
    for name, status, detail in all_results:
        icon = "✓" if status == "PASS" else "✗"
        print(f"  {icon} {name}: {detail}")
        if status == "PASS":
            passed += 1
        else:
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")

    if failed > 0:
        print("\nFAILED TESTS - REVIEW SCREENSHOTS!")
        return False
    else:
        print("\nAll visual tests passed!")
        return True


def test_main_webapp(browser, port):
    """Test the main webapp."""
    results = []
    page = browser.new_page(viewport={'width': 1200, 'height': 800})

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    try:
        # Load page
        page.goto(f"http://localhost:{port}/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Screenshot initial state
        page.screenshot(path=f"{SCREENSHOT_DIR}/main_01_initial.png")

        # Test 1: Page loads
        title = page.title()
        if title:
            results.append(("Page loads", "PASS", f"Title: {title[:30]}"))
        else:
            results.append(("Page loads", "FAIL", "No title"))

        # Test 2: Console errors
        critical_errors = [e for e in console_errors if "favicon" not in e.lower()]
        if not critical_errors:
            results.append(("No console errors", "PASS", "Clean"))
        else:
            results.append(("No console errors", "FAIL", str(critical_errors[:2])))

        # Test 3: Student dropdown exists and has options
        dropdown = page.locator("select").first
        if dropdown.count() > 0:
            options = dropdown.locator("option").all_text_contents()
            if len(options) > 1:
                results.append(("Student dropdown", "PASS", f"{len(options)} options"))

                # Test 4: Select a student and verify chart
                dropdown.select_option(index=1)
                time.sleep(1)
                page.screenshot(path=f"{SCREENSHOT_DIR}/main_02_student_selected.png")

                # Check if canvas is visible
                canvas = page.locator("canvas")
                if canvas.count() > 0 and canvas.first.is_visible():
                    results.append(("Chart renders", "PASS", "Canvas visible"))
                else:
                    results.append(("Chart renders", "FAIL", "Canvas not visible"))
            else:
                results.append(("Student dropdown", "FAIL", "Only 1 option"))
        else:
            results.append(("Student dropdown", "FAIL", "Not found"))

    except Exception as e:
        results.append(("Main webapp", "FAIL", str(e)))

    page.close()
    return results


def test_strata_webapp(browser, port):
    """Test the Strata webapp."""
    results = []
    page = browser.new_page(viewport={'width': 1200, 'height': 800})

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    try:
        page.goto(f"http://localhost:{port}/strata/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        page.screenshot(path=f"{SCREENSHOT_DIR}/strata_01_initial.png")

        # Test 1: Page loads
        title = page.title()
        if title:
            results.append(("Page loads", "PASS", f"Title: {title[:30]}"))
        else:
            results.append(("Page loads", "FAIL", "No title"))

        # Test 2: Console errors
        critical_errors = [e for e in console_errors if "favicon" not in e.lower()]
        if not critical_errors:
            results.append(("No console errors", "PASS", "Clean"))
        else:
            results.append(("No console errors", "FAIL", str(critical_errors[:2])))

        # Test 3: Student dropdown
        dropdown = page.locator("select").first
        if dropdown.count() > 0:
            options = dropdown.locator("option").all_text_contents()
            if len(options) > 1:
                results.append(("Student dropdown", "PASS", f"{len(options)} options"))

                # Select student
                dropdown.select_option(index=1)
                time.sleep(1)
                page.screenshot(path=f"{SCREENSHOT_DIR}/strata_02_student_selected.png")

                canvas = page.locator("canvas")
                if canvas.count() > 0 and canvas.first.is_visible():
                    results.append(("Chart renders", "PASS", "Canvas visible"))
                else:
                    results.append(("Chart renders", "FAIL", "Canvas not visible"))
            else:
                results.append(("Student dropdown", "FAIL", "Only 1 option"))
        else:
            results.append(("Student dropdown", "FAIL", "Not found"))

    except Exception as e:
        results.append(("Strata webapp", "FAIL", str(e)))

    page.close()
    return results


def test_compare_webapp(browser, port):
    """Test the Compare webapp thoroughly."""
    results = []
    page = browser.new_page(viewport={'width': 1400, 'height': 900})

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    try:
        page.goto(f"http://localhost:{port}/compare/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        page.screenshot(path=f"{SCREENSHOT_DIR}/compare_01_initial.png")

        # Test 1: Page loads with correct student count
        count_el = page.locator("#studentCount")
        count_text = count_el.text_content() if count_el.count() > 0 else ""
        if "490" in count_text or "students" in count_text.lower():
            results.append(("Page loads", "PASS", count_text))
        else:
            results.append(("Page loads", "FAIL", f"Count: {count_text}"))

        # Test 2: Console errors
        critical_errors = [e for e in console_errors if "favicon" not in e.lower()]
        if not critical_errors:
            results.append(("No console errors", "PASS", "Clean"))
        else:
            results.append(("No console errors", "FAIL", str(critical_errors[:2])))

        # Test 3: Schools dropdown - NOT multi-select
        school_select = page.locator("#schoolFilter")
        is_multiple = school_select.evaluate("el => el.multiple")
        if is_multiple:
            results.append(("Schools not multi-select", "FAIL", "Still has multiple attribute!"))
        else:
            options = school_select.locator("option").all_text_contents()
            results.append(("Schools dropdown", "PASS", f"{len(options)} options, single-select"))

        # Test 4: Click schools dropdown and screenshot while open
        school_select.click()
        time.sleep(0.3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/compare_02_schools_open.png")
        # Verify options are visible (not blank)
        # Check first visible option text
        first_opt = school_select.locator("option").first.text_content()
        if first_opt and len(first_opt.strip()) > 0:
            results.append(("Schools options visible", "PASS", f"First: '{first_opt}'"))
        else:
            results.append(("Schools options visible", "FAIL", "Blank option text"))
        page.keyboard.press("Escape")
        time.sleep(0.2)

        # Test 5: Subjects dropdown
        subject_select = page.locator("#subjectFilter")
        subject_opts = subject_select.locator("option").all_text_contents()
        if len(subject_opts) >= 5:
            results.append(("Subjects dropdown", "PASS", f"{len(subject_opts)} options"))
        else:
            results.append(("Subjects dropdown", "FAIL", f"Only {len(subject_opts)} options"))

        # Test 6: Grades dropdown
        grade_select = page.locator("#gradeFilter")
        grade_opts = grade_select.locator("option").all_text_contents()
        if len(grade_opts) >= 13:
            results.append(("Grades dropdown", "PASS", f"{len(grade_opts)} options"))
        else:
            results.append(("Grades dropdown", "FAIL", f"Only {len(grade_opts)} options"))

        # Test 7: Filter by school and verify count changes
        initial_count = count_el.text_content()
        school_select.select_option(index=1)
        time.sleep(0.5)
        new_count = count_el.text_content()
        page.screenshot(path=f"{SCREENSHOT_DIR}/compare_03_school_filtered.png")
        if new_count != initial_count:
            results.append(("School filter works", "PASS", f"{initial_count} -> {new_count}"))
        else:
            results.append(("School filter works", "FAIL", "Count didn't change"))

        # Test 8: Student A dropdown has options after filter
        student_a = page.locator("#studentSelectA")
        student_a_opts = student_a.locator("option").all_text_contents()
        if len(student_a_opts) > 1:
            results.append(("Student A dropdown", "PASS", f"{len(student_a_opts)} options"))

            # Test 9: Select student A and verify chart
            student_a.select_option(index=1)
            time.sleep(1)
            page.screenshot(path=f"{SCREENSHOT_DIR}/compare_04_student_a.png")

            # Check for info cards
            info_cards = page.locator(".info-card, .student-info, [class*='info']")
            if info_cards.count() > 0:
                results.append(("Student A info displays", "PASS", "Info cards visible"))
            else:
                results.append(("Student A info displays", "FAIL", "No info cards"))
        else:
            results.append(("Student A dropdown", "FAIL", "No options after filter"))

        # Test 10: Student B dropdown
        student_b = page.locator("#studentSelectB")
        student_b_opts = student_b.locator("option").all_text_contents()
        if len(student_b_opts) > 1:
            # Select different student
            student_b.select_option(index=min(2, len(student_b_opts)-1))
            time.sleep(1)
            page.screenshot(path=f"{SCREENSHOT_DIR}/compare_05_both_students.png")
            results.append(("Student B dropdown", "PASS", f"{len(student_b_opts)} options"))
        else:
            results.append(("Student B dropdown", "FAIL", "No options"))

        # Test 11: Clear filters button
        clear_btn = page.locator("#clearFilters, .clear-filters, button:has-text('Clear')")
        if clear_btn.count() > 0:
            clear_btn.first.click()
            time.sleep(0.5)
            cleared_count = count_el.text_content()
            if "490" in cleared_count:
                results.append(("Clear filters", "PASS", f"Restored to {cleared_count}"))
            else:
                results.append(("Clear filters", "FAIL", f"Count: {cleared_count}"))
        else:
            results.append(("Clear filters", "FAIL", "Button not found"))

        # Test 12: Animate button exists
        animate_btn = page.locator("#animateBtnA, button:has-text('Animate')")
        if animate_btn.count() > 0:
            results.append(("Animate button", "PASS", "Found"))
        else:
            results.append(("Animate button", "FAIL", "Not found"))

    except Exception as e:
        results.append(("Compare webapp", "FAIL", str(e)))

    page.close()
    return results


if __name__ == "__main__":
    success = run_all_visual_tests()
    sys.exit(0 if success else 1)
