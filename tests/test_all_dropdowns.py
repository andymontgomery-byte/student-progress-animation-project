#!/usr/bin/env python3
"""Test every dropdown on the compare page and report which work/fail."""

import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

URL = "https://andymontgomery-byte.github.io/student-progress-animation-project/compare/"

def test_dropdowns():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1400, 'height': 900})

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("Loading page...")
        page.goto(URL)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Test 1: Schools dropdown
        print("\n" + "="*50)
        print("TESTING: Schools dropdown (#schoolFilter)")
        print("="*50)
        try:
            school_select = page.locator("#schoolFilter")
            options = school_select.locator("option").all_text_contents()
            print(f"  Options found: {len(options)}")
            print(f"  First 5: {options[:5]}")

            if len(options) > 1:
                school_select.select_option(index=1)
                time.sleep(0.3)
                count = page.locator("#studentCount").text_content()
                print(f"  After selecting index 1: student count = {count}")
                school_select.select_option(value="")
                results.append(("Schools dropdown", "WORKS", f"{len(options)} options"))
            else:
                results.append(("Schools dropdown", "BROKEN", "Only 1 option"))
        except Exception as e:
            results.append(("Schools dropdown", "BROKEN", str(e)))
            print(f"  ERROR: {e}")

        # Test 2: Subjects dropdown
        print("\n" + "="*50)
        print("TESTING: Subjects dropdown (#subjectFilter)")
        print("="*50)
        try:
            subject_select = page.locator("#subjectFilter")
            options = subject_select.locator("option").all_text_contents()
            print(f"  Options found: {len(options)}")
            print(f"  All options: {options}")

            if len(options) > 1:
                subject_select.select_option(index=1)
                time.sleep(0.3)
                count = page.locator("#studentCount").text_content()
                print(f"  After selecting index 1: student count = {count}")
                subject_select.select_option(value="")
                results.append(("Subjects dropdown", "WORKS", f"{len(options)} options"))
            else:
                results.append(("Subjects dropdown", "BROKEN", "Only 1 option"))
        except Exception as e:
            results.append(("Subjects dropdown", "BROKEN", str(e)))
            print(f"  ERROR: {e}")

        # Test 3: Grades dropdown
        print("\n" + "="*50)
        print("TESTING: Grades dropdown (#gradeFilter)")
        print("="*50)
        try:
            grade_select = page.locator("#gradeFilter")
            options = grade_select.locator("option").all_text_contents()
            print(f"  Options found: {len(options)}")
            print(f"  All options: {options}")

            if len(options) > 1:
                grade_select.select_option(index=1)
                time.sleep(0.3)
                count = page.locator("#studentCount").text_content()
                print(f"  After selecting index 1: student count = {count}")
                grade_select.select_option(value="")
                results.append(("Grades dropdown", "WORKS", f"{len(options)} options"))
            else:
                results.append(("Grades dropdown", "BROKEN", "Only 1 option"))
        except Exception as e:
            results.append(("Grades dropdown", "BROKEN", str(e)))
            print(f"  ERROR: {e}")

        # Test 4: Student A dropdown
        print("\n" + "="*50)
        print("TESTING: Student A dropdown (#studentSelectA)")
        print("="*50)
        try:
            student_a = page.locator("#studentSelectA")
            options = student_a.locator("option").all_text_contents()
            print(f"  Options found: {len(options)}")
            print(f"  First 3: {options[:3]}")

            if len(options) > 1:
                student_a.select_option(index=1)
                time.sleep(0.5)
                # Check if chart rendered by looking for info cards
                info_visible = page.locator(".info-card").first.is_visible() if page.locator(".info-card").count() > 0 else False
                print(f"  Info card visible after selection: {info_visible}")

                # Take screenshot
                path = os.path.join(SCREENSHOT_DIR, "dropdown_test_studentA.png")
                page.screenshot(path=path)
                print(f"  Screenshot: {path}")

                student_a.select_option(index=0)
                results.append(("Student A dropdown", "WORKS", f"{len(options)} options, info_visible={info_visible}"))
            else:
                results.append(("Student A dropdown", "BROKEN", "Only 1 option"))
        except Exception as e:
            results.append(("Student A dropdown", "BROKEN", str(e)))
            print(f"  ERROR: {e}")

        # Test 5: Student B dropdown
        print("\n" + "="*50)
        print("TESTING: Student B dropdown (#studentSelectB)")
        print("="*50)
        try:
            student_b = page.locator("#studentSelectB")
            options = student_b.locator("option").all_text_contents()
            print(f"  Options found: {len(options)}")
            print(f"  First 3: {options[:3]}")

            if len(options) > 1:
                student_b.select_option(index=1)
                time.sleep(0.5)

                # Take screenshot
                path = os.path.join(SCREENSHOT_DIR, "dropdown_test_studentB.png")
                page.screenshot(path=path)
                print(f"  Screenshot: {path}")

                student_b.select_option(index=0)
                results.append(("Student B dropdown", "WORKS", f"{len(options)} options"))
            else:
                results.append(("Student B dropdown", "BROKEN", "Only 1 option"))
        except Exception as e:
            results.append(("Student B dropdown", "BROKEN", str(e)))
            print(f"  ERROR: {e}")

        # Test 6: Combined filter then student selection
        print("\n" + "="*50)
        print("TESTING: Filter then select student")
        print("="*50)
        try:
            # Apply school filter
            page.locator("#schoolFilter").select_option(index=1)
            time.sleep(0.3)

            # Check student dropdown updated
            student_a = page.locator("#studentSelectA")
            options_after_filter = student_a.locator("option").all_text_contents()
            print(f"  Student options after school filter: {len(options_after_filter)}")

            if len(options_after_filter) > 1:
                student_a.select_option(index=1)
                time.sleep(0.5)
                path = os.path.join(SCREENSHOT_DIR, "dropdown_test_filtered_student.png")
                page.screenshot(path=path)
                print(f"  Screenshot: {path}")
                results.append(("Filter + Student", "WORKS", f"{len(options_after_filter)} students after filter"))
            else:
                results.append(("Filter + Student", "BROKEN", "No students after filter"))
        except Exception as e:
            results.append(("Filter + Student", "BROKEN", str(e)))
            print(f"  ERROR: {e}")

        if console_errors:
            print(f"\nConsole errors: {console_errors}")

        browser.close()

    # Summary
    print("\n" + "="*60)
    print("DROPDOWN TEST SUMMARY")
    print("="*60)
    for name, status, detail in results:
        icon = "✓" if status == "WORKS" else "✗"
        print(f"  {icon} {name}: {status} - {detail}")

    broken = [r for r in results if r[1] == "BROKEN"]
    if broken:
        print(f"\n{len(broken)} BROKEN dropdowns found!")
        return False
    else:
        print(f"\nAll {len(results)} dropdowns work!")
        return True

if __name__ == "__main__":
    test_dropdowns()
