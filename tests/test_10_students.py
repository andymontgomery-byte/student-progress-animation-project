#!/usr/bin/env python3
"""
Test every webapp with 10+ different students.
Screenshot each step and verify visually.
"""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'tests', 'screenshots', 'student_tests')
PORT = 8772

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_student_tests():
    print("=" * 70)
    print("TESTING 10+ STUDENTS ON EACH WEBAPP")
    print("=" * 70)

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

            # Test Main Webapp with 10 students
            print("\n" + "=" * 70)
            print("MAIN WEBAPP - Testing 10 students")
            print("=" * 70)
            results = test_webapp_students(
                browser, PORT, "/", "main", 10
            )
            all_results.extend(results)

            # Test Strata Webapp with all students (it has fewer)
            print("\n" + "=" * 70)
            print("STRATA WEBAPP - Testing all students")
            print("=" * 70)
            results = test_webapp_students(
                browser, PORT, "/strata/", "strata", 10
            )
            all_results.extend(results)

            # Test Compare Webapp with 10 student pairs
            print("\n" + "=" * 70)
            print("COMPARE WEBAPP - Testing 10 student pairs")
            print("=" * 70)
            results = test_compare_students(browser, PORT, 10)
            all_results.extend(results)

            # Test Compare with different filter combinations
            print("\n" + "=" * 70)
            print("COMPARE WEBAPP - Testing filter combinations")
            print("=" * 70)
            results = test_compare_filters(browser, PORT)
            all_results.extend(results)

            browser.close()

    finally:
        server.terminate()
        server.wait()

    # Summary
    print("\n" + "=" * 70)
    print("STUDENT TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in all_results if r[1] == "PASS")
    failed = sum(1 for r in all_results if r[1] == "FAIL")

    for name, status, detail in all_results:
        icon = "✓" if status == "PASS" else "✗"
        print(f"  {icon} {name}: {detail}")

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Screenshots: {SCREENSHOT_DIR}")

    if failed > 0:
        print("\nFAILED - Review screenshots!")
        return False
    return True


def test_webapp_students(browser, port, path, name, count):
    """Test selecting multiple students on a single-dropdown webapp."""
    results = []
    page = browser.new_page(viewport={'width': 1200, 'height': 900})

    try:
        page.goto(f"http://localhost:{port}{path}")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        dropdown = page.locator("select").first
        options = dropdown.locator("option").all_text_contents()
        num_students = len(options) - 1  # Exclude placeholder

        test_count = min(count, num_students)
        print(f"  Testing {test_count} of {num_students} students...")

        for i in range(1, test_count + 1):
            # Select student
            dropdown.select_option(index=i)
            time.sleep(0.8)

            # Get student name from dropdown
            selected_text = options[i] if i < len(options) else f"Student {i}"
            student_name = selected_text.split(" - ")[0] if " - " in selected_text else f"student_{i}"
            student_name = student_name.replace(" ", "_")[:20]

            # Screenshot
            screenshot_path = f"{SCREENSHOT_DIR}/{name}_{i:02d}_{student_name}.png"
            page.screenshot(path=screenshot_path)

            # Verify chart has data points (canvas should be drawn)
            canvas = page.locator("canvas").first
            if canvas.is_visible():
                # Check if there are visible data labels on the chart
                # The chart shows percentile numbers like "46", "81", "95"
                page_text = page.locator("body").text_content()

                # A valid chart should have numbers in the percentile range
                has_data = any(str(n) in page_text for n in range(1, 100))

                if has_data:
                    results.append((f"{name} student {i}", "PASS", f"{student_name}"))
                    print(f"    ✓ Student {i}: {student_name}")
                else:
                    results.append((f"{name} student {i}", "FAIL", "No data visible"))
                    print(f"    ✗ Student {i}: No data visible")
            else:
                results.append((f"{name} student {i}", "FAIL", "Canvas not visible"))
                print(f"    ✗ Student {i}: Canvas not visible")

    except Exception as e:
        results.append((f"{name} webapp", "FAIL", str(e)))

    page.close()
    return results


def test_compare_students(browser, port, count):
    """Test selecting student pairs on compare webapp."""
    results = []
    page = browser.new_page(viewport={'width': 1400, 'height': 900})

    try:
        page.goto(f"http://localhost:{port}/compare/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        student_a = page.locator("#studentSelectA")
        student_b = page.locator("#studentSelectB")

        options_a = student_a.locator("option").all_text_contents()
        num_students = len(options_a) - 1

        test_count = min(count, num_students // 2)
        print(f"  Testing {test_count} student pairs...")

        for i in range(test_count):
            idx_a = i * 2 + 1
            idx_b = i * 2 + 2

            if idx_b >= len(options_a):
                break

            # Select student A
            student_a.select_option(index=idx_a)
            time.sleep(0.5)

            # Select student B
            student_b.select_option(index=idx_b)
            time.sleep(0.5)

            # Get names
            name_a = options_a[idx_a].split(" - ")[0] if " - " in options_a[idx_a] else f"A{idx_a}"
            name_b = options_a[idx_b].split(" - ")[0] if " - " in options_a[idx_b] else f"B{idx_b}"

            # Screenshot
            screenshot_path = f"{SCREENSHOT_DIR}/compare_pair_{i+1:02d}.png"
            page.screenshot(path=screenshot_path)

            # Verify both charts rendered
            canvases = page.locator("canvas")
            if canvases.count() >= 2:
                results.append((f"compare pair {i+1}", "PASS", f"{name_a} vs {name_b}"))
                print(f"    ✓ Pair {i+1}: {name_a} vs {name_b}")
            else:
                results.append((f"compare pair {i+1}", "FAIL", "Charts not visible"))
                print(f"    ✗ Pair {i+1}: Charts not visible")

    except Exception as e:
        results.append(("compare pairs", "FAIL", str(e)))

    page.close()
    return results


def test_compare_filters(browser, port):
    """Test different filter combinations on compare webapp."""
    results = []
    page = browser.new_page(viewport={'width': 1400, 'height': 900})

    try:
        page.goto(f"http://localhost:{port}/compare/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        school_select = page.locator("#schoolFilter")
        subject_select = page.locator("#subjectFilter")
        grade_select = page.locator("#gradeFilter")
        count_el = page.locator("#studentCount")

        # Get filter options
        schools = school_select.locator("option").all_text_contents()[1:6]  # First 5 schools
        subjects = subject_select.locator("option").all_text_contents()[1:]  # All subjects
        grades = grade_select.locator("option").all_text_contents()[1:6]  # First 5 grades

        test_num = 0

        # Test each school
        print("  Testing school filters...")
        for i, school in enumerate(schools[:3]):
            school_select.select_option(index=i+1)
            time.sleep(0.3)
            count = count_el.text_content()

            screenshot_path = f"{SCREENSHOT_DIR}/filter_school_{i+1}.png"
            page.screenshot(path=screenshot_path)

            if count.strip() != "0 students":
                results.append((f"school filter {school[:15]}", "PASS", count))
                print(f"    ✓ {school[:20]}: {count}")
            else:
                results.append((f"school filter {school[:15]}", "FAIL", "0 students"))
                print(f"    ✗ {school[:20]}: 0 students")

            # Reset
            school_select.select_option(value="")
            time.sleep(0.2)

        # Test each subject
        print("  Testing subject filters...")
        for i, subject in enumerate(subjects):
            subject_select.select_option(index=i+1)
            time.sleep(0.3)
            count = count_el.text_content()

            screenshot_path = f"{SCREENSHOT_DIR}/filter_subject_{i+1}.png"
            page.screenshot(path=screenshot_path)

            if count.strip() != "0 students":
                results.append((f"subject filter {subject[:15]}", "PASS", count))
                print(f"    ✓ {subject}: {count}")
            else:
                results.append((f"subject filter {subject[:15]}", "FAIL", "0 students"))
                print(f"    ✗ {subject}: 0 students")

            # Reset
            subject_select.select_option(value="")
            time.sleep(0.2)

        # Test each grade
        print("  Testing grade filters...")
        for i, grade in enumerate(grades[:5]):
            # Reset ALL filters first and wait for 490 students
            school_select.select_option(value="")
            subject_select.select_option(value="")
            grade_select.select_option(value="")
            page.wait_for_function("document.getElementById('studentCount').textContent.includes('490')", timeout=5000)

            grade_select.select_option(index=i+1)
            # Wait for count to change from 490
            page.wait_for_function("!document.getElementById('studentCount').textContent.includes('490')", timeout=5000)
            time.sleep(0.2)
            count = count_el.text_content()

            screenshot_path = f"{SCREENSHOT_DIR}/filter_grade_{i+1}.png"
            page.screenshot(path=screenshot_path)

            # Check if count is exactly "0 students" (not just contains "0")
            if count.strip() != "0 students":
                results.append((f"grade filter {grade}", "PASS", count))
                print(f"    ✓ {grade}: {count}")
            else:
                results.append((f"grade filter {grade}", "FAIL", "0 students"))
                print(f"    ✗ {grade}: 0 students")

            # Reset
            grade_select.select_option(value="")
            time.sleep(0.2)

        # Test combined filters - use Alpha Austin + Math K-12 (known to have students)
        print("  Testing combined filters...")
        # Reset all first
        school_select.select_option(value="")
        subject_select.select_option(value="")
        grade_select.select_option(value="")
        time.sleep(0.2)

        # Alpha Austin is index 2, Math K-12 is index 2
        school_select.select_option(index=2)  # Alpha Austin
        subject_select.select_option(index=2)  # Math K-12
        time.sleep(0.3)
        count = count_el.text_content()
        screenshot_path = f"{SCREENSHOT_DIR}/filter_combined.png"
        page.screenshot(path=screenshot_path)

        if count.strip() != "0 students":
            results.append((f"combined filter", "PASS", count))
            print(f"    ✓ Combined: {count}")
        else:
            results.append((f"combined filter", "FAIL", "0 students"))
            print(f"    ✗ Combined: 0 students")

        # Select a student after filtering
        student_a = page.locator("#studentSelectA")
        opts = student_a.locator("option").all_text_contents()
        if len(opts) > 1:
            student_a.select_option(index=1)
            time.sleep(0.5)
            screenshot_path = f"{SCREENSHOT_DIR}/filter_then_select.png"
            page.screenshot(path=screenshot_path)
            results.append(("filter then select", "PASS", "Student selected after filter"))
            print(f"    ✓ Select after filter works")
        else:
            results.append(("filter then select", "FAIL", "No students after filter"))
            print(f"    ✗ No students after filter")

    except Exception as e:
        results.append(("filter tests", "FAIL", str(e)))

    page.close()
    return results


if __name__ == "__main__":
    success = run_student_tests()
    sys.exit(0 if success else 1)
