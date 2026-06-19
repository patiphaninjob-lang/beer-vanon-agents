import unittest
from unittest.mock import patch

import beer_top100_agent as top100


class ProcessSingleStockFallbackTest(unittest.TestCase):
    def test_process_single_stock_keeps_record_when_stock_context_fails(self):
        with patch.object(top100, "get_stock_context", side_effect=RuntimeError("boom")):
            with patch.object(top100, "search_knowledge", return_value="knowledge ctx"):
                with patch.object(
                    top100,
                    "combined_analysis",
                    return_value={
                        "interpretation": "ok",
                        "beer_view": "ok",
                        "homework_analysis": [{"topic": "ธุรกิจ", "insight": "x"}],
                    },
                ):
                    with patch.object(top100, "generate_mini_chart_b64", return_value=b"chart"):
                        result = top100.process_single_stock(
                            ticker="FAIL",
                            rank=1,
                            mktcap=None,
                            hist_df=None,
                            query="query",
                            posts=[],
                            embeddings=None,
                            embed_model=None,
                            query_vector=None,
                            user_notes_db={},
                        )

        self.assertIsNotNone(result)
        self.assertEqual(result["stock"]["ticker"], "FAIL")
        self.assertEqual(result["stock"]["name"], "FAIL")
        self.assertEqual(len(result["analysis_data"]["homework_analysis"]), 6)

    def test_completion_email_includes_archive_link(self):
        html = top100.build_completion_email(
            "Tuesday, 26 May 2026",
            "https://example.com/?date=2026-05-26",
            100,
        )

        self.assertIn("https://example.com/?date=2026-05-26", html)
        self.assertIn("การบ้าน Beer Top 100 เสร็จแล้ว", html)
        self.assertNotIn("เบียร์วิเคราะห์เจาะลึก", html)
        self.assertNotIn("card-homework", html)

    def test_scheduled_report_paths_include_phase_and_manual_archive(self):
        day = top100.datetime.date(2026, 6, 18)
        with patch.object(top100, "DATA_DIR", top100.Path("docs/data")):
            paths = top100.scheduled_report_paths(day, "postmarket")

        self.assertEqual(
            [str(path).replace("\\", "/") for path in paths],
            ["docs/data/2026-06-18-postmarket.json", "docs/data/2026-06-18.json"],
        )

    def test_scheduled_report_paths_deduplicates_manual_archive(self):
        day = top100.datetime.date(2026, 6, 18)
        with patch.object(top100, "DATA_DIR", top100.Path("docs/data")):
            paths = top100.scheduled_report_paths(day, "manual")

        self.assertEqual([str(path).replace("\\", "/") for path in paths], ["docs/data/2026-06-18.json"])

    def test_archive_health_detects_missing_artifacts(self):
        payload = {
            "stocks": [
                {
                    "ticker": "OK",
                    "chart_b64": "abc",
                    "homework_checklist": [{}] * 6,
                    "market_cap": 100,
                },
                {
                    "ticker": "MISS",
                    "chart_b64": "",
                    "homework_checklist": [{}],
                    "market_cap": 0,
                },
            ],
            "market_indices": {"dji": {}, "spx": {}},
        }

        health = top100.build_archive_health(payload, expected_total=2)

        self.assertEqual(health["status"], "warning")
        self.assertIn("missing_charts 1", health["issues"])
        self.assertIn("incomplete_homework 1", health["issues"])
        self.assertIn("missing_market_indices ixic", health["issues"])
        self.assertIn("zero_market_cap 1", health["issues"])
        self.assertEqual(health["counts"]["charts"], 1)

    def test_archive_health_accepts_complete_archive(self):
        payload = {
            "stocks": [
                {
                    "ticker": "OK",
                    "chart_b64": "abc",
                    "homework_checklist": [{}] * 6,
                    "market_cap": 100,
                }
            ],
            "market_indices": {"dji": {}, "spx": {}, "ixic": {}},
        }

        health = top100.build_archive_health(payload, expected_total=1)

        self.assertEqual(health["status"], "ok")
        self.assertEqual(health["issues"], [])


if __name__ == "__main__":
    unittest.main()
