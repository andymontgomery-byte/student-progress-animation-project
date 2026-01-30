# Student Progress Animation

## Overview
Web app showing student growth animations for high-growth MAP test takers (CGI > 0.8).

## Live URLs
- **Main webapp:** https://andymontgomery-byte.github.io/student-progress-animation-project/
- **Strata webapp:** https://andymontgomery-byte.github.io/student-progress-animation-project/strata/
- **Compare webapp:** https://andymontgomery-byte.github.io/student-progress-animation-project/compare/
- **Norms comparison:** https://andymontgomery-byte.github.io/student-progress-animation-project/norms_comparison.html

## Project Structure
```
student_progress_animation/
├── CLAUDE.md                    # This file
├── requirements.md              # Project requirements
├── .gitignore                   # Git ignore rules
├── data/
│   ├── input/                   # Raw data (checked in)
│   │   ├── fall_data.xlsx
│   │   ├── winter_data.xlsx
│   │   └── archive_2025-01-29/  # Previous data files
│   └── output/                  # Generated (NOT checked in)
│       ├── student_progress.csv
│       ├── student_progress_2020.csv  # Table built with 2020 norms (for QC)
│       └── student_progress_2025_old.csv  # Previous 2025 table
├── scripts/
│   └── build_table.py           # Builds student_progress.csv from data + norms
├── norms_tables/
│   ├── CLAUDE.md                # Norms extraction docs
│   ├── NormsTables.pdf          # NWEA 2020 norms (NOT checked in, too large)
│   ├── norms_2025.xlsx          # NWEA 2025 norms (checked in)
│   ├── norms_comparison.html    # 2020 vs 2025 visual comparison
│   ├── csv/
│   │   ├── student_status_percentiles.csv       # 2020 norms (13,365 rows)
│   │   ├── student_status_percentiles_2025.csv  # 2025 norms (13,365 rows)
│   │   ├── norms_2020_matrix.csv                # 2020 matrix format
│   │   ├── norms_2025_matrix.csv                # 2025 matrix format
│   │   └── norms_diff_matrix.csv                # 2025-2020 differences
│   ├── test_extraction.py       # 2020 norms tests (8 tests)
│   └── test_extraction_2025.py  # 2025 norms tests (10 tests)
├── docs/                        # GitHub Pages
│   ├── index.html               # Main web app
│   ├── data.json                # Filtered data for main app (CGI > 0.8)
│   ├── norms_comparison.html    # 2020 vs 2025 norms diff table
│   ├── strata/                  # Strata-only webapp
│   │   ├── index.html
│   │   └── data.json
│   └── compare/                 # Side-by-side comparison webapp
│       └── index.html           # Uses ../data.json
└── tests/
    ├── run_all_tests.py           # Master test runner (75 tests)
    ├── test_norms_extraction.py   # 8 tests
    ├── test_table_building.py     # 11 tests
    ├── test_webapp.py             # 11 structural tests
    ├── test_compare_webapp.py     # 11 structural tests
    ├── test_webapp_browser.py     # 8 browser tests (Playwright)
    ├── test_strata_browser.py     # 7 browser tests (Playwright)
    └── test_compare_browser.py    # 19 browser tests (Playwright)
```

## What's Checked In vs Not

| Checked In | NOT Checked In (generated/large) |
|------------|----------------------------------|
| `data/input/*.xlsx` | `data/output/*` |
| `norms_tables/csv/*` | `norms_tables/*.pdf` |
| `webapp/index.html` | `webapp/data.json` |
| `tests/*` | `__pycache__/` |
| `*.md`, `.gitignore` | `.claude/` |

## Quick Reference: Processing New Score Data

When user provides new xlsx files, run these steps:

```bash
# 1. Archive old data
mkdir -p data/input/archive_$(date +%Y-%m-%d)
mv data/input/fall_data.xlsx data/input/archive_$(date +%Y-%m-%d)/
mv data/input/winter_data.xlsx data/input/archive_$(date +%Y-%m-%d)/

# 2. Copy new files (user will provide paths)
cp "/path/to/fall_file.xlsx" data/input/fall_data.xlsx
cp "/path/to/winter_file.xlsx" data/input/winter_data.xlsx

# 3. Rebuild the student progress table
python3 scripts/build_table.py

# 4. Run tests
python3 tests/run_all_tests.py

# 5. Update webapp JSON files (see Python code below)

# 6. Push to GitHub
git add data/input/*.xlsx docs/data.json docs/strata/
git commit -m "Update with new score data"
git push
```

### Python: Update Webapp JSON Files
Run this after rebuilding the table:
```python
import csv, json

# Load table
data = []
with open('data/output/student_progress.csv') as f:
    for row in csv.DictReader(f):
        data.append({
            'email': row['email'],
            'grade': row['grade'],
            'school': row['school'],
            'course': row['course'],
            'fall_pct': int(row['fall_pct']) if row['fall_pct'] else None,
            'fall_99_levels': int(row['fall_99_levels']) if row['fall_99_levels'] else 0,
            'winter_pct': int(row['winter_pct']) if row['winter_pct'] else None,
            'winter_99_levels': int(row['winter_99_levels']) if row['winter_99_levels'] else 0,
            'projected_pct': int(row['projected_pct']) if row['projected_pct'] else None,
            'projected_99_levels': int(row['projected_99_levels']) if row['projected_99_levels'] else 0,
            'cgi': float(row['cgi']) if row['cgi'] else None
        })

# Main webapp (CGI > 0.8)
filtered = sorted([r for r in data if r['cgi'] and r['cgi'] > 0.8], key=lambda r: r['cgi'], reverse=True)
with open('docs/data.json', 'w') as f:
    json.dump(filtered, f, indent=2)

# Strata webapp
STRATA_SCHOOLS = {'AIE Elite Prep', 'All American Prep', 'DeepWater Prep', 'Modern Samurai Academy', 'The Bennett School'}
strata = sorted([r for r in filtered if r['school'] in STRATA_SCHOOLS], key=lambda r: r['cgi'], reverse=True)
with open('docs/strata/data.json', 'w') as f:
    json.dump(strata, f, indent=2)

print(f"Main: {len(filtered)} | Strata: {len(strata)}")
```

## Data File Formats

### Input Excel Files
Both files have: Row 1 = title, Row 2 = blank, Row 3 = headers, Row 4+ = data

**fall_data.xlsx columns:**
| Column | Description |
|--------|-------------|
| email | Student email |
| course | Math K-12, Reading, Language Usage, Science K-12 |
| grade | K, 1-12 (may be null for some records) |
| districtname | District name |
| schoolname | School name |
| termname | Term (Fall) |
| testritscore | RIT score |
| testpercentile | Achievement percentile (1-99) |

**winter_data.xlsx columns:**
| Column | Description |
|--------|-------------|
| email | Student email |
| course | Math K-12, Reading, Language Usage, Science K-12 |
| grade | K, 1-12 |
| districtname | District name |
| schoolname | School name |
| termname | Term (Winter) |
| falltowinterconditionalgrowthindex | CGI - std devs above expected growth |
| testritscore | Winter RIT score |
| testpercentile | Winter achievement percentile |
| falltowinterobservedgrowth | RIT point gain from fall to winter |

### Course to Subject Mapping
```python
COURSE_TO_SUBJECT = {
    'Math K-12': 'Mathematics',
    'Reading': 'Reading',
    'Language Usage': 'Language Usage',
    'Science K-12': 'Science'
}
```

### Norms CSV Files
Located in `norms_tables/csv/`:
| File | Description |
|------|-------------|
| `student_status_percentiles.csv` | 2020 norms (subject, term, grade, percentile, rit_score) |
| `student_status_percentiles_2025.csv` | 2025 norms (same format) |
| `norms_2020_matrix.csv` | 2020 in matrix format (rows=percentiles, cols=subject/term/grade) |
| `norms_2025_matrix.csv` | 2025 in matrix format |
| `norms_diff_matrix.csv` | 2025-2020 difference (positive=harder, negative=easier) |

## Workflow for New Data (Detailed)

### 1. Archive old data and drop in new files
```bash
# Archive old data
mkdir -p data/input/archive_YYYY-MM-DD
mv data/input/fall_data.xlsx data/input/archive_YYYY-MM-DD/
mv data/input/winter_data.xlsx data/input/archive_YYYY-MM-DD/

# Copy new files
cp /path/to/new_fall_data.xlsx data/input/fall_data.xlsx
cp /path/to/new_winter_data.xlsx data/input/winter_data.xlsx
```

### 2. If new norms tables
See "Building and Testing Norms Tables" section below.

### 3. Rebuild the table
```bash
python3 scripts/build_table.py
```
This builds `data/output/student_progress.csv` using 2025 norms.

### 4. Run all tests
```bash
python3 tests/run_all_tests.py
```

### 5. Update webapp data and deploy
```bash
# Update docs/data.json and docs/strata/data.json (use Python code above)
# Then push to GitHub
git add data/input/*.xlsx docs/data.json docs/strata/data.json
git commit -m "Update data"
git push
```

## Key Metrics (as of 2025-01-29)
- Fall records: 5,782
- Winter records: 889
- Total student/subject combinations with CGI: 889
- High-growth (CGI > 0.8): 490 (55.1%)
- Subjects: Math K-12, Reading, Language Usage, Science K-12
- Grades: K-12

## Compare Webapp

**Build:** Side-by-side comparison webapp at `/compare/` showing two student animations simultaneously.

**Features:**
- Two independent chart panels (Student A and Student B)
- Filter dropdowns for school, subject, and grade
- Student count updates as filters are applied
- Dropdown shows starting percentile: `Name - Subject G# (Start: P##, CGI: #.##)`
- Sorted by CGI descending

**Verify before delivering:**
1. All filter dropdowns populate from data
2. Filtering reduces student count correctly
3. Combined filters work (school + subject + grade)
4. Selecting student in either panel displays chart
5. Both panels work independently
6. Browser tests pass: `python3 tests/test_compare_browser.py`

## Strata Webapp

**Build:** Create a filtered webapp at `/strata/` showing only students from Strata schools with CGI > 0.8.

**Strata schools:**
- AIE Elite Prep
- All American Prep
- DeepWater Prep
- Modern Samurai Academy
- The Bennett School

**Verify before delivering:**
1. All records in `docs/strata/data.json` have school in Strata list
2. All records have CGI > 0.8
3. Sorted by CGI descending

## Building and Testing Norms Tables

### Build
Extract norms from Excel to CSV with columns: subject, term, grade, percentile, rit_score

### Verify before delivering
1. Row count = 13,365 (Math/Reading 13 grades × 3 terms × 99 pct + Language 10 + Science 9)
2. Aggregate sums by subject match Excel source
3. Run test suite: `python3 norms_tables/test_extraction_2025.py`

---

## Building Norms Diff Table

### Build
Create a comparison table showing 2025 RIT minus 2020 RIT for each subject/term/grade/percentile. Color code: green = harder (positive), red = easier (negative).

### Verify before delivering
1. Cell count = 13,365
2. Parse the output back to data and verify each cell = norms_2025[key] - norms_2020[key]
3. Spot check 10+ random cells manually
4. Sum all diffs by subject and verify totals

## Comparing Old vs New Data

When new data files arrive, compare before replacing:
```python
from openpyxl import load_workbook

def compare_xlsx(old_path, new_path, name):
    def load(path):
        wb = load_workbook(path)
        ws = wb.active
        headers = None
        data = {}
        for row in ws.iter_rows(values_only=True):
            if row[0] == 'email':
                headers = row
                continue
            if headers and row[0]:
                rec = dict(zip(headers, row))
                key = (rec['email'], rec['course'])
                data[key] = rec
        return data

    old, new = load(old_path), load(new_path)
    print(f"{name}: {len(old)} -> {len(new)} ({len(new)-len(old):+d})")
    print(f"  Only in old: {len(set(old.keys()) - set(new.keys()))}")
    print(f"  Only in new: {len(set(new.keys()) - set(old.keys()))}")
```

## Test Coverage

### Structural Tests (41 tests)
- **Norms extraction**: 8 tests (subjects, terms, percentiles, grades, RIT ranges, monotonicity, row counts, spot checks)
- **Table building**: 11 tests (columns, validity, ranges, CGI filter, uniqueness)
- **Webapp**: 11 tests (files exist, JSON valid, filtering, sorting, HTML structure)
- **Compare webapp**: 11 tests (two charts, filters, student selects, data loading)

### Browser Tests with Playwright (34 tests)
These test actual browser functionality, not just HTML structure:
- **Main webapp browser**: 8 tests (page loads, data loads, console errors, dropdown, canvas, student selection, animation)
- **Strata webapp browser**: 7 tests (page loads, data loads, Strata-only schools, CGI threshold, student selection)
- **Compare webapp browser**: 19 tests (page loads, all filters populate, filtering works, student counts, dropdowns show percentile, both charts work independently, animations)

### Visual Dropdown Tests
`test_dropdown_visual.py` - catches rendering bugs that programmatic tests miss:
- Takes screenshots of dropdowns while open
- Flags multi-select elements (which have cross-browser rendering issues)
- Verifies option text is visually present, not just programmatically

Run: `python3 tests/test_dropdown_visual.py`

Run all tests: `python3 tests/run_all_tests.py`

### Playwright Requirements
Browser tests require Playwright. Already installed at:
`/Library/Frameworks/Python.framework/Versions/3.11/bin/playwright`

If needed: `pip3 install playwright && playwright install`

## Lessons Learned

### Programmatic tests can pass while visual rendering fails
- **Critical bug found**: Schools dropdown showed checkboxes with BLANK labels in Safari
- Programmatic test: `select.options` had 28 items with correct text ✓
- Visual reality: Users saw empty checkboxes with no text ✗
- **Root cause**: `<select multiple size="1">` renders differently across browsers
- **Fix**: Use visual tests that take screenshots of open dropdowns
- **Rule**: If users interact with it visually, test it visually

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

### Excel extraction gotchas
- **Grade 0 is Kindergarten**: In Excel, grade 0 means K. Convert `'0'` to `'K'`.
- **0 is falsy in Python**: Use `if cell is not None` not `if cell` when checking Excel values, because grade 0 is a valid value but evaluates to False.
- **Row/column indexing**: Excel row 1 = index 0 in most libraries. Double-check header rows.
- **Verify with multiple methods**: Extract the same data using different libraries (openpyxl vs pandas) and compare results.

### PDF extraction gotchas
- **Large PDFs crash context**: Break into chunks before reading.
- **Table layouts vary**: Headers may span multiple rows, columns may be merged.
- **Spot checks aren't enough**: Use aggregate sums to catch missing sections.
- **Test suite is essential**: 240 random spot checks + structure verification.
- **Full re-extraction verified**: 2020 norms re-extracted using pypdf, 13,365/13,365 (100%) match CSV.

### Verification confidence levels
- **2025 Excel norms**: HIGH - verified 3 ways (openpyxl, pandas, cell-by-cell)
- **2020 PDF norms**: HIGH - full re-extraction matches 100%, plus 240 spot checks
- **Diff matrix**: HIGH - computed from verified source CSVs
