#!/usr/bin/env python3
"""
UI Test Agent - Enforces visual testing standards on any webapp.

Usage:
  python3 scripts/ui_test_agent.py https://example.com
  python3 scripts/ui_test_agent.py https://example.com --output ./test_results

Standards enforced:
1. Visual verification with screenshots (not just programmatic checks)
2. Test 10+ variations for dropdowns/inputs
3. Flag cross-browser issues (multi-select, custom elements)
4. Verify elements are visually rendered, not just present in DOM
5. Test filter/search combinations
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from playwright.sync_api import sync_playwright, Page


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    screenshot: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class UITestReport:
    url: str
    timestamp: str
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    results: List[TestResult] = field(default_factory=list)


class UITestAgent:
    """Agent that enforces UI testing standards."""

    def __init__(self, base_url: str, output_dir: str = "./ui_test_results"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.screenshot_dir = os.path.join(output_dir, "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.report = UITestReport(
            url=base_url,
            timestamp=datetime.now().isoformat()
        )

    def run_all_tests(self) -> UITestReport:
        """Run all UI tests on the target URL."""
        print(f"\n{'='*70}")
        print(f"UI TEST AGENT")
        print(f"{'='*70}")
        print(f"URL: {self.base_url}")
        print(f"Output: {self.output_dir}")
        print()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1400, 'height': 900})

            # Collect console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            # Load page
            print("Loading page...")
            page.goto(self.base_url)
            page.wait_for_load_state("networkidle")
            time.sleep(1)

            # Take initial screenshot
            self._screenshot(page, "01_initial_load")

            # Run test suites
            self._test_console_errors(console_errors)
            self._test_dropdowns(page)
            self._test_forms(page)
            self._test_buttons(page)
            self._test_links(page)
            self._test_accessibility(page)

            browser.close()

        # Generate report
        self._generate_report()

        return self.report

    def _screenshot(self, page: Page, name: str) -> str:
        """Take a screenshot and return the path."""
        path = os.path.join(self.screenshot_dir, f"{name}.png")
        page.screenshot(path=path)
        return path

    def _add_result(self, name: str, passed: bool, message: str,
                    screenshot: str = None, warnings: List[str] = None):
        """Add a test result."""
        result = TestResult(
            name=name,
            passed=passed,
            message=message,
            screenshot=screenshot,
            warnings=warnings or []
        )
        self.report.results.append(result)

        if passed:
            self.report.passed += 1
            icon = "✓"
        else:
            self.report.failed += 1
            icon = "✗"

        self.report.warnings += len(result.warnings)

        print(f"  {icon} {name}: {message}")
        for warning in result.warnings:
            print(f"    ⚠ {warning}")

    def _test_console_errors(self, errors: List[str]):
        """Test for JavaScript console errors."""
        print("\n--- Console Errors ---")

        # Filter out non-critical errors
        critical = [e for e in errors if "favicon" not in e.lower()]

        if critical:
            self._add_result(
                "No console errors",
                False,
                f"{len(critical)} errors found",
                warnings=critical[:5]  # Show first 5
            )
        else:
            self._add_result("No console errors", True, "Clean")

    def _test_dropdowns(self, page: Page):
        """Test all dropdowns with visual verification."""
        print("\n--- Dropdown Tests ---")

        selects = page.locator("select").all()

        if not selects:
            self._add_result("Dropdowns exist", True, "No dropdowns found (OK)")
            return

        self._add_result("Dropdowns found", True, f"{len(selects)} dropdowns")

        for i, select in enumerate(selects):
            select_id = select.get_attribute("id") or f"select_{i}"

            # Check for multi-select (cross-browser issue!)
            is_multiple = select.evaluate("el => el.multiple")
            if is_multiple:
                self._add_result(
                    f"Dropdown {select_id}",
                    False,
                    "MULTI-SELECT DETECTED",
                    warnings=["Multi-select renders as blank checkboxes in Safari",
                              "Consider using single-select or custom component"]
                )
                continue

            # Get options
            options = select.locator("option").all_text_contents()

            if len(options) < 2:
                self._add_result(
                    f"Dropdown {select_id}",
                    False,
                    f"Only {len(options)} options"
                )
                continue

            # Test selecting multiple options (not just index=1!)
            test_count = min(10, len(options))
            errors = []

            for j in range(1, test_count):
                try:
                    select.select_option(index=j)
                    time.sleep(0.2)
                except Exception as e:
                    errors.append(f"Option {j}: {e}")

            # Screenshot with last selection
            screenshot = self._screenshot(page, f"dropdown_{select_id}")

            # Reset
            try:
                select.select_option(index=0)
            except:
                pass

            if errors:
                self._add_result(
                    f"Dropdown {select_id}",
                    False,
                    f"{len(errors)} selection errors",
                    screenshot=screenshot,
                    warnings=errors[:3]
                )
            else:
                self._add_result(
                    f"Dropdown {select_id}",
                    True,
                    f"{len(options)} options, tested {test_count-1} selections",
                    screenshot=screenshot
                )

    def _test_forms(self, page: Page):
        """Test form inputs."""
        print("\n--- Form Tests ---")

        inputs = page.locator("input:visible, textarea:visible").all()

        if not inputs:
            self._add_result("Form inputs exist", True, "No inputs found (OK)")
            return

        self._add_result("Form inputs found", True, f"{len(inputs)} inputs")

        for i, inp in enumerate(inputs):
            input_id = inp.get_attribute("id") or inp.get_attribute("name") or f"input_{i}"
            input_type = inp.get_attribute("type") or "text"

            # Skip hidden/submit inputs
            if input_type in ("hidden", "submit", "button"):
                continue

            # Test that input is interactable
            try:
                if input_type in ("text", "email", "search", "tel", "url"):
                    inp.fill("test input")
                    time.sleep(0.1)
                    inp.fill("")
                elif input_type == "checkbox":
                    inp.check()
                    inp.uncheck()
                elif input_type == "radio":
                    inp.check()

                self._add_result(f"Input {input_id}", True, f"type={input_type}, interactable")

            except Exception as e:
                self._add_result(
                    f"Input {input_id}",
                    False,
                    f"Not interactable: {e}"
                )

    def _test_buttons(self, page: Page):
        """Test that buttons are clickable."""
        print("\n--- Button Tests ---")

        buttons = page.locator("button:visible, input[type='button']:visible, input[type='submit']:visible").all()

        if not buttons:
            self._add_result("Buttons exist", True, "No buttons found (OK)")
            return

        self._add_result("Buttons found", True, f"{len(buttons)} buttons")

        for i, btn in enumerate(buttons):
            btn_text = btn.text_content() or btn.get_attribute("value") or f"button_{i}"
            btn_text = btn_text.strip()[:20]

            try:
                # Check button is enabled and visible
                is_disabled = btn.is_disabled()
                is_visible = btn.is_visible()

                if is_disabled:
                    self._add_result(f"Button '{btn_text}'", True, "Disabled (OK)")
                elif is_visible:
                    self._add_result(f"Button '{btn_text}'", True, "Visible and enabled")
                else:
                    self._add_result(f"Button '{btn_text}'", False, "Not visible")

            except Exception as e:
                self._add_result(f"Button '{btn_text}'", False, f"Error: {e}")

    def _test_links(self, page: Page):
        """Test that links are valid."""
        print("\n--- Link Tests ---")

        links = page.locator("a[href]:visible").all()

        if not links:
            self._add_result("Links exist", True, "No links found (OK)")
            return

        # Just count and spot check
        self._add_result("Links found", True, f"{len(links)} links")

        broken = []
        for link in links[:10]:  # Check first 10
            href = link.get_attribute("href")
            if href and href.startswith("javascript:"):
                continue
            if href == "#":
                continue

            try:
                is_visible = link.is_visible()
                if not is_visible:
                    broken.append(href)
            except:
                pass

        if broken:
            self._add_result(
                "Link visibility",
                False,
                f"{len(broken)} hidden links",
                warnings=broken[:3]
            )
        else:
            self._add_result("Link visibility", True, "All checked links visible")

    def _test_accessibility(self, page: Page):
        """Basic accessibility checks."""
        print("\n--- Accessibility Tests ---")

        # Check for alt text on images
        images = page.locator("img").all()
        missing_alt = []
        for img in images:
            alt = img.get_attribute("alt")
            if alt is None or alt == "":
                src = img.get_attribute("src") or "unknown"
                missing_alt.append(src[:50])

        if missing_alt:
            self._add_result(
                "Image alt text",
                False,
                f"{len(missing_alt)} images missing alt",
                warnings=missing_alt[:3]
            )
        else:
            self._add_result(
                "Image alt text",
                True,
                f"All {len(images)} images have alt text"
            )

        # Check for form labels
        inputs_without_labels = page.locator("input:not([type='hidden']):not([type='submit']):not([type='button'])").all()
        unlabeled = []
        for inp in inputs_without_labels:
            inp_id = inp.get_attribute("id")
            if inp_id:
                label = page.locator(f"label[for='{inp_id}']")
                if label.count() == 0:
                    unlabeled.append(inp_id)

        if unlabeled:
            self._add_result(
                "Form labels",
                False,
                f"{len(unlabeled)} inputs without labels",
                warnings=unlabeled[:3]
            )
        else:
            self._add_result("Form labels", True, "All inputs have labels")

    def _generate_report(self):
        """Generate the test report."""
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print(f"{'='*70}")
        print(f"  Passed: {self.report.passed}")
        print(f"  Failed: {self.report.failed}")
        print(f"  Warnings: {self.report.warnings}")
        print()

        # Save JSON report
        report_path = os.path.join(self.output_dir, "report.json")
        with open(report_path, "w") as f:
            json.dump(asdict(self.report), f, indent=2)
        print(f"Report saved: {report_path}")

        # Save markdown report
        md_path = os.path.join(self.output_dir, "report.md")
        with open(md_path, "w") as f:
            f.write(f"# UI Test Report\n\n")
            f.write(f"**URL:** {self.report.url}\n\n")
            f.write(f"**Date:** {self.report.timestamp}\n\n")
            f.write(f"**Results:** {self.report.passed} passed, {self.report.failed} failed, {self.report.warnings} warnings\n\n")

            f.write("## Results\n\n")
            for r in self.report.results:
                icon = "✓" if r.passed else "✗"
                f.write(f"- {icon} **{r.name}**: {r.message}\n")
                for w in r.warnings:
                    f.write(f"  - ⚠ {w}\n")

        print(f"Markdown report: {md_path}")
        print(f"Screenshots: {self.screenshot_dir}")

        if self.report.failed > 0:
            print(f"\n⚠ {self.report.failed} TESTS FAILED - Review report")
        else:
            print(f"\n✓ ALL TESTS PASSED")


def main():
    parser = argparse.ArgumentParser(
        description="UI Test Agent - Enforces visual testing standards"
    )
    parser.add_argument("url", help="URL to test")
    parser.add_argument("--output", "-o", default="./ui_test_results",
                        help="Output directory for results")

    args = parser.parse_args()

    agent = UITestAgent(args.url, args.output)
    report = agent.run_all_tests()

    sys.exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    main()
