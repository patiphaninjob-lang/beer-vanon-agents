import unittest

from us_universe import (
    build_us_universe,
    is_common_stock_candidate,
    normalize_ticker,
    parse_market_cap,
)


class UsUniverseTest(unittest.TestCase):
    def test_parse_market_cap_supports_common_suffixes(self):
        self.assertEqual(parse_market_cap("$1.2T"), 1.2e12)
        self.assertEqual(parse_market_cap("$3.5B"), 3.5e9)
        self.assertEqual(parse_market_cap("42M"), 42e6)
        self.assertEqual(parse_market_cap("N/A"), 0)

    def test_normalize_and_filter_tickers(self):
        self.assertEqual(normalize_ticker("brk.b"), "BRK-B")
        self.assertTrue(is_common_stock_candidate("AAPL"))
        self.assertFalse(is_common_stock_candidate("ABC-W"))
        self.assertFalse(is_common_stock_candidate("TOO-LONG1"))

    def test_build_us_universe_merges_dynamic_and_static(self):
        rows = [
            {"ticker": "NEW", "market_cap": 200},
            {"ticker": "AAPL", "market_cap": 100},
        ]

        universe, meta = build_us_universe(
            static_universe=["AAPL", "MSFT"],
            dynamic_limit=10,
            fetcher=lambda: rows,
        )

        self.assertEqual(universe, ["NEW", "AAPL", "MSFT"])
        self.assertEqual(meta["source"], "nasdaq_screener")
        self.assertEqual(meta["candidate_count"], 3)
        self.assertIn("NEW", meta["new_dynamic_tickers"])

    def test_build_us_universe_falls_back_to_static_on_error(self):
        def fail():
            raise RuntimeError("boom")

        universe, meta = build_us_universe(
            static_universe=["AAPL"],
            fetcher=fail,
        )

        self.assertEqual(universe, ["AAPL"])
        self.assertEqual(meta["source"], "static_fallback")
        self.assertIn("boom", meta["error"])


if __name__ == "__main__":
    unittest.main()
