# NWEA Projected Growth Comparison Tool

## Overview

Interactive tool to compare NWEA projected growth values between 2020 and 2025 norms by subject, growth period, grade, and starting RIT score.

## Live URL

https://andymontgomery-byte.github.io/student-progress-animation-project/projected_growth/

## Dimensions

### Subject
- Math
- Reading
- Language
- Science

### Growth Period
| Period | Description |
|--------|-------------|
| Fall to Fall | Year-over-year growth |
| Fall to Winter | Within-year growth (first half) |
| Winter to Winter | Year-over-year from winter |
| Fall to Spring | Full academic year |
| Winter to Spring | Within-year growth (second half) |
| Spring to Spring | Year-over-year from spring |

### Norms View
| View | Description | Color Coding |
|------|-------------|--------------|
| 2020 | 2020 norms projected growth | Dark green → Yellow (high → low) |
| 2025 | 2025 norms projected growth | Dark green → Yellow (high → low) |
| Diff (2025-2020) | Difference between norms | Dark green → Dark red (positive → negative), threshold at 0 |
| Ratio (2025/2020) | Ratio of norms | Dark green → Dark red (>1 → <1), threshold at 1.0 |

## Table Format

- **Rows**: Starting RIT score (ascending)
- **Columns**: Grade level (K through 12)
- **Values**: Projected growth in RIT points

## Data Source

Extracted from MAP export data:
- 2020 norms: Used for tests through Spring 2024-2025
- 2025 norms: Used for tests starting Fall 2025-2026

### Field Mapping
| Growth Period | CSV Field |
|---------------|-----------|
| Fall to Fall | `falltofallprojectedgrowth` |
| Fall to Winter | `falltowinterprojectedgrowth` |
| Winter to Winter | `wintertowinterprojectedgrowth` |
| Fall to Spring | `falltospringprojectedgrowth` |
| Winter to Spring | `wintertospringprojectedgrowth` |
| Spring to Spring | `springtospringprojectedgrowth` |

## 2020 vs 2025 Norms Comparison

### Key Findings

The 2025 norms generally show **higher projected growth** than 2020 norms, meaning:
- Students need to grow MORE to meet the same percentile targets
- The same amount of growth results in LOWER CGI scores
- Achievement percentiles are recalibrated to current student population

### Interpretation

| Diff Value | Meaning |
|------------|---------|
| Positive (green) | 2025 expects MORE growth than 2020 |
| Zero (white) | Same expectations |
| Negative (red) | 2025 expects LESS growth than 2020 |

| Ratio Value | Meaning |
|-------------|---------|
| > 1.0 (green) | 2025 expects MORE growth |
| = 1.0 (white) | Same expectations |
| < 1.0 (red) | 2025 expects LESS growth |

## Data Availability

### 2020 Norms
- All 6 growth periods available
- Data from 2017-2018 through 2024-2025 school years

### 2025 Norms
- Only Fall-to-Fall, Fall-to-Winter, Winter-to-Winter available
- Spring periods not yet available (current year is 2025-2026)
- Data from Fall 2025-2026 onward

## Algorithm

1. Load projected growth data from JSON
2. Filter by selected subject and growth period
3. Build grade × RIT matrix
4. Apply color coding based on norms view:
   - **2020/2025**: Map value range to green-yellow gradient
   - **Diff**: Map to red-green gradient with 0 as midpoint
   - **Ratio**: Map to red-green gradient with 1.0 as midpoint

## Files

```
docs/projected_growth/
├── index.html              # Main webapp
├── SPEC.md                 # This file
└── ../projected_growth_data.json  # Data file
```
