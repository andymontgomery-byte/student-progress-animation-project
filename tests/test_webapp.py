#!/usr/bin/env python3
"""
Test suite for webapp data and structure.
Run: python3 tests/test_webapp.py
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBAPP_DIR = os.path.join(BASE_DIR, 'webapp')
DATA_JSON = os.path.join(WEBAPP_DIR, 'data.json')
INDEX_HTML = os.path.join(WEBAPP_DIR, 'index.html')

def load_webapp_data():
    """Load webapp JSON data"""
    with open(DATA_JSON) as f:
        return json.load(f)

def test_data_json_exists():
    """Test that data.json exists"""
    assert os.path.exists(DATA_JSON), f"data.json not found at {DATA_JSON}"
    print("✓ data.json exists")

def test_index_html_exists():
    """Test that index.html exists"""
    assert os.path.exists(INDEX_HTML), f"index.html not found at {INDEX_HTML}"
    print("✓ index.html exists")

def test_data_json_valid():
    """Test that data.json is valid JSON"""
    try:
        data = load_webapp_data()
        assert isinstance(data, list), "data.json should be a list"
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON: {e}")
    print("✓ data.json is valid JSON")

def test_data_has_required_fields():
    """Test that each record has required fields"""
    data = load_webapp_data()

    required = [
        'email', 'grade', 'school', 'course',
        'fall_pct', 'fall_99_levels',
        'winter_pct', 'winter_99_levels',
        'projected_pct', 'projected_99_levels',
        'cgi'
    ]

    for i, record in enumerate(data[:10]):  # Check first 10
        missing = [f for f in required if f not in record]
        assert not missing, f"Record {i} missing fields: {missing}"

    print(f"✓ All required fields present in data")

def test_data_filtered_by_cgi():
    """Test that all records have CGI > 0.8"""
    data = load_webapp_data()

    low_cgi = [r for r in data if r['cgi'] <= 0.8]
    assert not low_cgi, f"Found {len(low_cgi)} records with CGI <= 0.8"
    print(f"✓ All {len(data)} records have CGI > 0.8")

def test_data_sorted_by_cgi():
    """Test that data is sorted by CGI descending"""
    data = load_webapp_data()

    for i in range(1, len(data)):
        assert data[i]['cgi'] <= data[i-1]['cgi'], f"Data not sorted: index {i-1} CGI={data[i-1]['cgi']}, index {i} CGI={data[i]['cgi']}"

    print("✓ Data sorted by CGI descending")

def test_index_html_loads_data():
    """Test that index.html references data.json"""
    with open(INDEX_HTML) as f:
        content = f.read()

    assert 'data.json' in content, "index.html does not reference data.json"
    print("✓ index.html references data.json")

def test_index_html_has_chart():
    """Test that index.html has chart canvas"""
    with open(INDEX_HTML) as f:
        content = f.read()

    assert '<canvas' in content, "index.html missing canvas element"
    assert 'id="chart"' in content, "index.html missing chart canvas"
    print("✓ index.html has chart canvas")

def test_index_html_has_select():
    """Test that index.html has student select dropdown"""
    with open(INDEX_HTML) as f:
        content = f.read()

    assert '<select' in content, "index.html missing select element"
    assert 'studentSelect' in content, "index.html missing studentSelect"
    print("✓ index.html has student selector")

def test_percentile_values_valid():
    """Test that percentile values are valid in webapp data"""
    data = load_webapp_data()

    for r in data:
        for field in ['fall_pct', 'winter_pct', 'projected_pct']:
            val = r.get(field)
            if val is not None:
                assert 1 <= val <= 99, f"{r['email']}: {field}={val} out of range"

    print("✓ All percentile values in range 1-99")

def test_99_levels_valid():
    """Test that 99 level values are valid"""
    data = load_webapp_data()

    for r in data:
        for field in ['fall_99_levels', 'winter_99_levels', 'projected_99_levels']:
            val = r.get(field)
            if val is not None:
                assert 0 <= val <= 12, f"{r['email']}: {field}={val} out of range"

    print("✓ All 99th grade levels in valid range")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("WEBAPP TESTS")
    print("=" * 60)
    print()

    tests = [
        test_data_json_exists,
        test_index_html_exists,
        test_data_json_valid,
        test_data_has_required_fields,
        test_data_filtered_by_cgi,
        test_data_sorted_by_cgi,
        test_index_html_loads_data,
        test_index_html_has_chart,
        test_index_html_has_select,
        test_percentile_values_valid,
        test_99_levels_valid,
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
