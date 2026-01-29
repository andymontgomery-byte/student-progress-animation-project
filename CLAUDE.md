# Student Progress Animation

## Overview
Web app showing student growth animations for high-growth MAP test takers (CGI > 0.8).

## Live URL
https://andymontgomery-byte.github.io/student-progress-animation/

## Project Structure
```
student_progress_animation/
├── CLAUDE.md                    # This file
├── requirements.md              # Project requirements
├── student_progress.csv         # Built table (361 records)
├── norms_tables/
│   ├── CLAUDE.md                # Norms extraction docs
│   ├── NormsTables.pdf          # NWEA 2020 norms (465 pages)
│   ├── csv/
│   │   └── student_status_percentiles.csv  # Extracted norms (13,365 rows)
│   └── test_extraction.py       # Norms extraction tests
├── webapp/
│   ├── index.html               # Web app
│   └── data.json                # Filtered data (188 records, CGI > 0.8)
└── tests/
    ├── run_all_tests.py         # Master test runner
    ├── test_norms_extraction.py # 8 tests
    ├── test_table_building.py   # 11 tests
    └── test_webapp.py           # 11 tests
```

## Workflow for New Data

### 1. Drop in new data files
Place Excel files in Downloads:
- Fall data: `Email,_Course,_Grade_*.xlsx` with columns: email, course, grade, districtname, schoolname, termname, testritscore, testpercentile
- Winter data: `Email,_Course,_Grade_*.xlsx` with columns: email, course, grade, districtname, schoolname, termname, falltowinterconditionalgrowthindex, testritscore, testpercentile, falltowinterobservedgrowth

### 2. If new norms tables
- Copy PDF to `norms_tables/`
- DO NOT read PDF directly (too large) - break into chunks first
- Re-extract to CSV
- Run: `python3 norms_tables/test_extraction.py`

### 3. Rebuild the table
Ask Claude to rebuild `student_progress.csv` from the new data files.

### 4. Run all tests
```bash
python3 tests/run_all_tests.py
```

### 5. Update webapp and deploy
```bash
# Regenerate webapp data
# (Claude will do this)

# Push to GitHub
cd webapp
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
