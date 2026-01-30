# Test Use Cases

## Source: requirements.md

This document maps every requirement to user-facing use cases and their corresponding tests.

## Use Case Coverage: 22/22 (100%)

| Req ID | Requirement | Use Case | Test | Verified |
|--------|-------------|----------|------|----------|
| REQ-1 | Load MAP data xlsx files | System loads fall/winter xlsx data | test_table_building.py | Data rows match expected counts |
| REQ-2 | Extract norms tables (2020, 2025) | System extracts all subjects/terms/grades/percentiles | test_norms_extraction.py | 13,365 rows, all spot checks pass |
| REQ-3 | Table has student email | User data includes email identifier | test_table_building.test_no_empty_emails | No empty emails |
| REQ-4 | Table has grade level | User data includes grade (K-12) | test_table_building.test_all_grades_valid | All grades valid |
| REQ-5 | Table has school | User data includes school name | test_table_building.test_required_columns | Column exists |
| REQ-6 | Table has course/subject | User data includes course | test_table_building.test_all_courses_valid | 4 valid courses |
| REQ-7 | Starting percentile (fall) | User sees fall percentile on chart | test_visual_verification.py | Screenshot shows Fall data point |
| REQ-8 | Current percentile (winter) | User sees winter percentile on chart | test_visual_verification.py | Screenshot shows Winter data point |
| REQ-9 | Projected percentile (spring) | User sees projected spring percentile | test_visual_verification.py | Screenshot shows Spring data point |
| REQ-10 | 99th grade levels displayed | User sees 99+N levels for high performers | test_visual_verification.py | Screenshot shows "99+6" etc. |
| REQ-11 | CGI (Conditional Growth Index) | Data includes growth index | test_table_building.test_cgi_values_numeric | All CGI values numeric |
| REQ-12 | Filter for CGI > 0.8 | Only high-growth students in webapp | test_webapp.test_all_records_high_growth | 490 students, all CGI > 0.8 |
| REQ-13 | User selects student from dropdown | User picks student, chart updates | test_webapp_browser.test_selecting_student | Screenshot shows selected student |
| REQ-14 | User sees growth animation | Chart animates Fall→Winter→Spring | test_webapp_browser.test_animation | Animation triggered |
| REQ-15 | Y-axis shows 0-99 + 99th levels | User sees Y-axis: 0, 25, 50, 75, 99, 99+2... | test_chart_axes.test_y_axis_labels | Screenshot verified |
| REQ-16 | X-axis shows Fall, Winter, Spring | User sees X-axis with term labels | test_chart_axes.test_x_axis_labels | Screenshot verified |
| REQ-17 | Strata webapp: filtered schools | Only Strata schools appear | test_strata_browser.test_only_strata_schools | 5 schools only |
| REQ-18 | Compare: two side-by-side charts | User sees Student A and Student B charts | test_compare_browser.test_both_charts | Both canvases visible |
| REQ-19 | Compare: filter by school | User selects school, list filters | test_compare_browser.test_filter_by_school | Count updates |
| REQ-20 | Compare: filter by subject | User selects subject, list filters | test_compare_browser.test_filter_by_subject | Count updates |
| REQ-21 | Compare: filter by grade | User selects grade, list filters | test_compare_browser.test_filter_by_grade | Count updates |
| REQ-22 | Compare: combined filters | User applies school+subject+grade | test_compare_browser.test_combined_filtering | Count reflects all filters |

## Visual Verification Requirements

Each use case involving UI must have:
1. Screenshot taken after action
2. Screenshot reviewed with Claude vision
3. Visual confirmation that element renders correctly (not just exists in DOM)

## Cross-Browser Testing

Tests run in both:
- Chromium (Chrome/Edge)
- WebKit (Safari)

Screenshots captured in both browsers to catch rendering differences.

## How to Run

```bash
# Full regression suite (all use cases)
python3 tests/run_all_tests.py

# Visual verification with screenshots
python3 tests/test_visual_verification.py

# Chart axis verification
python3 tests/test_chart_axes.py
```

## Gaps Identified and Resolved

| Date | Gap | Resolution |
|------|-----|------------|
| 2026-01-30 | Safari multi-select rendered blank checkboxes | Changed to single-select, added cross-browser tests |
| 2026-01-30 | No explicit Y-axis/X-axis label verification | Added test_chart_axes.py |
| 2026-01-30 | No use case documentation | Created this USE_CASES.md |
