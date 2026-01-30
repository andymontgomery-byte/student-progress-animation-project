#!/usr/bin/env python3
"""
Master test runner - runs all test suites.
Run: python3 tests/run_all_tests.py
"""

import sys
import os

# Add tests directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_norms_extraction import run_all_tests as test_norms
from test_table_building import run_all_tests as test_table
from test_webapp import run_all_tests as test_webapp
from test_compare_webapp import run_all_tests as test_compare

def main():
    print()
    print("=" * 60)
    print("RUNNING ALL TEST SUITES")
    print("=" * 60)
    print()

    results = {}

    # Run norms extraction tests
    print("\n" + "=" * 60)
    results['norms'] = test_norms()

    # Run table building tests
    print("\n" + "=" * 60)
    results['table'] = test_table()

    # Run webapp tests
    print("\n" + "=" * 60)
    results['webapp'] = test_webapp()

    # Run comparison webapp tests
    print("\n" + "=" * 60)
    results['compare'] = test_compare()

    # Summary
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All test suites passed!")
    else:
        print("Some tests failed. Review output above.")

    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
