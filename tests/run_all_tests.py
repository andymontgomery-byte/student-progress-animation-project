#!/usr/bin/env python3
"""
Master regression test suite - runs ALL tests.
Run: python3 tests/run_all_tests.py

This is the single command to verify everything works.
"""

import sys
import os

# Add tests directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_norms_extraction import run_all_tests as test_norms
from test_table_building import run_all_tests as test_table
from test_webapp import run_all_tests as test_webapp
from test_compare_webapp import run_all_tests as test_compare
from test_webapp_browser import run_browser_tests as test_webapp_browser
from test_strata_browser import run_browser_tests as test_strata_browser
from test_compare_browser import run_browser_tests as test_compare_browser
from test_dropdown_visual import run_visual_dropdown_tests as test_dropdown_visual
from test_full_visual import run_all_visual_tests as test_full_visual
from test_10_students import run_student_tests as test_10_students

def main():
    print()
    print("=" * 70)
    print("REGRESSION TEST SUITE")
    print("=" * 70)
    print()
    print("This runs ALL tests to verify the entire system works.")
    print()

    results = {}

    # === DATA TESTS ===
    print("\n" + "=" * 70)
    print("PART 1: DATA TESTS")
    print("=" * 70)

    print("\n" + "-" * 50)
    results['norms_extraction'] = test_norms()

    print("\n" + "-" * 50)
    results['table_building'] = test_table()

    # === STRUCTURAL TESTS ===
    print("\n" + "=" * 70)
    print("PART 2: STRUCTURAL TESTS")
    print("=" * 70)

    print("\n" + "-" * 50)
    results['webapp_structure'] = test_webapp()

    print("\n" + "-" * 50)
    results['compare_structure'] = test_compare()

    # === BROWSER TESTS ===
    print("\n" + "=" * 70)
    print("PART 3: BROWSER TESTS (Playwright)")
    print("=" * 70)

    print("\n" + "-" * 50)
    results['main_browser'] = test_webapp_browser()

    print("\n" + "-" * 50)
    results['strata_browser'] = test_strata_browser()

    print("\n" + "-" * 50)
    results['compare_browser'] = test_compare_browser()

    # === VISUAL TESTS ===
    print("\n" + "=" * 70)
    print("PART 4: VISUAL TESTS (Screenshots)")
    print("=" * 70)

    print("\n" + "-" * 50)
    results['dropdown_visual'] = test_dropdown_visual()

    print("\n" + "-" * 50)
    results['full_visual'] = test_full_visual()

    # === COMPREHENSIVE STUDENT TESTS ===
    print("\n" + "=" * 70)
    print("PART 5: COMPREHENSIVE STUDENT TESTS (10+ students each)")
    print("=" * 70)

    print("\n" + "-" * 50)
    results['10_students'] = test_10_students()

    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("REGRESSION TEST SUMMARY")
    print("=" * 70)

    all_passed = True
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    print("=" * 70)
    if all_passed:
        print("ALL REGRESSION TESTS PASSED!")
        print("The system is verified working.")
    else:
        print("SOME TESTS FAILED - Review output above.")
    print("=" * 70)

    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
