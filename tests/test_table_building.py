#!/usr/bin/env python3
"""
Test suite for student progress table building.
Run: python3 tests/test_table_building.py
"""

import csv
import os
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE_CSV = os.path.join(BASE_DIR, 'student_progress.csv')
NORMS_CSV = os.path.join(BASE_DIR, 'norms_tables', 'csv', 'student_status_percentiles.csv')

def load_table():
    """Load student progress table"""
    data = []
    with open(TABLE_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def load_norms():
    """Load norms for verification"""
    norms = {}
    with open(NORMS_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['subject'], row['term'], row['grade'])
            if key not in norms:
                norms[key] = {}
            norms[key][int(row['percentile'])] = int(row['rit_score'])
    return norms

def test_required_columns():
    """Test that all required columns are present"""
    data = load_table()

    required = [
        'email', 'grade', 'school', 'course',
        'fall_pct', 'fall_99_levels',
        'winter_pct', 'winter_99_levels',
        'projected_pct', 'projected_99_levels',
        'cgi'
    ]

    actual = list(data[0].keys())
    missing = [c for c in required if c not in actual]

    assert not missing, f"Missing columns: {missing}"
    print(f"✓ All {len(required)} required columns present")

def test_no_empty_emails():
    """Test that no rows have empty email"""
    data = load_table()
    empty = [r for r in data if not r['email'] or r['email'].strip() == '']

    assert not empty, f"Found {len(empty)} rows with empty email"
    print("✓ No empty emails")

def test_valid_courses():
    """Test that all courses are valid"""
    data = load_table()
    valid_courses = {'Math K-12', 'Reading', 'Language Usage', 'Science K-12'}

    courses = set(r['course'] for r in data)
    invalid = courses - valid_courses

    assert not invalid, f"Invalid courses: {invalid}"
    print(f"✓ All courses valid: {courses}")

def test_valid_grades():
    """Test that all grades are valid"""
    data = load_table()
    valid_grades = {'K'} | {str(i) for i in range(1, 13)}

    grades = set(r['grade'] for r in data if r['grade'])
    invalid = grades - valid_grades

    assert not invalid, f"Invalid grades: {invalid}"
    print(f"✓ All grades valid")

def test_percentiles_in_range():
    """Test that all percentiles are 1-99"""
    data = load_table()

    errors = []
    for r in data:
        for col in ['fall_pct', 'winter_pct', 'projected_pct']:
            if r[col]:
                pct = int(r[col])
                if not (1 <= pct <= 99):
                    errors.append(f"{r['email']} {col}={pct}")

    assert not errors, f"Invalid percentiles:\n" + "\n".join(errors[:5])
    print("✓ All percentiles in range 1-99")

def test_99_levels_non_negative():
    """Test that 99th grade levels are non-negative integers"""
    data = load_table()

    errors = []
    for r in data:
        for col in ['fall_99_levels', 'winter_99_levels', 'projected_99_levels']:
            if r[col]:
                lvl = int(r[col])
                if lvl < 0:
                    errors.append(f"{r['email']} {col}={lvl}")

    assert not errors, f"Negative 99 levels:\n" + "\n".join(errors[:5])
    print("✓ All 99th grade levels non-negative")

def test_cgi_is_numeric():
    """Test that CGI values are valid numbers"""
    data = load_table()

    errors = []
    for r in data:
        try:
            cgi = float(r['cgi'])
        except (ValueError, TypeError):
            errors.append(f"{r['email']}: cgi={r['cgi']}")

    assert not errors, f"Invalid CGI values:\n" + "\n".join(errors[:5])
    print("✓ All CGI values are numeric")

def test_high_cgi_count():
    """Test count of students with CGI > 0.8"""
    data = load_table()

    high_cgi = [r for r in data if float(r['cgi']) > 0.8]

    # Just verify we have some high-growth students
    assert len(high_cgi) > 0, "No students with CGI > 0.8"
    print(f"✓ {len(high_cgi)} student/subject combinations with CGI > 0.8 (of {len(data)} total)")

def test_99_levels_only_when_99th_percentile():
    """Test that 99th grade levels > 0 only when percentile is 99"""
    data = load_table()

    errors = []
    for r in data:
        pairs = [
            ('fall_pct', 'fall_99_levels'),
            ('winter_pct', 'winter_99_levels'),
            ('projected_pct', 'projected_99_levels')
        ]
        for pct_col, lvl_col in pairs:
            if r[pct_col] and r[lvl_col]:
                pct = int(r[pct_col])
                lvl = int(r[lvl_col])
                if pct < 99 and lvl > 0:
                    errors.append(f"{r['email']}: {pct_col}={pct} but {lvl_col}={lvl}")

    assert not errors, f"99 levels without 99th percentile:\n" + "\n".join(errors[:5])
    print("✓ 99th grade levels only present when at 99th percentile")

def test_projected_reasonable():
    """Test that projected percentiles are reasonable (not wildly different from winter)"""
    data = load_table()

    warnings = []
    for r in data:
        if r['winter_pct'] and r['projected_pct']:
            winter = int(r['winter_pct'])
            projected = int(r['projected_pct'])
            # Projected should not drop significantly
            if projected < winter - 20:
                warnings.append(f"{r['email']}: winter={winter}, projected={projected}")

    if warnings:
        print(f"  Warning: {len(warnings)} records have projected < winter-20")
    print("✓ Projected percentiles checked")

def test_unique_email_course_combinations():
    """Test that email+course combinations are unique"""
    data = load_table()

    seen = set()
    duplicates = []
    for r in data:
        key = (r['email'], r['course'])
        if key in seen:
            duplicates.append(key)
        seen.add(key)

    assert not duplicates, f"Duplicate email+course: {duplicates[:5]}"
    print(f"✓ All {len(data)} email+course combinations are unique")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("TABLE BUILDING TESTS")
    print("=" * 60)
    print()

    tests = [
        test_required_columns,
        test_no_empty_emails,
        test_valid_courses,
        test_valid_grades,
        test_percentiles_in_range,
        test_99_levels_non_negative,
        test_cgi_is_numeric,
        test_high_cgi_count,
        test_99_levels_only_when_99th_percentile,
        test_projected_reasonable,
        test_unique_email_course_combinations,
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
