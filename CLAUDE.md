# Student Progress Animation

## Overview
Web app showing student growth animations for high-growth MAP test takers (CGI > 0.8).

## Live URL
https://andymontgomery-byte.github.io/student-progress-animation-project/

## Project Structure
```
student_progress_animation/
├── CLAUDE.md                    # This file
├── requirements.md              # Project requirements
├── .gitignore                   # Git ignore rules
├── data/
│   ├── input/                   # Raw data (checked in)
│   │   ├── fall_data.xlsx
│   │   └── winter_data.xlsx
│   └── output/                  # Generated (NOT checked in)
│       └── student_progress.csv
├── norms_tables/
│   ├── CLAUDE.md                # Norms extraction docs
│   ├── NormsTables.pdf          # NWEA 2020 norms (NOT checked in, too large)
│   ├── norms_2025.xlsx          # NWEA 2025 norms (checked in)
│   ├── norms_comparison.html    # 2020 vs 2025 visual comparison
│   ├── csv/
│   │   ├── student_status_percentiles.csv       # 2020 norms (13,365 rows)
│   │   └── student_status_percentiles_2025.csv  # 2025 norms (13,365 rows)
│   ├── test_extraction.py       # 2020 norms tests (8 tests)
│   └── test_extraction_2025.py  # 2025 norms tests (10 tests)
├── docs/                        # GitHub Pages (was: webapp/)
│   ├── index.html               # Web app (checked in)
│   └── data.json                # Filtered data (NOT checked in, generated)
└── tests/
    ├── run_all_tests.py         # Master test runner
    ├── test_norms_extraction.py # 8 tests
    ├── test_table_building.py   # 11 tests
    └── test_webapp.py           # 11 tests
```

## What's Checked In vs Not

| Checked In | NOT Checked In (generated/large) |
|------------|----------------------------------|
| `data/input/*.xlsx` | `data/output/*` |
| `norms_tables/csv/*` | `norms_tables/*.pdf` |
| `webapp/index.html` | `webapp/data.json` |
| `tests/*` | `__pycache__/` |
| `*.md`, `.gitignore` | `.claude/` |

## Workflow for New Data

### 1. Drop in new data files
Replace files in `data/input/`:
- `fall_data.xlsx` - columns: email, course, grade, districtname, schoolname, termname, testritscore, testpercentile
- `winter_data.xlsx` - columns: email, course, grade, districtname, schoolname, termname, falltowinterconditionalgrowthindex, testritscore, testpercentile, falltowinterobservedgrowth

### 2. If new norms tables
- Copy PDF to `norms_tables/`
- DO NOT read PDF directly (too large) - break into chunks first
- Re-extract to CSV
- Run: `python3 norms_tables/test_extraction.py`

### 3. Rebuild the table
Ask Claude to rebuild `data/output/student_progress.csv` from the new data files.

### 4. Run all tests
```bash
python3 tests/run_all_tests.py
```

### 5. Update webapp and deploy
```bash
# Regenerate webapp/data.json (Claude will do this)
# Then push to GitHub
git add .
git commit -m "Update data"
git push
```

## Key Metrics
- Total student/subject combinations: 361
- High-growth (CGI > 0.8): 188 (52.1%)
- Subjects: Math K-12, Reading, Language Usage, Science K-12
- Grades: K-12

## Test Coverage
- **Norms extraction**: 8 tests (subjects, terms, percentiles, grades, RIT ranges, monotonicity, row counts, spot checks)
- **Table building**: 11 tests (columns, validity, ranges, CGI filter, uniqueness)
- **Webapp**: 11 tests (files exist, JSON valid, filtering, sorting, HTML structure)

Run all tests: `python3 tests/run_all_tests.py`

## Lessons Learned

### Always run tests before claiming something works
- Don't assume extraction/transformation worked just because it ran without errors
- Run the full test suite after every change
- Spot checks alone are not sufficient - they can miss systematic errors

### Use aggregation to verify table data
When working with tables, verify with multiple methods:
1. **Spot checks**: Random individual cell comparisons
2. **Row sums**: Sum across all columns for specific rows
3. **Column sums**: Sum across all rows for specific columns
4. **Total sums**: Sum of entire table by category
5. **Count checks**: Verify expected number of rows/columns

Example: The 2025 norms extraction initially missed Kindergarten (grade 0). Spot checks passed because they only tested grades 1-12. The aggregate sum check caught the bug because the total was lower than expected.

### Test at multiple levels
- Unit tests: Individual functions
- Integration tests: Data flows between components
- Aggregate tests: Overall data integrity
- Source comparison: Verify against original source files
