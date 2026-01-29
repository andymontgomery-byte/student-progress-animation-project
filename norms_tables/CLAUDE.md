# Norms Tables Extraction

## Goal
Extract the NWEA MAP norms tables from the PDF appendix that map RIT scores at each grade level to percentiles 1-99.

## Source
- `NormsTables.pdf` - NWEA 2020 MAP Growth Achievement Status and Growth Norms Tables

## Output
- `csv/student_status_percentiles.csv` - 13,365 rows mapping (subject, term, grade, percentile) → RIT score

## Data Structure

| Column | Description |
|--------|-------------|
| subject | Mathematics, Reading, Language Usage, Science |
| term | Fall, Winter, Spring |
| grade | K, 1-12 (varies by subject) |
| percentile | 1-99 |
| rit_score | The RIT score for that percentile |

## Coverage

| Subject | Grades | Rows |
|---------|--------|------|
| Mathematics | K-12 | 3,861 |
| Reading | K-12 | 3,861 |
| Language Usage | 2-11 | 2,970 |
| Science | 2-10 | 2,673 |

## Usage Example

To find what percentile a student is at:
1. Look up rows matching their subject, term, and grade
2. Find the row where their RIT score matches (or interpolate between rows)

To find the RIT needed for 99th percentile at a given grade:
```python
# Grade 4 Math, Fall, 99th percentile = RIT 233
row = df[(df.subject=='Mathematics') & (df.term=='Fall') &
         (df.grade=='4') & (df.percentile==99)]
```

## Notes
- Extracted from Appendix C.1 (Student Status Percentiles) of the PDF
- Tables C.1.1 through C.1.12 cover all subject/term combinations
- The PDF also contains School norms (Appendix C.2), Growth norms (Appendix B), and Conditional Growth distributions (Appendix D/E) which are not yet extracted
