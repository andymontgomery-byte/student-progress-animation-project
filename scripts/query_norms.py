#!/usr/bin/env python3
"""
Query helper for norms and student data.
Run: python3 scripts/query_norms.py

Examples:
  python3 scripts/query_norms.py --student "eric.feltoon"
  python3 scripts/query_norms.py --rit-for-percentile Math Spring 1 99
  python3 scripts/query_norms.py --target-rit "eric.feltoon" 99 1
"""

import sqlite3
import argparse
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'student_norms.db')


def get_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)


def lookup_rit(subject, term, grade, percentile, year=2025):
    """Look up RIT score for a given subject/term/grade/percentile."""
    conn = get_connection()
    cursor = conn.cursor()

    # Normalize subject name
    subject_map = {
        'math': 'Mathematics',
        'reading': 'Reading',
        'language': 'Language Usage',
        'science': 'Science'
    }
    subject = subject_map.get(subject.lower(), subject)

    cursor.execute('''
        SELECT rit_score FROM norms
        WHERE year=? AND subject=? AND term=? AND grade=? AND percentile=?
    ''', (year, subject, term, str(grade), percentile))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def get_student_info(email_pattern):
    """Get all info for a student matching the email pattern."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get student summary
    cursor.execute('''
        SELECT * FROM students WHERE email LIKE ?
    ''', (f'%{email_pattern}%',))
    student_rows = cursor.fetchall()
    student_cols = [d[0] for d in cursor.description]

    # Get raw scores
    cursor.execute('''
        SELECT * FROM scores WHERE email LIKE ? ORDER BY term
    ''', (f'%{email_pattern}%',))
    score_rows = cursor.fetchall()
    score_cols = [d[0] for d in cursor.description]

    conn.close()

    return student_cols, student_rows, score_cols, score_rows


def calculate_target_rit(email_pattern, target_percentile=99, levels_ahead=0):
    """Calculate what RIT a student needs to reach a target."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get student info
    cursor.execute('''
        SELECT grade, course FROM students WHERE email LIKE ?
    ''', (f'%{email_pattern}%',))
    result = cursor.fetchone()

    if not result:
        print(f"No student found matching '{email_pattern}'")
        return

    grade, course = result

    # Map course to subject
    subject_map = {
        'Math K-12': 'Mathematics',
        'Reading': 'Reading',
        'Language Usage': 'Language Usage',
        'Science K-12': 'Science'
    }
    subject = subject_map.get(course, course)

    # Calculate target grade (current grade + levels ahead)
    if grade == 'K':
        target_grade = str(levels_ahead) if levels_ahead > 0 else 'K'
    else:
        target_grade = str(int(grade) + levels_ahead)

    # Get target RIT
    cursor.execute('''
        SELECT rit_score FROM norms
        WHERE year=2025 AND subject=? AND term='Spring' AND grade=? AND percentile=?
    ''', (subject, target_grade, target_percentile))

    result = cursor.fetchone()
    conn.close()

    if result:
        return target_grade, result[0]
    return None, None


def print_student_report(email_pattern):
    """Print a full report for a student."""
    student_cols, student_rows, score_cols, score_rows = get_student_info(email_pattern)

    if not student_rows:
        print(f"No student found matching '{email_pattern}'")
        return

    for student in student_rows:
        student_dict = dict(zip(student_cols, student))

        print()
        print("=" * 70)
        print(f"STUDENT: {student_dict['email']}")
        print("=" * 70)
        print(f"  School: {student_dict['school']}")
        print(f"  Grade: {student_dict['grade']}")
        print(f"  Course: {student_dict['course']}")
        print(f"  CGI: {student_dict['cgi']}")
        print()

        print("PERCENTILES:")
        print(f"  Fall: {student_dict['fall_pct']}th" +
              (f" (+{student_dict['fall_99_levels']} levels)" if student_dict['fall_99_levels'] else ""))
        print(f"  Winter: {student_dict['winter_pct']}th" +
              (f" (+{student_dict['winter_99_levels']} levels)" if student_dict['winter_99_levels'] else ""))
        print(f"  Projected Spring: {student_dict['projected_pct']}th" +
              (f" (+{student_dict['projected_99_levels']} levels)" if student_dict['projected_99_levels'] else ""))
        print()

        # Get raw scores
        scores = [dict(zip(score_cols, row)) for row in score_rows
                  if student_dict['email'] in row[1] and student_dict['course'] == row[2]]

        if scores:
            print("RAW RIT SCORES:")
            for score in scores:
                print(f"  {score['term']}: RIT {score['rit_score']} ({score['percentile']}th percentile)")

            if len(scores) >= 2:
                fall_rit = next((s['rit_score'] for s in scores if s['term'] == 'Fall'), None)
                winter_rit = next((s['rit_score'] for s in scores if s['term'] == 'Winter'), None)
                if fall_rit and winter_rit:
                    print(f"  Growth (Fall→Winter): {winter_rit - fall_rit} RIT points")
        print()

        # Calculate targets
        print("TARGETS FOR SPRING:")
        for levels in [0, 1, 2]:
            target_grade, target_rit = calculate_target_rit(
                student_dict['email'], 99, levels)
            if target_rit:
                label = f"99th + {levels} level" if levels else "99th percentile"
                print(f"  {label}: RIT ≥ {target_rit} (Grade {target_grade} level)")


def interactive_query():
    """Run an interactive SQL query."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    print("SQLite Interactive Mode")
    print("Tables: norms, students, scores")
    print("Type 'quit' to exit")
    print()

    while True:
        try:
            query = input("SQL> ").strip()
            if query.lower() in ('quit', 'exit', 'q'):
                break
            if not query:
                continue

            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows:
                # Print header
                cols = [d[0] for d in cursor.description]
                print(" | ".join(cols))
                print("-" * (len(" | ".join(cols))))

                # Print rows
                for row in rows[:50]:  # Limit to 50 rows
                    print(" | ".join(str(v) for v in row))

                if len(rows) > 50:
                    print(f"... ({len(rows)} total rows, showing first 50)")
            else:
                print("(no results)")
            print()

        except Exception as e:
            print(f"Error: {e}")
            print()

    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Query norms and student data')
    parser.add_argument('--student', '-s', help='Get full report for student (email pattern)')
    parser.add_argument('--rit', '-r', nargs=4, metavar=('SUBJECT', 'TERM', 'GRADE', 'PERCENTILE'),
                        help='Look up RIT for subject/term/grade/percentile')
    parser.add_argument('--target', '-t', nargs=3, metavar=('EMAIL', 'PERCENTILE', 'LEVELS'),
                        help='Calculate target RIT for student')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactive SQL mode')

    args = parser.parse_args()

    if args.student:
        print_student_report(args.student)
    elif args.rit:
        subject, term, grade, pct = args.rit
        rit = lookup_rit(subject, term, grade, int(pct))
        if rit:
            print(f"{subject} {term} Grade {grade} {pct}th percentile: RIT {rit}")
        else:
            print("Not found")
    elif args.target:
        email, pct, levels = args.target
        target_grade, target_rit = calculate_target_rit(email, int(pct), int(levels))
        if target_rit:
            print(f"Target: RIT ≥ {target_rit} (Grade {target_grade} Spring {pct}th percentile)")
        else:
            print("Could not calculate target")
    elif args.interactive:
        interactive_query()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
