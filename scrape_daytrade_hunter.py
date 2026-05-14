"""
Collect public metadata about "Daytrade Hunter" for this project.

This script only reads publicly visible web page text. It does not bypass
paywalls, log in, download copyrighted PDFs, or extract the full book.

Outputs:
  data/daytrade_hunter/daytrade_hunter_raw.json
  data/daytrade_hunter/daytrade_hunter_notes.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_SOURCES = [
    "https://www.scribd.com/document/639572894/Daytrade-Hunter",
    "https://learning.udoncity.go.th/sharebook/book-detail.php?isbn=9786169245407",
    "https://sites.google.com/site/bookminimize/Daytrade-Hunter",
    "https://www.goodreads.com/book/show/28810653-daytrade-hunter",
    "https://thaipick.com/product/shopee/4048337",
    "https://www.facebook.com/StockExperience/posts/1328790057575516/",
    "https://www.blockdit.com/posts/5f3557e8307eeb09e003ca6c",
]

OUTPUT_DIR = Path("data") / "daytrade_hunter"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


class TextExtractor(HTMLParser):
    """Tiny HTML-to-text extractor using only the Python standard library."""

    BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }
    SKIP_TAGS = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if text:
            self._parts.append(text)

    def text(self) -> str:
        raw = " ".join(self._parts)
        raw = unescape(raw)
        raw = re.sub(r"[ \t\r\f\v]+", " ", raw)
        raw = re.sub(r"\n\s+", "\n", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


@dataclass
class SourceResult:
    url: str
    ok: bool
    fetched_at: str
    status: int | None = None
    title: str = ""
    text: str = ""
    error: str = ""
    facts: dict[str, str] = field(default_factory=dict)
    derived_notes: list[str] = field(default_factory=list)


def fetch_url(url: str, timeout: int) -> tuple[int, str]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "th,en;q=0.8"})
    with urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", None) or resp.getcode()
        content_type = resp.headers.get("content-type", "")
        raw = resp.read()

    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError:
        charset_match = re.search(r"charset=([\w-]+)", content_type, flags=re.I)
        charset = charset_match.group(1) if charset_match else "windows-874"
        try:
            html = raw.decode(charset, errors="replace")
        except LookupError:
            html = raw.decode("windows-874", errors="replace")
    return status, html


def html_to_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    parser.close()
    return parser.text()


def extract_title(html: str, text: str) -> str:
    patterns = [
        r"<meta[^>]+property=[\"']og:title[\"'][^>]+content=[\"']([^\"']+)",
        r"<title[^>]*>(.*?)</title>",
        r"<h1[^>]*>(.*?)</h1>",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I | re.S)
        if match:
            cleaned = re.sub(r"<[^>]+>", " ", match.group(1))
            return re.sub(r"\s+", " ", unescape(cleaned)).strip()
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return first_line[:120]


def compact_text(text: str, max_chars: int = 3000) -> str:
    lines = []
    seen = set()
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if len(line) < 2:
            continue
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        lines.append(line)
    result = "\n".join(lines)
    return result[:max_chars].strip()


def find_first(patterns: Iterable[str], text: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I | re.S)
        if match:
            value = match.group(1) if match.groups() else match.group(0)
            return re.sub(r"\s+", " ", value).strip(" :-")
    return ""


def extract_public_facts(text: str) -> dict[str, str]:
    facts: dict[str, str] = {}

    mappings = {
        "isbn": [r"ISBN\s*[:：]?\s*([0-9-]{10,17})", r"ISSN หรือ ISBN\s*[:：]?\s*([0-9-]{10,17})"],
        "author": [r"ผู้เขียน\s*[:：]\s*([^\n]+)", r"ผู้แต่ง\s*[:：]\s*([^\n]+)", r"กระทรวง จารุศิระ"],
        "publisher": [r"สำนักพิมพ์\s*[:：]\s*([^\n]+)", r"บริษัท สำนักพิมพ์\s*([^\n]+)"],
        "year": [r"ปีพิมพ์\s*[:：]\s*([0-9]{4})", r"ปี\s*([0-9]{4})", r"เดือนปีที่พิมพ์\s*[:：]\s*([0-9/]+)"],
        "pages": [r"จำนวนหน้า\s*[:：]\s*([0-9]+\s*หน้า)", r"([0-9]{2,4})\s*pages", r"([0-9]{2,4})\s*หน้า"],
        "price": [r"ราคา\s*[:：]?\s*(฿?\s*[0-9,]+(?:\.\d+)?\s*บาท?)", r"ราคาปกติ\s*[:：]?\s*([0-9,]+\s*บาท)"],
        "cover_type": [r"ประเภทปกหนังสือ\s*([^\n]+)", r"ชนิดปก\s*[:：]\s*([^\n]+)"],
        "dimensions": [r"ขนาด\s*[:：]\s*([0-9]+\s*x\s*[0-9]+\s*x\s*[0-9]+\s*มม\.)"],
        "weight": [r"น้ำหนัก\s*[:：]\s*([0-9]+\s*กรัม)"],
        "paper": [r"ชนิดกระดาษ\s*[:：]\s*([^\n]+)"],
    }

    for key, patterns in mappings.items():
        value = find_first(patterns, text)
        if value:
            facts[key] = value

    if "Daytrade Hunter" in text or "Day Trade Hunter" in text:
        facts.setdefault("title", "Daytrade Hunter เครื่องจักรผลิตเงินสด")

    strategies = []
    for name in ("Stop Hunt", "Breakout", "Buy on Dip", "Channel Trade", "Stock Quadrant"):
        if re.search(re.escape(name), text, flags=re.I):
            strategies.append(name)
    if strategies:
        facts["mentioned_concepts"] = ", ".join(strategies)

    toc_matches = re.findall(r"(บทที่\s*[0-9]+\s*[^\n]+)", text)
    if toc_matches:
        deduped = []
        for item in toc_matches:
            item = re.sub(r"\s+", " ", item).strip()
            if item not in deduped:
                deduped.append(item)
        facts["visible_table_of_contents"] = " | ".join(deduped[:20])

    return facts


def derive_public_notes(text: str) -> list[str]:
    """Create short paraphrased notes from public summary pages."""
    checks = [
        (
            ["กระแสเงินสด", "Daytrade"],
            "Daytrade is framed as short-term cash-flow generation from market volatility, not long-term portfolio compounding.",
        ),
        (
            ["ไม่เกิน 5 วัน"],
            "The public summary describes the holding period as short term, commonly within about five days.",
        ),
        (
            ["SCC", "ไม่มีการเคลื่อนไหว"],
            "High-priced or inactive stocks are described as less suitable for day trading.",
        ),
        (
            ["Scalper", "Ticker", "Volume"],
            "Scalping is associated with reading ticker flow and volume rather than relying only on chart patterns.",
        ),
        (
            ["Top Gainer"],
            "Candidate day-trade stocks can be found by watching daily top gainers and active movers.",
        ),
        (
            ["Mindset", "Stop loss"],
            "The summary stresses mindset, trading discipline, available buying power, and planned stop-loss execution.",
        ),
        (
            ["โลภ", "กลัว", "เสียดาย", "รู้งี้"],
            "Emotional risks highlighted include greed, fear, regret, and hindsight bias.",
        ),
        (
            ["เจ้า", "False Break"],
            "The summary warns that large players can create false breakouts or stop-loss traps around obvious technical levels.",
        ),
        (
            ["Stock Quadrant", "พื้นฐาน", "ขาขึ้น"],
            "Stock Quadrant combines fundamentals and technical trend quality to filter better trading candidates.",
        ),
        (
            ["แนวรับ", "แนวต้าน", "Trend Line", "Fibonacci"],
            "The toolset mentioned is intentionally simple: support/resistance, trend lines, moving averages, Fibonacci, and price patterns.",
        ),
        (
            ["Bid", "Offer"],
            "Bid-offer behavior is used as context for accumulation, distribution, and trend-stage interpretation.",
        ),
        (
            ["Breakout", "Buy On Dip", "Channel Trade"],
            "The public summary names four trading styles: panic/stop-hunt entries, breakout, buy-on-dip, and channel trading.",
        ),
        (
            ["รูปแบบเดียว", "ชำนาญ"],
            "A trader does not need to master every setup; specializing in one setup is presented as a viable path.",
        ),
    ]

    notes = []
    for needles, note in checks:
        if all(needle.lower() in text.lower() for needle in needles):
            notes.append(note)
    return notes


def collect_source(url: str, timeout: int) -> SourceResult:
    fetched_at = datetime.now(timezone.utc).isoformat()
    try:
        status, html = fetch_url(url, timeout)
        text = compact_text(html_to_text(html))
        return SourceResult(
            url=url,
            ok=True,
            fetched_at=fetched_at,
            status=status,
            title=extract_title(html, text),
            text=text,
            facts=extract_public_facts(text),
            derived_notes=derive_public_notes(text),
        )
    except HTTPError as exc:
        return SourceResult(url=url, ok=False, fetched_at=fetched_at, status=exc.code, error=str(exc))
    except (URLError, TimeoutError, OSError) as exc:
        return SourceResult(url=url, ok=False, fetched_at=fetched_at, error=str(exc))


def merge_facts(results: list[SourceResult]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for result in results:
        for key, value in result.facts.items():
            merged.setdefault(key, [])
            if value and value not in merged[key]:
                merged[key].append(value)
    return merged


def write_json(results: list[SourceResult], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notice": (
            "Publicly visible metadata only. This dataset intentionally avoids "
            "full-book extraction, paywall bypassing, or PDF downloading."
        ),
        "merged_facts": merge_facts(results),
        "sources": [asdict(result) for result in results],
    }
    path = output_dir / "daytrade_hunter_raw.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_markdown(results: list[SourceResult], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    merged = merge_facts(results)
    lines = [
        "# Daytrade Hunter - Public Research Notes",
        "",
        f"> Collected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "> Scope: public web metadata only; no full-book extraction or paywall bypass.",
        "",
        "## Merged Facts",
        "",
    ]

    if merged:
        for key in sorted(merged):
            values = "; ".join(merged[key])
            lines.append(f"- **{key}:** {values}")
    else:
        lines.append("- No facts extracted.")

    lines.extend(["", "## Sources", ""])
    for index, result in enumerate(results, 1):
        lines.append(f"### {index}. {result.title or result.url}")
        lines.append("")
        lines.append(f"- URL: {result.url}")
        lines.append(f"- OK: {result.ok}")
        if result.status:
            lines.append(f"- HTTP status: {result.status}")
        if result.error:
            lines.append(f"- Error: {result.error}")
        if result.facts:
            lines.append("- Extracted facts:")
            for key, value in sorted(result.facts.items()):
                lines.append(f"  - {key}: {value}")
        if result.text:
            preview = result.text[:1000].strip()
            lines.extend(["", "Public text preview:", "", "```text", preview, "```"])
        if result.derived_notes:
            lines.extend(["", "Derived notes:"])
            for note in result.derived_notes:
                lines.append(f"- {note}")
        lines.append("")

    path = output_dir / "daytrade_hunter_notes.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape public Daytrade Hunter metadata.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Directory for JSON/Markdown output.")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds.")
    parser.add_argument("--url", action="append", dest="urls", help="Extra source URL. Can be used multiple times.")
    parser.add_argument("--only-url", action="append", dest="only_urls", help="Use only this URL. Can be used multiple times.")
    return parser.parse_args()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    urls = args.only_urls or [*DEFAULT_SOURCES, *(args.urls or [])]

    print(f"Collecting {len(urls)} source(s)...")
    results: list[SourceResult] = []
    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] {url}")
        result = collect_source(url, args.timeout)
        results.append(result)
        status = "OK" if result.ok else "FAILED"
        print(f"  {status}: {result.title or result.error}")
        if idx < len(urls):
            time.sleep(max(args.delay, 0))

    output_dir = Path(args.output_dir)
    json_path = write_json(results, output_dir)
    md_path = write_markdown(results, output_dir)

    print("")
    print(f"Saved JSON: {json_path}")
    print(f"Saved Markdown: {md_path}")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
