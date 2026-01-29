#!/usr/bin/env python3
"""
Test suite to verify norms table extraction from PDF.
Compares 10 random samples from each of 24 PDF pages against the extracted CSV.
"""

from pypdf import PdfReader
import csv
import random

def load_csv_data(csv_path):
    """Load extracted CSV data into lookup dict"""
    data = {}
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['subject'], row['term'], row['grade'], int(row['percentile']))
            data[key] = int(row['rit_score'])
    return data

def parse_pdf_row(line, grades):
    """Parse a row from the PDF and return {grade: (percentile, rit)}"""
    parts = line.split()
    result = {}
    if len(parts) >= len(grades) + 1:
        try:
            pct = int(parts[0])
            if 1 <= pct <= 99:
                for i, grade in enumerate(grades):
                    if i + 1 < len(parts):
                        try:
                            rit = int(parts[i + 1])
                            if 100 <= rit <= 350:
                                result[grade] = (pct, rit)
                        except ValueError:
                            pass
        except ValueError:
            pass
    return result

def run_tests(pdf_path, csv_path, samples_per_page=10, seed=42):
    """Run extraction verification tests"""
    csv_data = load_csv_data(csv_path)
    print(f"Loaded {len(csv_data)} rows from CSV\n")

    # Table definitions: page (0-indexed), subject, term, grades
    tables_info = [
        {'page': 20, 'subject': 'Mathematics', 'term': 'Fall', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 21, 'subject': 'Mathematics', 'term': 'Fall', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 22, 'subject': 'Mathematics', 'term': 'Winter', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 23, 'subject': 'Mathematics', 'term': 'Winter', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 24, 'subject': 'Mathematics', 'term': 'Spring', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 25, 'subject': 'Mathematics', 'term': 'Spring', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 26, 'subject': 'Reading', 'term': 'Fall', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 27, 'subject': 'Reading', 'term': 'Fall', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 28, 'subject': 'Reading', 'term': 'Winter', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 29, 'subject': 'Reading', 'term': 'Winter', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 30, 'subject': 'Reading', 'term': 'Spring', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 31, 'subject': 'Reading', 'term': 'Spring', 'grades': ['K'] + [str(i) for i in range(1, 13)]},
        {'page': 32, 'subject': 'Language Usage', 'term': 'Fall', 'grades': [str(i) for i in range(2, 12)]},
        {'page': 33, 'subject': 'Language Usage', 'term': 'Fall', 'grades': [str(i) for i in range(2, 12)]},
        {'page': 34, 'subject': 'Language Usage', 'term': 'Winter', 'grades': [str(i) for i in range(2, 12)]},
        {'page': 35, 'subject': 'Language Usage', 'term': 'Winter', 'grades': [str(i) for i in range(2, 12)]},
        {'page': 36, 'subject': 'Language Usage', 'term': 'Spring', 'grades': [str(i) for i in range(2, 12)]},
        {'page': 37, 'subject': 'Language Usage', 'term': 'Spring', 'grades': [str(i) for i in range(2, 12)]},
        {'page': 38, 'subject': 'Science', 'term': 'Fall', 'grades': [str(i) for i in range(2, 11)]},
        {'page': 39, 'subject': 'Science', 'term': 'Fall', 'grades': [str(i) for i in range(2, 11)]},
        {'page': 40, 'subject': 'Science', 'term': 'Winter', 'grades': [str(i) for i in range(2, 11)]},
        {'page': 41, 'subject': 'Science', 'term': 'Winter', 'grades': [str(i) for i in range(2, 11)]},
        {'page': 42, 'subject': 'Science', 'term': 'Spring', 'grades': [str(i) for i in range(2, 11)]},
        {'page': 43, 'subject': 'Science', 'term': 'Spring', 'grades': [str(i) for i in range(2, 11)]},
    ]

    reader = PdfReader(pdf_path)
    random.seed(seed)

    total_tests = 0
    passed = 0
    failed = 0
    failures = []

    for table in tables_info:
        page = reader.pages[table['page']]
        text = page.extract_text() or ""
        lines = text.strip().split('\n')

        pdf_values = {}
        for line in lines:
            row_data = parse_pdf_row(line, table['grades'])
            for grade, (pct, rit) in row_data.items():
                pdf_values[(grade, pct)] = rit

        if len(pdf_values) >= samples_per_page:
            samples = random.sample(list(pdf_values.keys()), samples_per_page)
        else:
            samples = list(pdf_values.keys())

        for (grade, pct) in samples:
            pdf_rit = pdf_values[(grade, pct)]
            csv_key = (table['subject'], table['term'], grade, pct)
            csv_rit = csv_data.get(csv_key)

            total_tests += 1
            if csv_rit == pdf_rit:
                passed += 1
            else:
                failed += 1
                failures.append({
                    'page': table['page'] + 1,
                    'subject': table['subject'],
                    'term': table['term'],
                    'grade': grade,
                    'percentile': pct,
                    'pdf_rit': pdf_rit,
                    'csv_rit': csv_rit
                })

    print(f"=== Test Results ===")
    print(f"Pages tested: {len(tables_info)}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {100*passed/total_tests:.1f}%")

    if failures:
        print(f"\n=== Failures ===")
        for f in failures:
            print(f"  Page {f['page']}: {f['subject']} {f['term']} Grade {f['grade']} P{f['percentile']}: PDF={f['pdf_rit']}, CSV={f['csv_rit']}")

    return passed, failed

if __name__ == '__main__':
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, 'NormsTables.pdf')
    csv_path = os.path.join(base_dir, 'csv', 'student_status_percentiles.csv')

    run_tests(pdf_path, csv_path)
