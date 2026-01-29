#!/usr/bin/env python3
"""
Test suite for norms table extraction from PDF.
Run: python3 tests/test_norms_extraction.py
"""

import csv
import os
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NORMS_CSV = os.path.join(BASE_DIR, 'norms_tables', 'csv', 'student_status_percentiles.csv')

def load_norms():
    """Load extracted norms data"""
    data = []
    with open(NORMS_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'subject': row['subject'],
                'term': row['term'],
                'grade': row['grade'],
                'percentile': int(row['percentile']),
                'rit_score': int(row['rit_score'])
            })
    return data

def test_all_subjects_present():
    """Test that all 4 subjects are present"""
    data = load_norms()
    subjects = set(r['subject'] for r in data)
    expected = {'Mathematics', 'Reading', 'Language Usage', 'Science'}

    missing = expected - subjects
    extra = subjects - expected

    assert not missing, f"Missing subjects: {missing}"
    assert not extra, f"Unexpected subjects: {extra}"
    print("✓ All 4 subjects present")

def test_all_terms_present():
    """Test that all 3 terms are present"""
    data = load_norms()
    terms = set(r['term'] for r in data)
    expected = {'Fall', 'Winter', 'Spring'}

    assert terms == expected, f"Expected {expected}, got {terms}"
    print("✓ All 3 terms present (Fall, Winter, Spring)")

def test_all_percentiles_present():
    """Test that percentiles 1-99 are present for each subject/term/grade combo"""
    data = load_norms()

    # Group by subject/term/grade
    groups = defaultdict(set)
    for r in data:
        key = (r['subject'], r['term'], r['grade'])
        groups[key].add(r['percentile'])

    expected_percentiles = set(range(1, 100))
    errors = []

    for key, percentiles in groups.items():
        if percentiles != expected_percentiles:
            missing = expected_percentiles - percentiles
            if missing:
                errors.append(f"{key}: missing percentiles {sorted(missing)[:5]}...")

    assert not errors, f"Percentile errors:\n" + "\n".join(errors[:5])
    print(f"✓ All percentiles 1-99 present for {len(groups)} subject/term/grade combinations")

def test_grade_coverage():
    """Test correct grade coverage for each subject"""
    data = load_norms()

    subject_grades = defaultdict(set)
    for r in data:
        subject_grades[r['subject']].add(r['grade'])

    expected = {
        'Mathematics': {'K'} | {str(i) for i in range(1, 13)},  # K-12
        'Reading': {'K'} | {str(i) for i in range(1, 13)},       # K-12
        'Language Usage': {str(i) for i in range(2, 12)},        # 2-11
        'Science': {str(i) for i in range(2, 11)},               # 2-10
    }

    for subject, exp_grades in expected.items():
        actual = subject_grades[subject]
        assert actual == exp_grades, f"{subject}: expected grades {sorted(exp_grades)}, got {sorted(actual)}"

    print("✓ Grade coverage correct for all subjects")

def test_rit_scores_valid_range():
    """Test that all RIT scores are in valid range (100-350)"""
    data = load_norms()

    invalid = [r for r in data if not (100 <= r['rit_score'] <= 350)]
    assert not invalid, f"Invalid RIT scores: {invalid[:5]}"
    print("✓ All RIT scores in valid range (100-350)")

def test_rit_scores_monotonic():
    """Test that RIT scores increase with percentile for each subject/term/grade"""
    data = load_norms()

    # Group by subject/term/grade
    groups = defaultdict(list)
    for r in data:
        key = (r['subject'], r['term'], r['grade'])
        groups[key].append((r['percentile'], r['rit_score']))

    errors = []
    for key, values in groups.items():
        sorted_vals = sorted(values, key=lambda x: x[0])
        for i in range(1, len(sorted_vals)):
            if sorted_vals[i][1] < sorted_vals[i-1][1]:
                errors.append(f"{key}: P{sorted_vals[i-1][0]}={sorted_vals[i-1][1]} > P{sorted_vals[i][0]}={sorted_vals[i][1]}")

    assert not errors, f"Non-monotonic RIT scores:\n" + "\n".join(errors[:5])
    print("✓ RIT scores monotonically increase with percentile")

def test_expected_row_counts():
    """Test that we have the expected number of rows"""
    data = load_norms()

    # Math: 13 grades × 99 percentiles × 3 terms = 3861
    # Reading: 13 grades × 99 percentiles × 3 terms = 3861
    # Language Usage: 10 grades × 99 percentiles × 3 terms = 2970
    # Science: 9 grades × 99 percentiles × 3 terms = 2673
    # Total: 13365

    subject_counts = defaultdict(int)
    for r in data:
        subject_counts[r['subject']] += 1

    expected = {
        'Mathematics': 3861,
        'Reading': 3861,
        'Language Usage': 2970,
        'Science': 2673
    }

    for subject, exp_count in expected.items():
        actual = subject_counts[subject]
        assert actual == exp_count, f"{subject}: expected {exp_count} rows, got {actual}"

    assert len(data) == 13365, f"Expected 13365 total rows, got {len(data)}"
    print(f"✓ Row counts correct (total: {len(data)})")

def test_spot_check_values():
    """Spot check specific known values"""
    data = load_norms()

    # Create lookup
    lookup = {}
    for r in data:
        key = (r['subject'], r['term'], r['grade'], r['percentile'])
        lookup[key] = r['rit_score']

    # Known values to check (from manual PDF verification)
    checks = [
        (('Mathematics', 'Fall', 'K', 1), 111),
        (('Mathematics', 'Fall', '4', 99), 233),
        (('Mathematics', 'Winter', '8', 50), 228),
        (('Reading', 'Fall', 'K', 1), 108),
        (('Reading', 'Spring', '12', 99), 278),
        (('Language Usage', 'Winter', '5', 75), 218),
        (('Science', 'Fall', '3', 25), 180),
    ]

    errors = []
    for key, expected_rit in checks:
        actual = lookup.get(key)
        if actual != expected_rit:
            errors.append(f"{key}: expected {expected_rit}, got {actual}")

    assert not errors, f"Spot check failures:\n" + "\n".join(errors)
    print(f"✓ {len(checks)} spot check values verified")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("NORMS EXTRACTION TESTS")
    print("=" * 60)
    print()

    tests = [
        test_all_subjects_present,
        test_all_terms_present,
        test_all_percentiles_present,
        test_grade_coverage,
        test_rit_scores_valid_range,
        test_rit_scores_monotonic,
        test_expected_row_counts,
        test_spot_check_values,
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
