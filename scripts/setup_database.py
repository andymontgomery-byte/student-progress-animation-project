#!/usr/bin/env python3
"""
Set up SQLite database with norms and student data.
Run: python3 scripts/setup_database.py
"""

import sqlite3
import csv
import json
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'student_norms.db')
NORMS_2025 = os.path.join(BASE_DIR, 'norms_tables', 'csv', 'student_status_percentiles_2025.csv')
NORMS_2020 = os.path.join(BASE_DIR, 'norms_tables', 'csv', 'student_status_percentiles.csv')
DATA_JSON = os.path.join(BASE_DIR, 'docs', 'data.json')
FALL_DATA = os.path.join(BASE_DIR, 'data', 'input', 'fall_data.xlsx')
WINTER_DATA = os.path.join(BASE_DIR, 'data', 'input', 'winter_data.xlsx')


def setup_database():
    """Create and populate the SQLite database."""

    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creating tables...")

    # Create norms table
    cursor.execute('''
        CREATE TABLE norms (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            subject TEXT,
            term TEXT,
            grade TEXT,
            percentile INTEGER,
            rit_score INTEGER
        )
    ''')

    # Create index for fast lookups
    cursor.execute('CREATE INDEX idx_norms_lookup ON norms(subject, term, grade, percentile)')

    # Create students table (from data.json - high growth students)
    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY,
            email TEXT,
            grade TEXT,
            school TEXT,
            course TEXT,
            fall_pct INTEGER,
            fall_99_levels INTEGER,
            winter_pct INTEGER,
            winter_99_levels INTEGER,
            projected_pct INTEGER,
            projected_99_levels INTEGER,
            cgi REAL
        )
    ''')

    # Create raw scores table (actual RIT scores from input files)
    cursor.execute('''
        CREATE TABLE scores (
            id INTEGER PRIMARY KEY,
            email TEXT,
            course TEXT,
            grade TEXT,
            school TEXT,
            term TEXT,
            rit_score INTEGER,
            percentile INTEGER
        )
    ''')

    cursor.execute('CREATE INDEX idx_scores_email ON scores(email)')
    cursor.execute('CREATE INDEX idx_students_email ON students(email)')

    # Load 2025 norms
    print("Loading 2025 norms...")
    with open(NORMS_2025) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT INTO norms (year, subject, term, grade, percentile, rit_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (2025, row['subject'], row['term'], row['grade'],
                  int(row['percentile']), int(row['rit_score'])))

    # Load 2020 norms
    print("Loading 2020 norms...")
    with open(NORMS_2020) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT INTO norms (year, subject, term, grade, percentile, rit_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (2020, row['subject'], row['term'], row['grade'],
                  int(row['percentile']), int(row['rit_score'])))

    # Load students from data.json
    print("Loading student data...")
    with open(DATA_JSON) as f:
        students = json.load(f)

    for s in students:
        cursor.execute('''
            INSERT INTO students (email, grade, school, course, fall_pct, fall_99_levels,
                                  winter_pct, winter_99_levels, projected_pct, projected_99_levels, cgi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (s['email'], str(s['grade']), s['school'], s['course'],
              s['fall_pct'], s['fall_99_levels'], s['winter_pct'], s['winter_99_levels'],
              s['projected_pct'], s['projected_99_levels'], s['cgi']))

    # Load raw scores from Excel files
    print("Loading raw scores from Excel...")

    # Fall data - skip first 2 rows (header + column names row)
    fall = pd.read_excel(FALL_DATA, skiprows=2, header=None)
    fall.columns = ['email', 'course', 'grade', 'district', 'school', 'term', 'rit', 'percentile']
    for _, row in fall.iterrows():
        try:
            cursor.execute('''
                INSERT INTO scores (email, course, grade, school, term, rit_score, percentile)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['email'], row['course'], str(row['grade']), row['school'],
                  'Fall', int(row['rit']), int(row['percentile'])))
        except (ValueError, TypeError):
            continue  # Skip invalid rows

    # Winter data - skip first 2 rows
    winter = pd.read_excel(WINTER_DATA, skiprows=2, header=None)
    # Columns: email, course, grade, district, school, term, cgi, rit, percentile, growth
    for _, row in winter.iterrows():
        try:
            cursor.execute('''
                INSERT INTO scores (email, course, grade, school, term, rit_score, percentile)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row.iloc[0], row.iloc[1], str(row.iloc[2]), row.iloc[4],
                  'Winter', int(row.iloc[7]), int(row.iloc[8])))
        except (ValueError, TypeError):
            continue  # Skip invalid rows

    conn.commit()

    # Print summary
    cursor.execute('SELECT COUNT(*) FROM norms WHERE year=2025')
    norms_2025_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM norms WHERE year=2020')
    norms_2020_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM students')
    students_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM scores')
    scores_count = cursor.fetchone()[0]

    conn.close()

    print()
    print("=" * 50)
    print("DATABASE CREATED SUCCESSFULLY")
    print("=" * 50)
    print(f"  Location: {DB_PATH}")
    print(f"  2025 norms: {norms_2025_count:,} rows")
    print(f"  2020 norms: {norms_2020_count:,} rows")
    print(f"  Students: {students_count:,} rows")
    print(f"  Scores: {scores_count:,} rows")
    print()
    print("Example queries:")
    print("  sqlite3 data/student_norms.db")
    print("  SELECT * FROM norms WHERE subject='Mathematics' AND term='Spring' AND grade='1' AND percentile=99;")


if __name__ == '__main__':
    setup_database()
