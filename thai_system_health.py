"""
Lightweight canary checks for the Thai stock homework app.

The script writes docs/thai-data/system_health.json so the Thai dashboard can
show whether secrets and external providers are still usable.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import smtplib
import socket
import sys
import time
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent
THAI_AGENT_DIR = ROOT_DIR / "thai_agent"
COMMON_DIR = ROOT_DIR / "common"
for path in (THAI_AGENT_DIR, COMMON_DIR):
    if str(path) not in sys.path:
        sys.path.append(str(path))


CHECK_TIMEOUT = 20
DATA_DIR = Path("docs/thai-data")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def check_result(name: str, status: str, message: str, elapsed: float) -> dict:
    return {
        "name": name,
        "status": status,
        "message": message,
        "elapsed_ms": round(elapsed * 1000),
    }


def run_check(name: str, fn) -> dict:
    start = time.time()
    try:
        status, message = fn()
    except Exception as exc:
        status, message = "fail", f"{type(exc).__name__}: {exc}"
    return check_result(name, status, message, time.time() - start)


def check_env() -> tuple[str, str]:
    required = ["GROQ_API_KEY", "GMAIL_USER", "GMAIL_APP_PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        return "fail", "missing " + ", ".join(missing)
    return "ok", "required secrets present"


def check_groq() -> tuple[str, str]:
    from groq import Groq

    key = os.getenv("GROQ_API_KEY")
    if not key:
        return "fail", "GROQ_API_KEY missing"
    client = Groq(api_key=key, timeout=CHECK_TIMEOUT)
    models = client.models.list()
    count = len(getattr(models, "data", []) or [])
    return "ok", f"models reachable ({count})"


def check_gmail() -> tuple[str, str]:
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not user or not password:
        return "fail", "GMAIL_USER or GMAIL_APP_PASSWORD missing"

    socket.setdefaulttimeout(CHECK_TIMEOUT)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=CHECK_TIMEOUT) as smtp:
        smtp.login(user, password)
    return "ok", "smtp login ok"


def check_yfinance() -> tuple[str, str]:
    import yfinance as yf

    messages = []
    for symbol in ["^SET.BK", "^SET50.BK", "^SET100.BK", "PTT.BK"]:
        hist = yf.Ticker(symbol).history(period="3mo").dropna(subset=["Close"])
        if hist.empty:
            return "fail", f"{symbol} history unavailable"
        quality = "single point" if len(hist) == 1 else f"{len(hist)} rows"
        messages.append(f"{symbol} {quality}")
    return "ok", "; ".join(messages)


def check_universe() -> tuple[str, str]:
    from thai_top100_agent import TH_UNIVERSE

    count = len(TH_UNIVERSE)
    if count < 100:
        return "warning", f"Thai universe small ({count})"
    return "ok", f"Thai universe candidates {count}"


def check_archive_freshness(max_age_hours: int) -> tuple[str, str]:
    status_path = DATA_DIR / "status.json"
    if not status_path.exists():
        return "warning", "docs/thai-data/status.json missing"
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    generated = (payload.get("latest") or {}).get("generated")
    if not generated:
        return "warning", "latest generated timestamp missing"

    parsed = dt.datetime.fromisoformat(generated.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    age_hours = (
        dt.datetime.now(dt.timezone.utc) - parsed.astimezone(dt.timezone.utc)
    ).total_seconds() / 3600
    if age_hours > max_age_hours:
        return "warning", f"latest Thai archive age {age_hours:.1f}h"
    return "ok", f"latest Thai archive age {age_hours:.1f}h"


def build_health(max_age_hours: int) -> dict:
    checks = [
        run_check("env", check_env),
        run_check("groq", check_groq),
        run_check("gmail", check_gmail),
        run_check("universe", check_universe),
        run_check("yfinance", check_yfinance),
        run_check(
            "archive_freshness",
            lambda: check_archive_freshness(max_age_hours),
        ),
    ]
    failed = [c for c in checks if c["status"] == "fail"]
    warnings = [c for c in checks if c["status"] == "warning"]
    if failed:
        status = "fail"
    elif warnings:
        status = "warning"
    else:
        status = "ok"
    return {
        "updated": utc_now(),
        "status": status,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-age-hours", type=int, default=36)
    parser.add_argument("--out", default=str(DATA_DIR / "system_health.json"))
    parser.add_argument("--fail-on-error", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    health = build_health(args.max_age_hours)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(health, ensure_ascii=False, indent=2))

    if args.fail_on_error and health["status"] == "fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
