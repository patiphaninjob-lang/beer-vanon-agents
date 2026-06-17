import unittest
from unittest.mock import patch

import system_health


class SystemHealthTest(unittest.TestCase):
    def test_build_health_reports_fail_when_any_check_fails(self):
        checks = [
            {"name": "env", "status": "ok", "message": "ok", "elapsed_ms": 1},
            {"name": "groq", "status": "fail", "message": "bad key", "elapsed_ms": 1},
            {"name": "gmail", "status": "ok", "message": "ok", "elapsed_ms": 1},
            {"name": "yfinance", "status": "ok", "message": "ok", "elapsed_ms": 1},
            {"name": "archive_freshness", "status": "ok", "message": "ok", "elapsed_ms": 1},
        ]

        with patch.object(system_health, "run_check", side_effect=checks):
            health = system_health.build_health(max_age_hours=36)

        self.assertEqual(health["status"], "fail")
        self.assertEqual(health["checks"], checks)

    def test_build_health_reports_warning_without_failures(self):
        checks = [
            {"name": "env", "status": "ok", "message": "ok", "elapsed_ms": 1},
            {"name": "groq", "status": "ok", "message": "ok", "elapsed_ms": 1},
            {"name": "gmail", "status": "ok", "message": "ok", "elapsed_ms": 1},
            {"name": "yfinance", "status": "ok", "message": "ok", "elapsed_ms": 1},
            {"name": "archive_freshness", "status": "warning", "message": "old", "elapsed_ms": 1},
        ]

        with patch.object(system_health, "run_check", side_effect=checks):
            health = system_health.build_health(max_age_hours=36)

        self.assertEqual(health["status"], "warning")


if __name__ == "__main__":
    unittest.main()
