#!/usr/bin/env python3
"""
Generate norms_comparison.html with diff/ratio toggle.

Stores both 2020 and 2025 RIT values as data attributes so JavaScript
can compute either:
- Diff mode: 2025 - 2020 (negative = easier in 2025)
- Ratio mode: 2025 / 2020 (< 1.0 = easier in 2025)
"""

import csv
from collections import defaultdict

# Load both norms files
norms_2020 = defaultdict(dict)
norms_2025 = defaultdict(dict)

with open('/Users/andymontgomery/projects/student_progress_animation/norms_tables/csv/student_status_percentiles.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row['subject'], row['term'], row['grade'], int(row['percentile']))
        norms_2020[key] = int(row['rit_score'])

with open('/Users/andymontgomery/projects/student_progress_animation/norms_tables/csv/student_status_percentiles_2025.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row['subject'], row['term'], row['grade'], int(row['percentile']))
        norms_2025[key] = int(row['rit_score'])

# Calculate stats
total_cells = 0
easier = 0
same = 0
harder = 0
total_diff = 0

for key in norms_2020:
    if key in norms_2025:
        diff = norms_2025[key] - norms_2020[key]
        total_cells += 1
        total_diff += diff
        if diff < 0:
            easier += 1
        elif diff > 0:
            harder += 1
        else:
            same += 1

mean_diff = total_diff / total_cells if total_cells else 0

# Generate HTML
html = '''<!DOCTYPE html>
<html>
<head>
<title>2020 vs 2025 Norms Comparison</title>
<style>
body { font-family: -apple-system, sans-serif; padding: 20px; background: #1a1a2e; color: #fff; }
h1, h2, h3 { margin-top: 30px; }
table { border-collapse: collapse; margin: 20px 0; font-size: 12px; }
th, td { padding: 4px 8px; text-align: center; border: 1px solid #333; min-width: 35px; }
th { background: #16213e; position: sticky; top: 0; }
.grade-header { background: #2d3a5a; }
.pct-col { background: #16213e; font-weight: bold; }
.up { background: #1b5e20; color: #81c784; }
.down { background: #b71c1c; color: #ef9a9a; }
.same { background: #37474f; color: #90a4ae; }
.na { background: #263238; color: #546e7a; }
.legend { display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 8px; }
.legend-box { width: 20px; height: 20px; }
.summary { background: #16213e; padding: 15px; border-radius: 8px; margin: 20px 0; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0; }
.stat-box { background: #16213e; padding: 15px; border-radius: 8px; text-align: center; }
.stat-value { font-size: 24px; font-weight: bold; }
.stat-label { font-size: 12px; color: #888; }

/* Toggle switch styles */
.toggle-container {
    display: flex;
    align-items: center;
    gap: 15px;
    margin: 20px 0;
    padding: 15px;
    background: #16213e;
    border-radius: 8px;
    width: fit-content;
}
.toggle-label {
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    padding: 5px 10px;
    border-radius: 4px;
    transition: background 0.2s;
}
.toggle-label.active {
    background: #4472C4;
}
.toggle-label:hover:not(.active) {
    background: #333;
}
.toggle-switch {
    position: relative;
    width: 60px;
    height: 30px;
    background: #333;
    border-radius: 15px;
    cursor: pointer;
    transition: background 0.3s;
}
.toggle-switch.ratio {
    background: #4472C4;
}
.toggle-switch::after {
    content: '';
    position: absolute;
    width: 26px;
    height: 26px;
    background: #fff;
    border-radius: 50%;
    top: 2px;
    left: 2px;
    transition: transform 0.3s;
}
.toggle-switch.ratio::after {
    transform: translateX(30px);
}
.mode-description {
    font-size: 12px;
    color: #888;
    margin-top: 10px;
}
</style>
</head>
<body>
<h1>2020 → 2025 Norms Delta</h1>
<p>Shows change in RIT score required for each percentile.</p>

<div class="toggle-container">
    <span class="toggle-label active" id="diff-label" onclick="setMode('diff')">Diff (2025−2020)</span>
    <div class="toggle-switch" id="toggle" onclick="toggleMode()"></div>
    <span class="toggle-label" id="ratio-label" onclick="setMode('ratio')">Ratio (2025÷2020)</span>
</div>
<div class="mode-description" id="mode-desc">
    <span id="diff-desc"><b>Diff mode:</b> Negative = easier to achieve in 2025 (lower RIT needed)</span>
    <span id="ratio-desc" style="display:none"><b>Ratio mode:</b> &lt;1.0 = easier in 2025, &gt;1.0 = harder in 2025</span>
</div>

<div class="legend">
<div class="legend-item"><div class="legend-box up"></div> <span id="legend-up">2025 higher (harder)</span></div>
<div class="legend-item"><div class="legend-box same"></div> <span id="legend-same">Same</span></div>
<div class="legend-item"><div class="legend-box down"></div> <span id="legend-down">2025 lower (easier)</span></div>
</div>

<div class="stats">
<div class="stat-box"><div class="stat-value down">''' + f'{easier:,}' + '''</div><div class="stat-label">Easier in 2025</div></div>
<div class="stat-box"><div class="stat-value same">''' + f'{same:,}' + '''</div><div class="stat-label">Same</div></div>
<div class="stat-box"><div class="stat-value up">''' + f'{harder:,}' + '''</div><div class="stat-label">Harder in 2025</div></div>
<div class="stat-box"><div class="stat-value">''' + f'{mean_diff:.2f}' + '''</div><div class="stat-label">Mean Change</div></div>
</div>
'''

# Generate tables for each subject and term
subjects = ['Mathematics', 'Reading', 'Language Usage', 'Science']
terms = ['Fall', 'Winter', 'Spring']

# Grade ranges by subject
grade_ranges = {
    'Mathematics': ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
    'Reading': ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
    'Language Usage': ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
    'Science': ['2', '3', '4', '5', '6', '7', '8', '9', '10']
}

for subject in subjects:
    html += f'<h2>{subject}</h2>\n'
    grades = grade_ranges[subject]

    for term in terms:
        html += f'<h3>{term}</h3>\n'
        html += '<table>\n'

        # Header row
        html += '<tr><th>Pct</th>'
        for grade in grades:
            html += f'<th class="grade-header">Gr {grade}</th>'
        html += '</tr>\n'

        # Data rows (99 down to 1)
        for pct in range(99, 0, -1):
            html += f'<tr><td class="pct-col">{pct}</td>'

            for grade in grades:
                key = (subject, term, grade, pct)
                v2020 = norms_2020.get(key)
                v2025 = norms_2025.get(key)

                if v2020 is not None and v2025 is not None:
                    diff = v2025 - v2020

                    if diff > 0:
                        css_class = 'up'
                        diff_text = f'+{diff}'
                    elif diff < 0:
                        css_class = 'down'
                        diff_text = str(diff)
                    else:
                        css_class = 'same'
                        diff_text = '0'

                    # Store both values as data attributes
                    html += f'<td class="{css_class}" data-v2020="{v2020}" data-v2025="{v2025}">{diff_text}</td>'
                else:
                    html += '<td class="na">—</td>'

            html += '</tr>\n'

        html += '</table>\n'

# Add JavaScript for toggle functionality
html += '''
<script>
let currentMode = 'diff';

function toggleMode() {
    setMode(currentMode === 'diff' ? 'ratio' : 'diff');
}

function setMode(mode) {
    currentMode = mode;
    const toggle = document.getElementById('toggle');
    const diffLabel = document.getElementById('diff-label');
    const ratioLabel = document.getElementById('ratio-label');
    const diffDesc = document.getElementById('diff-desc');
    const ratioDesc = document.getElementById('ratio-desc');
    const legendUp = document.getElementById('legend-up');
    const legendSame = document.getElementById('legend-same');
    const legendDown = document.getElementById('legend-down');

    if (mode === 'ratio') {
        toggle.classList.add('ratio');
        diffLabel.classList.remove('active');
        ratioLabel.classList.add('active');
        diffDesc.style.display = 'none';
        ratioDesc.style.display = 'inline';
        legendUp.textContent = 'Ratio > 1.0 (harder)';
        legendSame.textContent = 'Ratio = 1.0';
        legendDown.textContent = 'Ratio < 1.0 (easier)';
    } else {
        toggle.classList.remove('ratio');
        diffLabel.classList.add('active');
        ratioLabel.classList.remove('active');
        diffDesc.style.display = 'inline';
        ratioDesc.style.display = 'none';
        legendUp.textContent = '2025 higher (harder)';
        legendSame.textContent = 'Same';
        legendDown.textContent = '2025 lower (easier)';
    }

    updateAllCells();
}

function updateAllCells() {
    const cells = document.querySelectorAll('td[data-v2020]');

    cells.forEach(cell => {
        const v2020 = parseInt(cell.dataset.v2020);
        const v2025 = parseInt(cell.dataset.v2025);

        if (currentMode === 'diff') {
            // Diff mode: 2025 - 2020
            const diff = v2025 - v2020;

            if (diff > 0) {
                cell.className = 'up';
                cell.textContent = '+' + diff;
            } else if (diff < 0) {
                cell.className = 'down';
                cell.textContent = diff;
            } else {
                cell.className = 'same';
                cell.textContent = '0';
            }
        } else {
            // Ratio mode: 2025 / 2020
            // Use actual ratio for color (consistent with diff mode)
            // but display rounded value for readability
            const ratio = v2025 / v2020;
            const ratioText = ratio.toFixed(2);

            // Color based on actual ratio, not rounded
            // This ensures green/red matches diff mode exactly
            if (v2025 > v2020) {
                cell.className = 'up';
                cell.textContent = ratioText;
            } else if (v2025 < v2020) {
                cell.className = 'down';
                cell.textContent = ratioText;
            } else {
                cell.className = 'same';
                cell.textContent = '1.00';
            }
        }
    });
}
</script>
</body>
</html>
'''

# Write to file
output_path = '/Users/andymontgomery/projects/student_progress_animation/docs/norms_comparison.html'
with open(output_path, 'w') as f:
    f.write(html)

print(f"Generated: {output_path}")
print(f"Total cells: {total_cells}")
print(f"Easier in 2025: {easier}")
print(f"Same: {same}")
print(f"Harder in 2025: {harder}")
print(f"Mean change: {mean_diff:.2f}")
