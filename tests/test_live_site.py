#!/usr/bin/env python3
"""Test the LIVE GitHub Pages site - what users actually see."""

import time
from playwright.sync_api import sync_playwright

URLS = {
    "main": "https://andymontgomery-byte.github.io/student-progress-animation-project/",
    "strata": "https://andymontgomery-byte.github.io/student-progress-animation-project/strata/",
    "compare": "https://andymontgomery-byte.github.io/student-progress-animation-project/compare/",
}

def test_live_site():
    print("=" * 60)
    print("TESTING LIVE GITHUB PAGES SITE")
    print("=" * 60)
    print()

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for name, url in URLS.items():
            print(f"\nTesting {name}: {url}")
            page = browser.new_page(viewport={'width': 1400, 'height': 900})

            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            try:
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                time.sleep(1)

                # Check for errors
                critical = [e for e in console_errors if "favicon" not in e.lower()]
                if critical:
                    results.append((name, "FAIL", f"Console errors: {critical}"))
                    continue

                # Check dropdowns work
                if name == "compare":
                    # Check schools dropdown is NOT multi-select
                    school = page.locator("#schoolFilter")
                    is_multi = school.evaluate("el => el.multiple")
                    if is_multi:
                        results.append((name, "FAIL", "Schools still has multiple attribute!"))
                        continue

                    # Check it has options
                    opts = school.locator("option").all_text_contents()
                    if len(opts) < 2:
                        results.append((name, "FAIL", f"Schools only has {len(opts)} options"))
                        continue

                    # Select and verify
                    school.select_option(index=1)
                    time.sleep(0.5)

                    student_a = page.locator("#studentSelectA")
                    student_a.select_option(index=1)
                    time.sleep(0.5)

                    results.append((name, "PASS", f"Schools has {len(opts)} options, selection works"))

                else:
                    # Main and Strata
                    dropdown = page.locator("select").first
                    opts = dropdown.locator("option").all_text_contents()
                    if len(opts) > 1:
                        dropdown.select_option(index=1)
                        time.sleep(0.5)
                        results.append((name, "PASS", f"Dropdown has {len(opts)} options"))
                    else:
                        results.append((name, "FAIL", "Dropdown empty"))

            except Exception as e:
                results.append((name, "FAIL", str(e)))

            page.close()

        browser.close()

    print("\n" + "=" * 60)
    print("LIVE SITE TEST RESULTS")
    print("=" * 60)

    all_pass = True
    for name, status, detail in results:
        icon = "✓" if status == "PASS" else "✗"
        print(f"  {icon} {name}: {detail}")
        if status != "PASS":
            all_pass = False

    return all_pass

if __name__ == "__main__":
    import sys
    success = test_live_site()
    sys.exit(0 if success else 1)
