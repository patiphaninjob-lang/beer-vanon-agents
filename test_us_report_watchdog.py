import json
import tempfile
import unittest
from pathlib import Path

from scripts import us_report_watchdog as watchdog


class UsReportWatchdogTest(unittest.TestCase):
    def write_archive(self, root: Path, report_date: str, phase: str, issues: list):
        data_dir = root / "docs" / "data"
        data_dir.mkdir(parents=True)
        path = data_dir / f"{report_date}-{phase}.json"
        path.write_text(
            json.dumps({"health": {"issues": issues}}, ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def test_dispatches_when_archive_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = watchdog.evaluate_archive(Path(tmp), "2026-06-19", "premarket")

        self.assertTrue(result["dispatch"])
        self.assertEqual(result["reason"], "missing_archive")

    def test_dispatches_when_archive_has_blocking_health_issue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_archive(root, "2026-06-19", "premarket", ["stock_count 79/100"])

            result = watchdog.evaluate_archive(root, "2026-06-19", "premarket")

        self.assertTrue(result["dispatch"])
        self.assertEqual(result["reason"], "blocking_health_issues")
        self.assertEqual(result["blocking_issues"], ["stock_count 79/100"])

    def test_accepts_archive_with_only_fallback_analysis_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_archive(root, "2026-06-19", "postmarket", ["fallback_analysis 5"])

            result = watchdog.evaluate_archive(root, "2026-06-19", "postmarket")

        self.assertFalse(result["dispatch"])
        self.assertEqual(result["reason"], "archive_ok")


if __name__ == "__main__":
    unittest.main()
