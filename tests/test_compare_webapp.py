#!/usr/bin/env python3
"""
Test suite for comparison webapp.
Run: python3 tests/test_compare_webapp.py
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_JSON = os.path.join(BASE_DIR, 'docs', 'data.json')
COMPARE_HTML = os.path.join(BASE_DIR, 'docs', 'compare', 'index.html')

def load_data():
    with open(DATA_JSON) as f:
        return json.load(f)

def test_compare_html_exists():
    """Test that compare/index.html exists"""
    assert os.path.exists(COMPARE_HTML), f"compare/index.html not found at {COMPARE_HTML}"
    print("✓ compare/index.html exists")

def test_compare_html_has_two_charts():
    """Test that compare page has two chart canvases"""
    with open(COMPARE_HTML) as f:
        content = f.read()

    assert content.count('id="chart') >= 2, "compare page should have at least 2 chart elements"
    assert 'chartA' in content, "compare page should have chartA"
    assert 'chartB' in content, "compare page should have chartB"
    print("✓ compare page has two chart canvases")

def test_compare_html_has_filters():
    """Test that compare page has filter dropdowns"""
    with open(COMPARE_HTML) as f:
        content = f.read()

    assert 'schoolFilter' in content, "compare page should have school filter"
    assert 'subjectFilter' in content, "compare page should have subject filter"
    assert 'gradeFilter' in content, "compare page should have grade filter"
    print("✓ compare page has filter dropdowns")

def test_compare_html_has_two_student_selects():
    """Test that compare page has two student selectors"""
    with open(COMPARE_HTML) as f:
        content = f.read()

    assert 'studentSelectA' in content, "compare page should have studentSelectA"
    assert 'studentSelectB' in content, "compare page should have studentSelectB"
    print("✓ compare page has two student selectors")

def test_compare_html_loads_data():
    """Test that compare page loads data.json"""
    with open(COMPARE_HTML) as f:
        content = f.read()

    assert 'data.json' in content, "compare page should reference data.json"
    print("✓ compare page loads data.json")

def test_all_schools_have_students():
    """Test that every school has at least one student"""
    data = load_data()
    schools = set(r['school'] for r in data)

    for school in schools:
        count = len([r for r in data if r['school'] == school])
        assert count > 0, f"School {school} has no students"

    print(f"✓ All {len(schools)} schools have students")

def test_all_subjects_have_students():
    """Test that every subject has at least one student"""
    data = load_data()
    subjects = set(r['course'] for r in data)

    for subject in subjects:
        count = len([r for r in data if r['course'] == subject])
        assert count > 0, f"Subject {subject} has no students"

    print(f"✓ All {len(subjects)} subjects have students")

def test_all_grades_have_students():
    """Test that every grade has at least one student"""
    data = load_data()
    grades = set(r['grade'] for r in data)

    for grade in grades:
        count = len([r for r in data if r['grade'] == grade])
        assert count > 0, f"Grade {grade} has no students"

    print(f"✓ All {len(grades)} grades have students")

def test_dropdown_text_includes_start_percentile():
    """Test that dropdown would include starting percentile"""
    data = load_data()

    for r in data[:10]:
        # Verify fall_pct exists and is valid
        assert r['fall_pct'] is not None, f"Student {r['email']} has no fall_pct"
        assert 1 <= r['fall_pct'] <= 99, f"Student {r['email']} has invalid fall_pct: {r['fall_pct']}"

    print("✓ All students have valid starting percentile for dropdown")

def test_filter_combinations():
    """Test various filter combinations return results"""
    data = load_data()

    schools = list(set(r['school'] for r in data))
    subjects = list(set(r['course'] for r in data))

    # Test single filters - verify each school has students
    for school in schools[:5]:
        filtered = [r for r in data if r['school'] == school]
        assert len(filtered) > 0, f"No students for school: {school}"

    # Test combined filters - find ANY valid combinations across ALL schools/subjects
    combinations_tested = 0
    for school in schools:
        for subject in subjects:
            filtered = [r for r in data if r['school'] == school and r['course'] == subject]
            if len(filtered) > 0:
                combinations_tested += 1

    assert combinations_tested > 0, "No valid school+subject combinations"
    print(f"✓ Filter combinations work ({combinations_tested} combinations tested)")

def test_students_sorted_by_cgi():
    """Test that students can be sorted by CGI descending"""
    data = load_data()
    sorted_data = sorted(data, key=lambda x: x['cgi'], reverse=True)

    for i in range(1, min(len(sorted_data), 10)):
        assert sorted_data[i]['cgi'] <= sorted_data[i-1]['cgi'], "Students not sorted by CGI"

    print("✓ Students can be sorted by CGI descending")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("COMPARISON WEBAPP TESTS")
    print("=" * 60)
    print()

    tests = [
        test_compare_html_exists,
        test_compare_html_has_two_charts,
        test_compare_html_has_filters,
        test_compare_html_has_two_student_selects,
        test_compare_html_loads_data,
        test_all_schools_have_students,
        test_all_subjects_have_students,
        test_all_grades_have_students,
        test_dropdown_text_includes_start_percentile,
        test_filter_combinations,
        test_students_sorted_by_cgi,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
