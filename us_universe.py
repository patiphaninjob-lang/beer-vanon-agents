"""
US ticker universe selection with dynamic discovery and static fallback.

The agent still ranks by yfinance market cap after this module returns
candidate tickers. Dynamic discovery only widens the candidate pool so new
large listings are not missed.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import urllib.request
from pathlib import Path


STATIC_US_UNIVERSE = [
    "SPCX", "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "ORCL", "CRM",
    "AMD", "ADBE", "QCOM", "INTC", "TXN", "AMAT", "KLAC", "LRCX", "MU", "MRVL",
    "ADI", "NOW", "INTU", "SNPS", "CDNS", "CRWD", "PANW", "FTNT", "ZS", "IBM",
    "LLY", "UNH", "JNJ", "ABBV", "MRK", "PFE", "BMY", "AMGN", "GILD", "ISRG",
    "SYK", "BSX", "BDX", "DHR", "ZTS", "ELV", "CI", "HUM", "CVS", "HCA",
    "BRK-B", "JPM", "BAC", "WFC", "C", "GS", "MS", "AXP", "V", "MA",
    "BLK", "SPGI", "MCO", "ICE", "CME", "COF", "USB", "TFC", "PNC", "SCHW",
    "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "DG", "BKNG", "MAR", "HLT",
    "WMT", "COST", "PG", "KO", "PEP", "PM", "MO", "CL", "MDLZ", "GIS",
    "XOM", "CVX", "COP", "SLB", "MPC", "VLO", "OXY", "PSX", "HAL", "BKR",
    "GE", "CAT", "HON", "RTX", "LMT", "NOC", "BA", "UPS", "DE", "UNP",
    "CSX", "NSC", "ETN", "EMR", "MMM", "ROP",
    "NFLX", "TMUS", "T", "VZ", "CMCSA", "DIS",
    "LIN", "APD", "ECL", "FCX", "NEM", "SHW",
    "PLD", "AMT", "EQIX", "CCI", "SPG",
    "NEE", "SO", "DUK", "AEP", "EXC",
]
STATIC_US_UNIVERSE = list(dict.fromkeys(STATIC_US_UNIVERSE))

NASDAQ_SCREENER_URL = (
    "https://api.nasdaq.com/api/screener/stocks"
    "?tableonly=true&limit=5000&offset=0&download=true"
)


def normalize_ticker(symbol: str) -> str:
    ticker = (symbol or "").strip().upper()
    ticker = ticker.replace("/", "-").replace(".", "-")
    return ticker


def parse_market_cap(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("$", "")
    if not text or text.upper() in {"N/A", "NA", "--"}:
        return 0.0
    multiplier = 1.0
    suffix = text[-1:].upper()
    if suffix in {"T", "B", "M", "K"}:
        text = text[:-1]
        multiplier = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}[suffix]
    try:
        return float(text) * multiplier
    except ValueError:
        return 0.0


def is_common_stock_candidate(ticker: str) -> bool:
    if not ticker or len(ticker) > 8:
        return False
    if not re.fullmatch(r"[A-Z][A-Z0-9-]*", ticker):
        return False
    excluded_suffixes = ("-W", "-WS", "-WT", "-U", "-R", "-RT", "-P")
    return not ticker.endswith(excluded_suffixes)


def fetch_nasdaq_universe(timeout: int = 20) -> list[dict]:
    req = urllib.request.Request(
        NASDAQ_SCREENER_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
            "Origin": "https://www.nasdaq.com",
            "Referer": "https://www.nasdaq.com/market-activity/stocks/screener",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    rows = (((payload or {}).get("data") or {}).get("rows") or [])
    candidates = []
    for row in rows:
        ticker = normalize_ticker(row.get("symbol") or row.get("ticker"))
        market_cap = parse_market_cap(row.get("marketCap") or row.get("marketcap"))
        if not is_common_stock_candidate(ticker) or market_cap <= 0:
            continue
        candidates.append(
            {
                "ticker": ticker,
                "name": row.get("name") or row.get("companyName") or "",
                "market_cap": market_cap,
                "exchange": row.get("exchange") or "",
                "sector": row.get("sector") or "",
            }
        )

    candidates.sort(key=lambda item: item["market_cap"], reverse=True)
    return candidates


def build_us_universe(
    static_universe: list[str] | None = None,
    dynamic_limit: int = 240,
    fetcher=fetch_nasdaq_universe,
) -> tuple[list[str], dict]:
    static = list(dict.fromkeys(static_universe or STATIC_US_UNIVERSE))
    dynamic_rows = []
    error = ""
    try:
        dynamic_rows = fetcher()
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

    if dynamic_rows:
        dynamic_tickers = [row["ticker"] for row in dynamic_rows[:dynamic_limit]]
        universe = list(dict.fromkeys(dynamic_tickers + static))
        source = "nasdaq_screener"
    else:
        dynamic_tickers = []
        universe = static
        source = "static_fallback"

    dynamic_set = set(dynamic_tickers)
    static_set = set(static)
    meta = {
        "source": source,
        "updated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "static_count": len(static),
        "dynamic_count": len(dynamic_tickers),
        "candidate_count": len(universe),
        "new_dynamic_tickers": sorted(dynamic_set - static_set)[:50],
        "error": error,
    }
    return universe, meta


def write_universe_snapshot(path: Path, meta: dict, selected: list[str], market_caps: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **meta,
        "selected_count": len(selected),
        "selected": [
            {"ticker": ticker, "market_cap": market_caps.get(ticker, 0)}
            for ticker in selected
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
