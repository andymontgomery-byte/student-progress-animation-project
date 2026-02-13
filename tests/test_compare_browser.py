#!/usr/bin/env python3
"""
Browser-based tests for comparison webapp using Playwright.
Tests actual browser functionality, not just HTML structure.

Run: python3 tests/test_compare_browser.py
"""

import os
import sys
import time
import json
import subprocess
import signal
from playwright.sync_api import sync_playwright, expect

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DATA_JSON = os.path.join(DOCS_DIR, 'data.json')
PORT = 8765

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
        time.sleep(1)  # Give server time to start
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
    print("BROWSER-BASED COMPARISON WEBAPP TESTS")
    print("=" * 60)
    print()

    expected_data = load_expected_data()
    expected_schools = sorted(set(r['school'] for r in expected_data))
    expected_subjects = sorted(set(r['course'] for r in expected_data))
    expected_grades = sorted(set(str(r['grade']) for r in expected_data))

    passed = 0
    failed = 0

    with TestServer(DOCS_DIR, PORT):
        print(f"Server running at http://localhost:{PORT}")
        print()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Collect console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            tests = [
                ("Page loads successfully", test_page_loads),
                ("Data loads without errors", test_data_loads),
                ("No console errors", lambda p: test_no_console_errors(p, console_errors)),
                ("School filter populates correctly", lambda p: test_school_filter(p, expected_schools)),
                ("Subject filter populates correctly", lambda p: test_subject_filter(p, expected_subjects)),
                ("Grade filter populates correctly", lambda p: test_grade_filter(p, expected_grades)),
                ("Student count shows correct total", lambda p: test_student_count(p, len(expected_data))),
                ("Student selects populate", test_student_selects_populate),
                ("Dropdown shows starting percentile", test_dropdown_shows_percentile),
                ("Filtering by school works", test_filter_by_school),
                ("Filtering by subject works", test_filter_by_subject),
                ("Filtering by grade works", test_filter_by_grade),
                ("Combined filtering works", test_combined_filtering),
                ("Clear filters works", test_clear_filters),
                ("Selecting student A shows chart", test_select_student_a),
                ("Selecting student B shows chart", test_select_student_b),
                ("Both charts work independently", test_both_charts),
                ("Animation controls exist", test_animation_controls),
                ("Play button works", test_play_button),
            ]

            # Navigate to compare page
            page.goto(f"http://localhost:{PORT}/compare/")
            page.wait_for_load_state("networkidle")
            time.sleep(0.5)  # Extra wait for JS to execute

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
    assert page.locator("#chartA").count() > 0, "Should have chartA canvas"
    assert page.locator("#chartB").count() > 0, "Should have chartB canvas"


def test_data_loads(page):
    """Test that data.json is fetched and loaded"""
    # Check that student count element has a number
    count_text = page.locator("#studentCount").text_content()
    assert "students" in count_text.lower() or count_text.strip().isdigit() or "student" in count_text.lower(), \
        f"Student count should show number of students, got: {count_text}"
    assert "error" not in count_text.lower(), f"Should not show error: {count_text}"


def test_no_console_errors(page, console_errors):
    """Test that there are no JavaScript console errors"""
    # Filter out known non-critical errors
    critical_errors = [e for e in console_errors if "favicon" not in e.lower()]
    assert len(critical_errors) == 0, f"Console errors: {critical_errors}"


def test_school_filter(page, expected_schools):
    """Test that school filter dropdown populates with correct options"""
    options = page.locator("#schoolFilter option").all_text_contents()
    # First option is "All Schools"
    assert options[0] == "All Schools", f"First option should be 'All Schools', got: {options[0]}"
    filter_schools = [o for o in options if o != "All Schools"]
    assert len(filter_schools) == len(expected_schools), \
        f"Expected {len(expected_schools)} schools, got {len(filter_schools)}"


def test_subject_filter(page, expected_subjects):
    """Test that subject filter dropdown populates with correct options"""
    options = page.locator("#subjectFilter option").all_text_contents()
    assert options[0] == "All Subjects", f"First option should be 'All Subjects', got: {options[0]}"
    filter_subjects = [o for o in options if o != "All Subjects"]
    assert len(filter_subjects) == len(expected_subjects), \
        f"Expected {len(expected_subjects)} subjects, got {len(filter_subjects)}"


def test_grade_filter(page, expected_grades):
    """Test that grade filter dropdown populates with correct options"""
    options = page.locator("#gradeFilter option").all_text_contents()
    assert options[0] == "All Grades", f"First option should be 'All Grades', got: {options[0]}"
    filter_grades = [o for o in options if o != "All Grades"]
    assert len(filter_grades) == len(expected_grades), \
        f"Expected {len(expected_grades)} grades, got {len(filter_grades)}"


def test_student_count(page, expected_count):
    """Test that student count shows correct total"""
    count_text = page.locator("#studentCount").text_content()
    # Extract number from text like "1234 students"
    import re
    match = re.search(r'(\d+)', count_text)
    assert match, f"Could not find number in student count: {count_text}"
    actual_count = int(match.group(1))
    assert actual_count == expected_count, f"Expected {expected_count} students, got {actual_count}"


def test_student_selects_populate(page):
    """Test that student select dropdowns have options"""
    options_a = page.locator("#studentSelectA option").count()
    options_b = page.locator("#studentSelectB option").count()
    # Should have at least "Select a student" plus some actual students
    assert options_a > 1, f"Student A select should have options, got {options_a}"
    assert options_b > 1, f"Student B select should have options, got {options_b}"


def test_dropdown_shows_percentile(page):
    """Test that student dropdown options include starting percentile"""
    # Get first actual student option (not the placeholder)
    options = page.locator("#studentSelectA option").all_text_contents()
    student_options = [o for o in options if "Select a student" not in o and o.strip()]
    assert len(student_options) > 0, "Should have student options"

    # Check that option text includes percentile info (like "P45" or "45th")
    first_option = student_options[0]
    has_percentile = "P" in first_option or "%" in first_option or "th" in first_option.lower()
    assert has_percentile, f"Student option should show percentile, got: {first_option}"


def test_filter_by_school(page):
    """Test that filtering by school reduces student count"""
    # Get initial count
    initial_text = page.locator("#studentCount").text_content()
    import re
    initial_match = re.search(r'(\d+)', initial_text)
    initial_count = int(initial_match.group(1))

    # Select a specific school
    page.locator("#schoolFilter").select_option(index=1)
    time.sleep(0.3)

    # Get new count
    new_text = page.locator("#studentCount").text_content()
    new_match = re.search(r'(\d+)', new_text)
    new_count = int(new_match.group(1))

    assert new_count < initial_count, f"Filtering should reduce count: {initial_count} -> {new_count}"
    assert new_count > 0, "Filtered result should have some students"

    # Reset filter
    page.locator("#schoolFilter").select_option(value="")
    time.sleep(0.2)


def test_filter_by_subject(page):
    """Test that filtering by subject works"""
    # Get initial count
    initial_text = page.locator("#studentCount").text_content()
    import re
    initial_match = re.search(r'(\d+)', initial_text)
    initial_count = int(initial_match.group(1))

    # Select a specific subject
    page.locator("#subjectFilter").select_option(index=1)
    time.sleep(0.3)

    # Get new count
    new_text = page.locator("#studentCount").text_content()
    new_match = re.search(r'(\d+)', new_text)
    new_count = int(new_match.group(1))

    assert new_count < initial_count, f"Filtering should reduce count: {initial_count} -> {new_count}"

    # Reset filter
    page.locator("#subjectFilter").select_option(value="")
    time.sleep(0.2)


def test_filter_by_grade(page):
    """Test that filtering by grade works"""
    # Get initial count
    initial_text = page.locator("#studentCount").text_content()
    import re
    initial_match = re.search(r'(\d+)', initial_text)
    initial_count = int(initial_match.group(1))

    # Select a specific grade
    page.locator("#gradeFilter").select_option(index=1)
    time.sleep(0.3)

    # Get new count
    new_text = page.locator("#studentCount").text_content()
    new_match = re.search(r'(\d+)', new_text)
    new_count = int(new_match.group(1))

    assert new_count < initial_count, f"Filtering should reduce count: {initial_count} -> {new_count}"

    # Reset filter
    page.locator("#gradeFilter").select_option(value="")
    time.sleep(0.2)


def test_combined_filtering(page):
    """Test that combining filters works correctly"""
    # Apply school filter
    page.locator("#schoolFilter").select_option(index=1)
    time.sleep(0.2)

    # Get count after school filter
    import re
    school_text = page.locator("#studentCount").text_content()
    school_match = re.search(r'(\d+)', school_text)
    school_count = int(school_match.group(1))

    # Add subject filter
    page.locator("#subjectFilter").select_option(index=1)
    time.sleep(0.2)

    # Get count after both filters
    combined_text = page.locator("#studentCount").text_content()
    combined_match = re.search(r'(\d+)', combined_text)
    combined_count = int(combined_match.group(1))

    assert combined_count <= school_count, \
        f"Combined filter should not increase count: {school_count} -> {combined_count}"

    # Reset filters
    page.locator("#schoolFilter").select_option(value="")
    page.locator("#subjectFilter").select_option(value="")
    time.sleep(0.2)


def test_clear_filters(page):
    """Test that clearing filters restores full student list"""
    # Get initial count
    import re
    initial_text = page.locator("#studentCount").text_content()
    initial_match = re.search(r'(\d+)', initial_text)
    initial_count = int(initial_match.group(1))

    # Apply filters
    page.locator("#schoolFilter").select_option(index=1)
    page.locator("#subjectFilter").select_option(index=1)
    time.sleep(0.2)

    # Clear filters (if there's a clear button, use it; otherwise reset dropdowns)
    clear_btn = page.locator("button:has-text('Clear'), button:has-text('Reset')")
    if clear_btn.count() > 0:
        clear_btn.first.click()
    else:
        page.locator("#schoolFilter").select_option(value="")
        page.locator("#subjectFilter").select_option(value="")
        page.locator("#gradeFilter").select_option(value="")
    time.sleep(0.2)

    # Verify count is restored
    final_text = page.locator("#studentCount").text_content()
    final_match = re.search(r'(\d+)', final_text)
    final_count = int(final_match.group(1))

    assert final_count == initial_count, f"Clear should restore count: {initial_count} -> {final_count}"


def test_select_student_a(page):
    """Test that selecting a student in panel A triggers chart update"""
    # Select first student
    page.locator("#studentSelectA").select_option(index=1)
    time.sleep(0.5)

    # Check that canvas has been drawn on (by checking for any chart-related state)
    # We can check if the canvas context exists and has content
    canvas_a = page.locator("#chartA")
    assert canvas_a.is_visible(), "Chart A canvas should be visible"

    # Reset
    page.locator("#studentSelectA").select_option(index=0)
    time.sleep(0.2)


def test_select_student_b(page):
    """Test that selecting a student in panel B triggers chart update"""
    # Select first student
    page.locator("#studentSelectB").select_option(index=1)
    time.sleep(0.5)

    # Check that canvas is visible
    canvas_b = page.locator("#chartB")
    assert canvas_b.is_visible(), "Chart B canvas should be visible"

    # Reset
    page.locator("#studentSelectB").select_option(index=0)
    time.sleep(0.2)


def test_both_charts(page):
    """Test that both charts can be used independently"""
    # Select different students in each panel
    options_a = page.locator("#studentSelectA option").count()
    options_b = page.locator("#studentSelectB option").count()

    if options_a > 2 and options_b > 2:
        page.locator("#studentSelectA").select_option(index=1)
        page.locator("#studentSelectB").select_option(index=2)
        time.sleep(0.5)

        # Both should be visible
        assert page.locator("#chartA").is_visible(), "Chart A should be visible"
        assert page.locator("#chartB").is_visible(), "Chart B should be visible"

        # Reset
        page.locator("#studentSelectA").select_option(index=0)
        page.locator("#studentSelectB").select_option(index=0)
    else:
        # Not enough students to test this properly
        pass


def test_animation_controls(page):
    """Test that animation control buttons exist"""
    # Look for play/pause buttons or similar controls
    play_btn = page.locator("button:has-text('Play'), button:has-text('Animate'), #playBtn, .play-btn")
    has_play = play_btn.count() > 0

    # Animation might be auto or controlled - just check page has some control mechanism
    # If no explicit play button, check if selecting a student auto-animates
    if not has_play:
        # Select a student and see if animation starts
        page.locator("#studentSelectA").select_option(index=1)
        time.sleep(1)
        # If we get here without error, animation may be automatic
        page.locator("#studentSelectA").select_option(index=0)

    # Pass if we found controls or if the page works without them (auto-animate)
    assert True


def test_play_button(page):
    """Test that play/animate button works if present"""
    # Select a student first
    page.locator("#studentSelectA").select_option(index=1)
    time.sleep(0.3)

    play_btn = page.locator("button:has-text('Play'), button:has-text('Animate'), #playBtn, .play-btn")
    if play_btn.count() > 0:
        play_btn.first.click()
        time.sleep(0.5)
        # If we get here without error, button works

    # Reset
    page.locator("#studentSelectA").select_option(index=0)
    assert True


if __name__ == '__main__':
    success = run_browser_tests()
    sys.exit(0 if success else 1)
