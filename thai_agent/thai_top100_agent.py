"""
thai_top100_agent.py
100 หุ้นไทย (SET100) เรียงจาก Market Cap ใหญ่ไปเล็ก
วิเคราะห์ทุกตัว → ส่ง email ทุกวัน จ-ศ หลังตลาดปิด (ไทย)
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os, json, smtplib, datetime, time, argparse, threading
import numpy as np
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from concurrent.futures import ThreadPoolExecutor
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False
try:
    from groq import Groq
except ModuleNotFoundError:
    Groq = None

ROOT_DIR = Path(__file__).resolve().parents[1]
COMMON_DIR = ROOT_DIR / "common"
if not (COMMON_DIR / "beer_dna.py").exists():
    COMMON_DIR = ROOT_DIR
if str(COMMON_DIR) not in sys.path:
    sys.path.append(str(COMMON_DIR))

from beer_dna import BEER_DNA
from thai_homework_framework import (
    HOMEWORK_FRAMEWORK_TITLE,
    build_stock_homework_checklist,
    homework_email_guide_html,
    homework_prompt_block,
)

load_dotenv()

# ─── Global Lock for Output & Rate Limit ──────────────────────
print_lock = threading.Lock()
groq_lock = threading.Lock()
usage_lock = threading.Lock()
last_groq_call = 0.0

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

# ─── Config ───────────────────────────────────────────────────
KNOWLEDGE_JSON  = COMMON_DIR / "beervanon_cleaned.json"
DATA_DIR        = ROOT_DIR / "docs/thai-data"
HISTORY_DIR     = ROOT_DIR / "docs/thai-history-data"
METADATA_CACHE  = Path(__file__).with_name("thai_metadata_cache.json")
EMBEDDINGS_FILE = COMMON_DIR / "embeddings.npz"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL      = "llama-3.1-8b-instant"   # 6000 TPM limit
REPORT_TO        = os.getenv("GMAIL_USER", "patiphan.injob@gmail.com")
TOP_N            = 100
CALL_DELAY       = 15.0   # 10 วินาที เพื่อให้รอดจาก 6000 TPM (Token Per Minute)
GITHUB_PAGES_URL = "https://patiphaninjob-lang.github.io/beer-vanon-agents"
RUN_REQUEST_ID   = os.getenv("RUN_REQUEST_ID", "").strip()
RUN_REQUEST_SOURCE = os.getenv("RUN_REQUEST_SOURCE", "").strip()
RUN_REQUESTED_BY = os.getenv("RUN_REQUESTED_BY", "").strip()
def detect_report_phase() -> str:
    phase = os.getenv("RUN_PHASE", "").strip().lower()
    if phase in {"premarket", "postmarket", "manual"}:
        return phase
    
    import datetime
    try:
        tz_bangkok = datetime.timezone(datetime.timedelta(hours=7))
        now_bk = datetime.datetime.now(tz_bangkok)
    except Exception:
        now_bk = datetime.datetime.now()
        
    hour = now_bk.hour
    if hour < 6:
        return "premarket"
    elif hour < 12:
        return "postmarket"
    else:
        return "premarket"

RUN_PHASE = detect_report_phase()
THAI_TOP100_ENABLED = os.getenv("THAI_TOP100_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}
THAI_NOTES_FILE = ROOT_DIR / "docs/thai/notes/notes.json"
THAI_USAGE_FILE = DATA_DIR / "usage_stats.json"
INPUT_COST_PER_1M = 0.05
OUTPUT_COST_PER_1M = 0.08
THAI_MARKET_INDEX_KEYS = ("set", "set50", "set100")


def normalized_run_phase() -> str:
    return RUN_PHASE if RUN_PHASE in {"premarket", "postmarket"} else "legacy"


def archive_key_for_date(day: datetime.date) -> str:
    date_key = day.strftime("%Y-%m-%d")
    phase = normalized_run_phase()
    return f"{date_key}-{phase}" if phase != "legacy" else date_key


def build_archive_health(payload: dict, expected_total: int = TOP_N) -> dict:
    stocks = payload.get("stocks", [])
    market_indices = payload.get("market_indices") or {}
    test_run = bool(payload.get("test_run"))

    missing_charts = [s.get("ticker", "?") for s in stocks if not s.get("chart_b64")]
    incomplete_homework = [
        s.get("ticker", "?")
        for s in stocks
        if len(s.get("homework_checklist") or []) != 6
    ]
    zero_market_cap = [s.get("ticker", "?") for s in stocks if not s.get("market_cap")]
    missing_news = [s.get("ticker", "?") for s in stocks if not s.get("news")]
    missing_market_indices = [
        key for key in THAI_MARKET_INDEX_KEYS if key not in market_indices
    ]
    single_point_indices = [
        key for key, data in market_indices.items()
        if data.get("quality") == "single_point"
    ]

    issues = []
    if not test_run and len(stocks) != expected_total:
        issues.append(f"stock_count {len(stocks)}/{expected_total}")
    if missing_charts:
        issues.append(f"missing_charts {len(missing_charts)}")
    if incomplete_homework:
        issues.append(f"incomplete_homework {len(incomplete_homework)}")
    if missing_news:
        issues.append(f"missing_news {len(missing_news)}")
    if missing_market_indices:
        issues.append(f"missing_market_indices {','.join(missing_market_indices)}")
    if single_point_indices:
        issues.append(f"single_point_indices {','.join(single_point_indices)}")
    if zero_market_cap:
        issues.append(f"zero_market_cap {len(zero_market_cap)}")

    return {
        "status": "ok" if not issues else "warning",
        "issues": issues,
        "counts": {
            "stocks": len(stocks),
            "expected_stocks": expected_total if not test_run else len(stocks),
            "charts": len(stocks) - len(missing_charts),
            "news": len(stocks) - len(missing_news),
            "homework_complete": len(stocks) - len(incomplete_homework),
            "market_indices": len(market_indices),
        },
        "missing": {
            "charts": missing_charts[:20],
            "news": missing_news[:20],
            "homework": incomplete_homework[:20],
            "market_indices": missing_market_indices,
            "single_point_indices": single_point_indices,
            "market_cap": zero_market_cap[:20],
        },
    }


def write_status_file(docs_dir: Path, payload: dict, archive_url: str) -> None:
    status_path = docs_dir / "status.json"
    existing = {}
    if status_path.exists():
        try:
            existing = json.loads(status_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    phase = payload.get("run_phase") or "legacy"
    entry = {
        "date": payload.get("date"),
        "archive_key": payload.get("archive_key") or payload.get("date"),
        "run_phase": phase,
        "generated": payload.get("generated"),
        "url": archive_url,
        "health": payload.get("health", {}),
    }

    phases = existing.get("phases") if isinstance(existing.get("phases"), dict) else {}
    phases[phase] = entry

    status_payload = {
        "updated": datetime.datetime.now().isoformat(),
        "latest": entry,
        "phases": phases,
    }
    status_path.write_text(
        json.dumps(status_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def record_thai_usage(model: str, prompt_tokens: int, completion_tokens: int) -> dict:
    """Record Thai-agent usage without writing to the US dashboard data path."""
    with usage_lock:
        THAI_USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        stats = {
            "model": model,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_cost": 0.0,
            "last_updated": "",
            "sessions": [],
        }
        if THAI_USAGE_FILE.exists():
            try:
                stats.update(json.loads(THAI_USAGE_FILE.read_text(encoding="utf-8")))
            except Exception:
                pass

        prompt_tokens = int(prompt_tokens or 0)
        completion_tokens = int(completion_tokens or 0)
        cost = (prompt_tokens / 1_000_000 * INPUT_COST_PER_1M) + (completion_tokens / 1_000_000 * OUTPUT_COST_PER_1M)
        stats["model"] = model
        stats["total_prompt_tokens"] = int(stats.get("total_prompt_tokens", 0)) + prompt_tokens
        stats["total_completion_tokens"] = int(stats.get("total_completion_tokens", 0)) + completion_tokens
        stats["total_cost"] = float(stats.get("total_cost", 0.0)) + cost
        stats["last_updated"] = datetime.datetime.now().isoformat()

        today = datetime.date.today().isoformat()
        sessions = stats.setdefault("sessions", [])
        session = next((s for s in sessions if s.get("date") == today), None)
        if not session:
            session = {"date": today, "prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
            sessions.append(session)
        session["prompt_tokens"] = int(session.get("prompt_tokens", 0)) + prompt_tokens
        session["completion_tokens"] = int(session.get("completion_tokens", 0)) + completion_tokens
        session["cost"] = float(session.get("cost", 0.0)) + cost

        THAI_USAGE_FILE.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        return stats


def get_thai_usage_status_line() -> str:
    if not THAI_USAGE_FILE.exists():
        return "Usage: No Thai data"
    try:
        stats = json.loads(THAI_USAGE_FILE.read_text(encoding="utf-8"))
        today = datetime.date.today().isoformat()
        session = next(
            (s for s in stats.get("sessions", []) if s.get("date") == today),
            {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0},
        )
        tokens = int(session.get("prompt_tokens", 0)) + int(session.get("completion_tokens", 0))
        return f"Thai Usage: {tokens:,} tokens (${float(session.get('cost', 0.0)):.4f})"
    except Exception:
        return "Usage: Error reading Thai stats"

# SET100 Tickers
TH_UNIVERSE = [
    "AAV.BK", "ADVANC.BK", "AEONTS.BK", "AMATA.BK", "AOT.BK", "AP.BK", "ASW.BK", "AWC.BK", "BAM.BK", "BANPU.BK", 
    "BA.BK", "BBL.BK", "BCH.BK", "BCP.BK", "BCPG.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", "BH.BK", "BJC.BK", 
    "BLA.BK", "BTG.BK", "BTS.BK", "CBG.BK", "CENTEL.BK", "CHG.BK", "CK.BK", "CKP.BK", "COM7.BK", "CPALL.BK", 
    "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "DOHOME.BK", "EA.BK", "EGCO.BK", "ERW.BK", "GLOBAL.BK", "GPSC.BK", 
    "GULF.BK", "GUNKUL.BK", "HANA.BK", "HMPRO.BK", "ICHI.BK", "INTUCH.BK", "IRPC.BK", "ITC.BK", "IVL.BK", "JAS.BK", 
    "JMART.BK", "JMT.BK", "KBANK.BK", "KCE.BK", "KKP.BK", "KTB.BK", "KTC.BK", "LANNA.BK", "LH.BK", "MASTER.BK", 
    "MBK.BK", "MC.BK", "MEGA.BK", "MINT.BK", "MTC.BK", "NEX.BK", "OR.BK", "ORI.BK", "OSP.BK", "PLANB.BK", 
    "PRM.BK", "PSH.BK", "PSL.BK", "PTG.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "QH.BK", "RATCH.BK", "SAWAD.BK", 
    "SCB.BK", "SCC.BK", "SCGP.BK", "SINGER.BK", "SIRI.BK", "SISB.BK", "SPALI.BK", "SPRC.BK", "STA.BK", "STEC.BK", 
    "STGT.BK", "TASCO.BK", "TCAP.BK", "THANI.BK", "THG.BK", "TIDLOR.BK", "TIPH.BK", "TISCO.BK", "TKN.BK", "TOP.BK", 
    "TPIPL.BK", "TPIPP.BK", "TRUE.BK", "TTA.BK", "TTB.BK", "TTW.BK", "TU.BK", "TVO.BK", "VGI.BK", "WHA.BK", "WHAUP.BK"
]
TH_UNIVERSE = list(dict.fromkeys(TH_UNIVERSE))   # deduplicate


# ─── Knowledge Base ───────────────────────────────────────────

def load_knowledge():
    path = Path(KNOWLEDGE_JSON)
    if not path.exists():
        return [], None, None
    posts = json.loads(path.read_text(encoding="utf-8"))
    emb_path = Path(EMBEDDINGS_FILE)
    if not emb_path.exists():
        return posts, None, None
    from sentence_transformers import SentenceTransformer
    model      = SentenceTransformer(EMBED_MODEL)
    embeddings = np.load(emb_path)["embeddings"].astype("float32")
    return posts, embeddings, model


def search_knowledge(query: str, posts, embeddings, embed_model, top_k=3, query_vector=None) -> str:
    if embed_model is not None and embeddings is not None:
        if query_vector is None:
            query_vector = embed_model.encode([query], normalize_embeddings=True)[0].astype("float32")
        scores  = embeddings @ query_vector
        top_idx = np.argsort(scores)[::-1][:top_k]
        relevant = [posts[i] for i in top_idx]
    else:
        words   = set(query.lower().split())
        scored  = [(sum(1 for w in words if w in p.get("content","").lower() and len(w)>2), p)
                   for p in posts]
        relevant = [p for s,p in sorted(scored, reverse=True) if s > 0][:top_k]
    parts, total = [], 0
    for p in relevant:
        chunk = p.get("content","")[:300]
        if total + len(chunk) > 800:
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n\n---\n\n".join(parts) or "ไม่พบข้อมูล"


def _fallback_homework_analysis(stock: dict, knowledge_ctx: str = "", user_notes: list = None) -> list[dict]:
    """Build a deterministic Chapter 34 homework set when Groq output is missing."""
    base_items = build_stock_homework_checklist(stock)
    direction = "ขึ้น" if stock.get("pct_change", 0) > 0 else "ลง"
    note_hint = f" คุณมีโน้ตอ้างอิง {len(user_notes)} รายการ" if user_notes else ""
    knowledge_hint = ""
    if knowledge_ctx:
        knowledge_hint = knowledge_ctx.strip().splitlines()[0][:220]

    insights = {
        "ธุรกิจ": (
            f"{stock['ticker']} อยู่ในกลุ่ม {stock.get('sector', 'N/A')} "
            f"และราคาวันนี้{direction} {abs(stock.get('pct_change', 0)):.1f}% "
            f"ให้โฟกัสว่าการเติบโตมาจากอะไรจริง{note_hint}"
        ),
        "ตัวเลข": (
            f"ดู market cap rank #{stock.get('rank', '-')}, volume {stock.get('volume', 0):,}, "
            f"และ P/E {stock.get('pe_ratio') or 'N/A'} ว่าราคาแพงหรือยังถูกเมื่อเทียบกับ growth"
        ),
        "การสื่อสาร": (
            "เช็กว่าข่าวล่าสุดหรือข้อมูลผู้บริหารเล่า story เดียวกับ thesis หรือไม่ "
            "ถ้ามีความขัดกันให้ระวังการตีความเองเกินข้อมูล"
        ),
        "คู่แข่ง": (
            f"เปรียบเทียบ {stock['ticker']} กับคู่แข่งหลักใน {sector if (sector:=stock.get('sector')) else 'ตลาด'} "
            f"ใครโตจริง ใครแพงเกิน ใครเสียเปรียบ"
        ),
        "ผู้บริหาร": (
            "ตรวจว่าผู้บริหารพูดเรื่อง capital allocation, growth และ risk management สม่ำเสมอไหม "
            "แล้วพฤติกรรมสอดคล้องกับ thesis หรือไม่"
        ),
        "แผนของเรา": (
            f"ถ้า thesis ยังไม่ชัด ให้รอดู/หั่น/ถือ ตาม framework ของคุณเองบนข้อมูลชุดนี้ "
            f"โดยใช้ข่าวและ knowledge context เป็นตัวช่วยตัดสินใจ"
        ),
    }

    if knowledge_hint:
        insights["ธุรกิจ"] += f" | knowledge hint: {knowledge_hint}"

    return [
        {
            "topic": item["topic"],
            "insight": insights.get(item["topic"], item.get("prompt", "")),
        }
        for item in base_items
    ]


def _normalize_homework_analysis(stock: dict, homework_items, knowledge_ctx: str = "", user_notes: list = None) -> list[dict]:
    """Guarantee a complete six-item Chapter 34 homework list."""
    fallback_items = _fallback_homework_analysis(stock, knowledge_ctx, user_notes)
    fallback_map = {item["topic"]: item["insight"] for item in fallback_items}
    ordered_topics = [item["topic"] for item in fallback_items]

    if not isinstance(homework_items, list):
        return fallback_items

    raw_map = {}
    for item in homework_items:
        if not isinstance(item, dict):
            continue
        topic = str(item.get("topic", "")).strip()
        if not topic:
            continue
        insight = str(item.get("insight", "")).strip()
        raw_map[topic] = insight or fallback_map.get(topic, "")

    return [
        {
            "topic": topic,
            "insight": raw_map.get(topic, fallback_map.get(topic, "")),
        }
        for topic in ordered_topics
    ]


# ─── Market Cap Ranking ────────────────────────────────────────

def fetch_market_caps(tickers: list) -> dict:
    """ดึง market cap แบบ concurrent"""
    import yfinance as yf

    def _get(t):
        try:
            fi = yf.Ticker(t).fast_info
            return t, getattr(fi, "market_cap", 0) or 0
        except Exception:
            return t, 0

    safe_print(f"  ดึง market cap {len(tickers)} หุ้นไทย (parallel)...")
    with ThreadPoolExecutor(max_workers=20) as ex:
        results = dict(ex.map(_get, tickers))
    return results


# ─── Stock Data ───────────────────────────────────────────────

def _parse_news(n: dict) -> dict:
    content = n.get("content", {})
    if content:
        title    = content.get("title", "")
        summary  = (content.get("summary") or "")[:220]
        provider = (content.get("provider") or {}).get("displayName", "")
        pub_raw  = content.get("pubDate", "")
        date_str = pub_raw[:10] if pub_raw else ""
        url      = ((content.get("canonicalUrl") or {}).get("url")
                    or (content.get("clickThroughUrl") or {}).get("url", ""))
    else:
        title    = n.get("title", "")
        summary  = (n.get("summary") or "")[:220]
        provider = n.get("publisher", "")
        ts       = n.get("providerPublishTime", 0)
        date_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""
        url      = n.get("link", "")
    return {"title": title, "summary": summary, "provider": provider, "date": date_str, "url": url}


def _tv_url(ticker: str, exchange_code: str = "") -> str:
    # สำหรับไทย TradingView มักใช้ SET:TICKER
    ticker_only = ticker.split(".")[0]
    return f"https://www.tradingview.com/chart/?symbol=SET:{ticker_only}"


def _safe_get_stock_context(ticker: str, rank: int, mktcap: float = 0, hist_df=None) -> dict:
    import yfinance as yf
    tk = yf.Ticker(ticker)
    
    # แยกไฟล์ cache สำหรับหุ้นไทย
    cache_file = METADATA_CACHE
    cache = {}
    if cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    stock_info = cache.get(ticker, {})
    
    if not stock_info:
        info = tk.info or {}
        stock_info = {
            "name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector", "N/A"),
            "pe_ratio": info.get("trailingPE"),
            "exchange": info.get("exchange", "SET"),
            "homework_34": None, # Initial empty homework
            "homework_updated": None
        }
        cache[ticker] = stock_info
        try:
            cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    if hist_df is None:
        hist = tk.history(period="5d")
    else:
        hist = hist_df

    price_now  = float(hist["Close"].iloc[-1]) if not hist.empty else 0
    price_prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price_now
    pct_change = (price_now - price_prev) / price_prev * 100 if price_prev else 0
    volume     = int(hist["Volume"].iloc[-1]) if not hist.empty else 0

    try:
        # Increase news count and details for deep analysis
        raw_news  = tk.news[:5] if tk.news else []
        news_list = [_parse_news(n) for n in raw_news]
        news_text = "\n".join(
            f"- [{n['provider']}] {n['title']}" + (f"\n  {n['summary']}" if n.get("summary") else "")
            for n in news_list
        ) if news_list else "ไม่มีข่าว"
    except Exception:
        news_list, news_text = [], "ไม่มีข่าว"

    return {
        "ticker":     ticker,
        "name":       stock_info.get("name", ticker),
        "sector":     stock_info.get("sector", "N/A"),
        "price":      price_now,
        "pct_change": pct_change,
        "volume":     volume,
        "market_cap": mktcap or stock_info.get("market_cap", 0),
        "pe_ratio":   stock_info.get("pe_ratio"),
        "news":       news_text,
        "news_list":  news_list,
        "rank":       rank,
        "tv_url":     _tv_url(ticker, stock_info.get("exchange", "")),
        "cached_homework": stock_info.get("homework_34"), # Return cached homework if exists
    }


# ─── Chart Generator ─────────────────────────────────────────

def generate_mini_chart_b64(ticker: str, hist_df=None) -> bytes:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import io, base64
        import yfinance as yf

        if hist_df is None:
            hist = yf.Ticker(ticker).history(period="3mo")
        else:
            hist = hist_df

        if len(hist) < 5:
            return b""

        BG    = "#131722"
        GREEN = "#26a69a"
        RED   = "#ef5350"

        fig, ax = plt.subplots(figsize=(4, 1.1))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        opens  = hist["Open"].values
        closes = hist["Close"].values
        highs  = hist["High"].values
        lows   = hist["Low"].values
        n      = len(hist)

        for i in range(n):
            up      = closes[i] >= opens[i]
            color   = GREEN if up else RED
            body_lo = min(opens[i], closes[i])
            body_h  = max(abs(closes[i] - opens[i]), (highs[i] - lows[i]) * 0.05)
            ax.add_patch(mpatches.Rectangle(
                (i - 0.38, body_lo), 0.76, body_h, color=color, zorder=2
            ))
            ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=0.7, zorder=1)

        pad = (highs.max() - lows.min()) * 0.04
        ax.set_xlim(-0.8, n - 0.2)
        ax.set_ylim(lows.min() - pad, highs.max() + pad)
        ax.axis("off")
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        buf = io.BytesIO()
        fig.savefig(buf, format="jpeg", dpi=90,
                    facecolor=BG, edgecolor="none",
                    bbox_inches="tight", pad_inches=0.02,
                    pil_kwargs={"quality": 60, "optimize": True})
        plt.close(fig)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        safe_print(f"  chart error [{ticker}]: {e}")
        return b""


# ─── Market Indices ───────────────────────────────────────────

def fetch_market_indices() -> dict:
    import yfinance as yf, base64
    indices = {"^SET.BK": "set", "^SET50.BK": "set50", "^SET100.BK": "set100"}
    result  = {}
    for symbol, key in indices.items():
        try:
            hist = yf.Ticker(symbol).history(period="3mo").dropna(subset=["Close"])
            if hist.empty:
                continue
            price = float(hist["Close"].iloc[-1])
            if len(hist) >= 2:
                prev = float(hist["Close"].iloc[-2])
                pct = (price - prev) / prev * 100 if prev else 0
                quality = "ok"
            else:
                pct = 0
                quality = "single_point"
            chart = generate_mini_chart_b64(symbol, hist_df=hist)
            result[key] = {
                "price":      round(price, 2),
                "pct_change": round(pct, 2),
                "chart_b64":  base64.b64encode(chart).decode() if chart else "",
                "symbol":     symbol,
                "quality":    quality,
            }
        except Exception as e:
            safe_print(f"   ⚠️ {symbol}: {e}")
    return result


# ─── User Notes ───────────────────────────────────────────────

def _firestore_value_to_python(value):
    if not isinstance(value, dict):
        return None
    if "mapValue" in value:
        fields = value["mapValue"].get("fields", {})
        return {key: _firestore_value_to_python(val) for key, val in fields.items()}
    if "arrayValue" in value:
        return [_firestore_value_to_python(val) for val in value["arrayValue"].get("values", [])]
    if "stringValue" in value or "timestampValue" in value:
        return value.get("stringValue", value.get("timestampValue"))
    if "integerValue" in value:
        return int(value["integerValue"])
    if "doubleValue" in value:
        return float(value["doubleValue"])
    if "booleanValue" in value:
        return bool(value["booleanValue"])
    if "nullValue" in value:
        return None
    return None


def _load_firestore_notes(doc_path: str) -> dict:
    try:
        from urllib.parse import quote
        from urllib.request import urlopen

        encoded_path = "/".join(quote(part, safe="") for part in doc_path.split("/"))
        url = f"https://firestore.googleapis.com/v1/projects/beam-7645f/databases/(default)/documents/{encoded_path}"
        with urlopen(url, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        notes = _firestore_value_to_python(payload.get("fields", {}).get("notes", {}))
        return notes if isinstance(notes, dict) else {}
    except Exception as e:
        safe_print(f"   ⚠️ firestore notes fallback: {e}")
        return {}


def load_user_notes() -> dict:
    notes = _load_firestore_notes("thai-data/thai_top100_notes")
    if notes:
        return notes

    for path in (THAI_NOTES_FILE, ROOT_DIR / "dashboard/thai/notes/notes.json"):
        if not path.exists():
            continue
        try:
            notes = json.loads(path.read_text(encoding="utf-8"))
            return notes if isinstance(notes, dict) else {}
        except Exception:
            continue
    return {}


def extract_ticker_history(all_hist, ticker: str):
    if all_hist is None:
        return None
    try:
        columns = all_hist.columns
        if getattr(columns, "nlevels", 1) > 1:
            symbols = set(columns.get_level_values(0))
            if ticker in symbols:
                return all_hist[ticker]
        return all_hist
    except Exception:
        return None


# ─── Combined Analysis ────────────────────────────────────────

def _flatten_content(content) -> str:
    if isinstance(content, dict):
        return "\n".join(f"• {k}: {v}" for k, v in content.items())
    if isinstance(content, list):
        return "\n".join(f"• {item}" for item in content)
    return str(content or "").strip()


def combined_analysis(stock: dict, knowledge_ctx: str, user_notes: list = None) -> dict:
    direction = "ขึ้น" if stock["pct_change"] > 0 else "ลง"
    
    # Persistent Homework Logic: Use cached version if available
    cached_hw = stock.get("cached_homework")
    hw_instruction = ""
    if cached_hw:
        hw_ctx = "\n".join([f"- {item['topic']}: {item['insight']}" for item in cached_hw])
        hw_instruction = f"""
ข้อมูลการบ้านเดิม (จาก Cache):
{hw_ctx}

ไม่ต้องเขียนการบ้านใหม่ ให้ใช้ข้อมูลเดิมเป็นหลัก แต่ถ้าข่าววันนี้กระทบต่อการบ้านข้อไหน ให้ระบุในส่วน 'note_review' แทน
"""
    else:
        hw_instruction = "เขียนวิเคราะห์การบ้าน 6 ด้าน (บทที่ 34) ให้ครบถ้วน"

    fallback  = {
        "interpretation": f"วิเคราะห์ {stock['ticker']} กลุ่ม {stock['sector']} วันนี้ {direction} {abs(stock['pct_change']):.1f}%",
        "beer_view": "ใช้ framework สำรองเนื่องจาก API ขัดข้อง",
        "homework_analysis": cached_hw or _fallback_homework_analysis(stock, knowledge_ctx, user_notes),
        "note_review": None,
        "analysis_status": "fallback",
    }

    # Selective BEER_DNA context (Keep it minimal to save space for News)
    dna_blocks = BEER_DNA.split("━━━")
    dna_context = dna_blocks[0] # Title + Basic
    for b in dna_blocks:
        if "7 หลักการ" in b or "Stock Quadrant (SQ)" in b:
            dna_context += "\n" + b.strip()

    notes_ctx = ""
    if user_notes:
        lines = [f"- {n['date']}: {n['note']}" for n in user_notes[:3]]
        notes_ctx = "\n\n🌡️ อารมณ์ตลาดจากโน้ต:\n" + "\n".join(lines)

    # Focus PROMPT on DEEP NEWS
    prompt = f"""คุณคือ Beer Vanon เทรดเดอร์มือโปร วิเคราะห์หุ้นไทย {stock['ticker']} ({stock['name']})
ราคา: {stock['price']:.2f} THB ({direction} {abs(stock['pct_change']):.1f}%) | Sector: {stock['sector']}
Mkt Cap Rank: #{stock['rank']} | Vol: {stock['volume']:,}

DNA ของคุณ (ใช้คำศัพท์และหลักการเหล่านี้ในการวิเคราะห์):
{dna_context[:600]}

ข่าววันนี้:
{stock['news'][:1500]}
{knowledge_ctx[:300]}{notes_ctx}

{hw_instruction}

ให้ตอบเป็น JSON (ภาษาไทย) โครงสร้างดังนี้:
{{
  "interpretation": "สรุปข่าวและวิเคราะห์นัยสำคัญต่อราคา (ขยี้เนื้อหาให้แน่น ห้ามคัดลอกประโยคนี้)",
  "beer_view": "ความเห็นสไตล์ Beer (ระบุรหัส SQ และมองว่าเป็นหุ้นรูปแบบไหนใน 7 รูปแบบ เช่น 'เข็มฉีดยา' หรือรูปแบบ Daytrade)",
  "homework_analysis": [
    {{ "topic": "ธุรกิจ", "insight": "..." }},
    {{ "topic": "ตัวเลข", "insight": "..." }},
    {{ "topic": "การสื่อสาร", "insight": "..." }},
    {{ "topic": "คู่แข่ง", "insight": "..." }},
    {{ "topic": "ผู้บริหาร", "insight": "..." }},
    {{ "topic": "แผนของเรา", "insight": "..." }}
  ],
  "note_review": "ผลกระทบต่อการบ้านเดิม/อารมณ์ตลาด (ถ้ามี)"
}}"""

    if Groq is None or not os.getenv("GROQ_API_KEY"):
        return fallback

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    try:
        global last_groq_call
        with groq_lock:
            now = time.time()
            elapsed = now - last_groq_call
            if elapsed < CALL_DELAY:
                time.sleep(CALL_DELAY - elapsed)
            last_groq_call = time.time()

        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": "คุณคือ Beer Vanon เทรดเดอร์สาย Survivor Trade วิเคราะห์หุ้นด้วยความเฉียบคม ใช้ภาษาไทยที่เป็นกันเองแต่เป็นมืออาชีพ (ไม่ต้องทักทาย) ให้คำแนะนำตามหลักการ EMA, SQ, Bid-Offer และการบ้านบทที่ 34"},
                      {"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )
        
        # Track usage
        try:
            record_thai_usage(GROQ_MODEL, resp.usage.prompt_tokens, resp.usage.completion_tokens)
        except Exception:
            pass

        data = json.loads(resp.choices[0].message.content)
        data["interpretation"] = _flatten_content(data.get("interpretation"))
        data["beer_view"] = _flatten_content(data.get("beer_view"))
        
        # If we had cache, preserve it unless explicitly returned new one (usually preserve)
        if cached_hw and not data.get("homework_analysis"):
             data["homework_analysis"] = cached_hw
        else:
             data["homework_analysis"] = _normalize_homework_analysis(stock, data.get("homework_analysis"), knowledge_ctx, user_notes)
             # Surgical improvement: Save newly generated homework back to cache
             _save_homework_to_cache(stock["ticker"], data["homework_analysis"])
             
        return data
    except Exception as e:
        # Let rate limit errors bubble up so process_single_stock can retry
        err_msg = str(e).lower()
        if "429" in err_msg or "rate_limit" in err_msg:
            raise e

        safe_print(f"   ⚠️ Groq Error [{stock['ticker']}]: {e}")
        return fallback


def _save_homework_to_cache(ticker: str, homework: list):
    """Saves generated Chapter 34 homework to the metadata cache."""
    cache_file = METADATA_CACHE
    if not cache_file.exists():
        return
    try:
        cache = json.loads(cache_file.read_text(encoding="utf-8"))
        if ticker in cache:
            cache[ticker]["homework_34"] = homework
            cache[ticker]["homework_updated"] = datetime.date.today().isoformat()
            cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        safe_print(f"   ⚠️ Cache Update Error [{ticker}]: {e}")


# ─── Presentation & Reporting ─────────────────────────────────

def _fmt_mktcap(cap: float) -> str:
    if cap >= 1e12:
        return f"${cap/1e12:.2f}T"
    if cap >= 1e9:
        return f"${cap/1e9:.1f}B"
    if cap > 0:
        return f"${cap/1e6:.0f}M"
    return "N/A"


def stock_card(stock: dict, analysis_data: dict, chart_cid: str, user_notes: list = None) -> str:
    arrow = "▲" if stock["pct_change"] >= 0 else "▼"
    color = "#16c784" if stock["pct_change"] >= 0 else "#ea3943"
    cap_str = _fmt_mktcap(stock["market_cap"])
    tv_url = stock["tv_url"]

    chart_block = (
        f'<a href="{tv_url}" target="_blank"><img src="cid:{chart_cid}" style="width:100%;border-radius:5px"></a>'
        if chart_cid else ""
    )

    hw_items = "".join(
        f'<div style="border-left:2px solid #475569;padding:5px 10px;margin-bottom:5px;background:#0f172a">'
        f'<div style="color:#10b981;font-size:0.75em;font-weight:bold">{item["topic"]}</div>'
        f'<div style="color:#d1d5db;font-size:0.82em">{item["insight"]}</div></div>'
        for item in analysis_data.get("homework_analysis", [])
    )

    return f"""
<div style="background:#1e293b;border-radius:12px;padding:15px;margin-bottom:12px;border-left:4px solid {color}">
  <div style="color:#ffffff;font-size:1.1em;font-weight:bold">#{stock['rank']} {stock['ticker']} <span style="font-size:0.75em;font-weight:normal;color:#8a8f98">{stock['name']}</span></div>
  <div style="color:{color};font-weight:bold">${stock['price']:.2f} ({arrow} {abs(stock['pct_change']):.2f}%)</div>
  <div style="color:#a0a6b3;font-size:0.78em;margin:5px 0">{stock['sector']} | Mkt Cap: {cap_str}</div>
  {chart_block}
  <div style="margin-top:10px;padding:10px;background:#0f172a;border-radius:8px">
    <div style="color:#10b981;font-size:0.8em;font-weight:bold;margin-bottom:5px">🧭 {HOMEWORK_FRAMEWORK_TITLE}</div>
    {hw_items}
  </div>
  <div style="margin-top:10px;padding:10px;background:#0f172a;border-radius:8px;color:#d1d5db;font-size:0.9em">
    <div style="color:#10b981;font-weight:bold">🍺 วิเคราะห์</div>
    {analysis_data.get('interpretation','')}<br><br>
    <strong>Beer มองว่า:</strong> {analysis_data.get('beer_view','')}
  </div>
</div>"""


def save_to_web(stocks_data: list, today: datetime.date, market_indices: dict = None, test_run: bool = False) -> str:
    docs_dir = DATA_DIR
    docs_dir.mkdir(parents=True, exist_ok=True)
    date_key = today.strftime("%Y-%m-%d")
    archive_key = archive_key_for_date(today)

    import numpy as np
    avg_chg  = float(np.mean([s["stock"]["pct_change"] for s in stocks_data])) if stocks_data else 0
    gainers  = [s for s in stocks_data if s["stock"]["pct_change"] > 0]
    losers   = [s for s in stocks_data if s["stock"]["pct_change"] < 0]
    by_gain  = sorted(stocks_data, key=lambda s: s["stock"]["pct_change"], reverse=True)

    payload = {
        "date": date_key,
        "archive_key": archive_key,
        "generated": datetime.datetime.now().isoformat(),
        "run_phase": normalized_run_phase(),
        "run_request": {
            "id": RUN_REQUEST_ID,
            "source": RUN_REQUEST_SOURCE,
            "requested_by": RUN_REQUESTED_BY,
        },
        "test_run": test_run,
        "homework_framework": HOMEWORK_FRAMEWORK_TITLE,
        "homework_guide": homework_prompt_block("หุ้นไทย"),
        "market_indices": market_indices or {},
        "summary": {
            "total":       len(stocks_data),
            "gainers":     len(gainers),
            "losers":      len(losers),
            "avg_change":  round(avg_chg, 2),
            "top_gainer":  {"ticker": by_gain[0]["stock"]["ticker"],  "pct": round(by_gain[0]["stock"]["pct_change"], 2)}  if by_gain else {},
            "top_loser":   {"ticker": by_gain[-1]["stock"]["ticker"], "pct": round(by_gain[-1]["stock"]["pct_change"], 2)} if by_gain else {},
        },
        "stocks": [
            {
                "rank": s["stock"]["rank"],
                "ticker": s["stock"]["ticker"],
                "name": s["stock"]["name"],
                "sector": s["stock"]["sector"],
                "price": round(s["stock"]["price"], 2),
                "pct_change": round(s["stock"]["pct_change"], 2),
                "volume": s["stock"]["volume"],
                "market_cap": s["stock"]["market_cap"],
                "pe_ratio": round(s["stock"]["pe_ratio"], 1) if s["stock"].get("pe_ratio") else None,
                "tv_url": s["stock"]["tv_url"],
                "news": s["stock"].get("news_list", []),
                "analysis": f"{s['analysis_data'].get('interpretation','')}\n\nBeer มองว่า: {s['analysis_data'].get('beer_view','')}",
                "homework_checklist": s["analysis_data"].get("homework_analysis", []),
                "chart_b64": __import__("base64").b64encode(s["chart_bytes"]).decode() if s.get("chart_bytes") else "",
            }
            for s in stocks_data
        ],
    }
    payload["health"] = build_archive_health(payload)
    if payload["health"]["status"] != "ok":
        safe_print(f"  ⚠️ Thai archive health warning: {', '.join(payload['health']['issues'])}")

    serialized_payload = json.dumps(payload, ensure_ascii=False, indent=2)
    (docs_dir / f"{archive_key}.json").write_text(serialized_payload, encoding="utf-8")
    if archive_key != date_key:
        (docs_dir / f"{date_key}.json").write_text(serialized_payload, encoding="utf-8")
    
    idx_path = docs_dir / "index.json"
    dates = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else []
    if date_key not in dates:
        dates.insert(0, date_key)
        dates.sort(reverse=True)
    idx_path.write_text(json.dumps(dates, ensure_ascii=False), encoding="utf-8")

    phase_param = f"&phase={normalized_run_phase()}" if normalized_run_phase() != "legacy" else ""
    url = f"{GITHUB_PAGES_URL}/thai/index.html?date={date_key}{phase_param}"
    write_status_file(docs_dir, payload, url)
    return url


def save_history_data(stocks_data: list) -> None:
    out_dir = HISTORY_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    import yfinance as yf
    tickers = [s["stock"]["ticker"] for s in stocks_data]
    
    # 1. Save Individual Stocks (Reduced to 2y for performance)
    all_hist = yf.download(tickers, period="2y", group_by="ticker", threads=True, progress=False)
    for ticker in tickers:
        hist = extract_ticker_history(all_hist, ticker)
        if hist is None or hist.empty: continue
        candles = [[idx.strftime("%Y-%m-%d"), round(row["Open"],4), round(row["High"],4), round(row["Low"],4), round(row["Close"],4), int(row["Volume"])]
                   for idx, row in hist.dropna(subset=["Close"]).iterrows()]
        payload = {"ticker": ticker, "timeframe": "1D", "period": "2y", "candles": candles}
        (out_dir / f"{ticker}.json").write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    # 2. Save Market Index History (SET)
    try:
        mkt_hist = yf.Ticker("^SET.BK").history(period="2y")
        if not mkt_hist.empty:
            candles = [[idx.strftime("%Y-%m-%d"), round(row["Open"],4), round(row["High"],4), round(row["Low"],4), round(row["Close"],4), 0]
                       for idx, row in mkt_hist.dropna(subset=["Close"]).iterrows()]
            payload = {"ticker": "market", "timeframe": "1D", "period": "5y", "candles": candles}
            (out_dir / "market.json").write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    except Exception as e:
        safe_print(f"   ⚠️ Failed to save market history: {e}")


def build_completion_email(date_str: str, archive_url: str, count: int, test_run: bool = False) -> str:
    status_label = "✅ เสร็จสมบูรณ์" if count >= 100 else "⚠️ เสร็จบางส่วน"
    if test_run: status_label = "🧪 TEST RUN"
    
    return f"""
<div style="font-family:sans-serif;background:#0f172a;color:#c9d1d9;padding:20px;max-width:600px;border-radius:10px">
  <div style="font-size:1.4em;font-weight:bold;color:#ffffff;margin-bottom:10px">🇹🇭 Thai Top 100</div>
  <div style="font-size:1.1em;margin-bottom:20px">{date_str}</div>
  
  <div style="background:#1e293b;padding:15px;border-radius:8px;border:1px solid #475569;margin-bottom:20px">
    <div style="font-size:0.9em;color:#8b949e">สถานะการทำงาน</div>
    <div style="font-size:1.2em;font-weight:bold;color:#58a6ff">{status_label}</div>
    <div style="margin-top:10px;font-size:0.9em">วิเคราะห์หุ้นไทยไปทั้งหมด <strong>{count}</strong> ตัว</div>
  </div>

  <div style="margin-bottom:25px">
    <a href="{archive_url}" style="display:inline-block;background:#238636;color:#ffffff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">
      🌐 ดูรายงานบน Web Archive
    </a>
  </div>

  {homework_email_guide_html()}

  <div style="font-size:0.8em;color:#8b949e;border-top:1px solid #475569;padding-top:15px;margin-top:20px">
    ระบบอัตโนมัติ Beer Vanon Stock Trading Knowledge System<br>
    © 2026 Beer Vanon Agent
  </div>
</div>
"""

def build_html_report(stocks_data: list, date_str: str, archive_url: str) -> str:
    cards = "".join([stock_card(s["stock"], s["analysis_data"], "") for s in stocks_data])
    return f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Beer Thai Top 100 Report - {date_str}</title>
    <style>
        body {{ background: #0f172a; color: #c9d1d9; font-family: sans-serif; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        a {{ color: #58a6ff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🇹🇭 Thai Top 100 Report</h1>
        <h3>{date_str}</h3>
        <p><a href="{archive_url}">🌐 ดูบน Web Archive</a></p>
        <hr style="border:0;border-top:1px solid #475569;margin:20px 0">
        {cards}
    </div>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--no-web", action="store_true")
    parser.add_argument("--no-email", action="store_true")
    parser.add_argument("--no-history", action="store_true")
    parser.add_argument("--out-html", type=str)
    parser.add_argument("--enable-thai", action="store_true", help="Run the prepared Thai agent while it is disabled by default")
    args = parser.parse_args()

    if not (args.enable_thai or THAI_TOP100_ENABLED):
        safe_print("🇹🇭 Thai Top 100 Agent is prepared but disabled.")
        safe_print("Set THAI_TOP100_ENABLED=1 or pass --enable-thai when you intentionally want to run it.")
        return

    try:
        tz_bangkok = datetime.timezone(datetime.timedelta(hours=7))
        now_bk = datetime.datetime.now(tz_bangkok)
    except Exception:
        now_bk = datetime.datetime.now()
        
    hour = now_bk.hour
    today = now_bk.date()
    
    if RUN_PHASE == "postmarket" and 6 <= hour < 12:
        today = today - datetime.timedelta(days=1)
    
    # 0. Safety Net Check: ถ้าเป็นระบบ Auto (schedule) และวันนี้ทำไปแล้ว (กดมือ) ให้ข้าม
    is_scheduled = os.getenv("GITHUB_EVENT_NAME") == "schedule"
    today_file_str = today.strftime("%Y-%m-%d")
    report_path = DATA_DIR / f"{archive_key_for_date(today)}.json"

    if is_scheduled and report_path.exists():
        try:
            existing_phase = json.loads(report_path.read_text(encoding="utf-8")).get("run_phase")
        except Exception:
            existing_phase = None
        if existing_phase == normalized_run_phase():
            safe_print(f"⚠️ [Safety Net] Thai {normalized_run_phase()} report already exists for {today_file_str}.")
            safe_print("⏭️ Skipping duplicate scheduled run for the same phase.")
            return

    date_str = today.strftime("%A, %d %B %Y")
    safe_print(f"\n🇹🇭 Thai Top 100 Agent — {date_str}\n{'='*55}")
    start_all = time.time()
    if RUN_REQUEST_ID or RUN_REQUEST_SOURCE or RUN_REQUESTED_BY or RUN_PHASE:
        safe_print(
            f"  run request: id={RUN_REQUEST_ID or '-'} source={RUN_REQUEST_SOURCE or '-'} requested_by={RUN_REQUESTED_BY or '-'} phase={normalized_run_phase()}"
        )

    # ── Checkpoint / Resume Logic (Unified) ──
    report_path = DATA_DIR / f"{archive_key_for_date(today)}.json"
    
    existing_results = {}
    if report_path.exists():
        try:
            today_data = json.loads(report_path.read_text(encoding="utf-8"))
            # If scheduled and today's report already exists, skip
            if os.getenv("GITHUB_EVENT_NAME") == "schedule" and today_data.get("run_phase") == normalized_run_phase() and not today_data.get("test_run"):
                safe_print(f"⚠️ [Safety Net] Thai {normalized_run_phase()} report already exists for {today_file_str}.")
                return
            
            if "stocks" in today_data:
                for s in today_data["stocks"]:
                    # Transform back to internal format for resume
                    existing_results[s["ticker"]] = {
                        "stock": {
                            "rank": s.get("rank"),
                            "ticker": s.get("ticker"),
                            "name": s.get("name"),
                            "sector": s.get("sector"),
                            "price": s.get("price"),
                            "pct_change": s.get("pct_change"),
                            "volume": s.get("volume"),
                            "market_cap": s.get("market_cap"),
                            "pe_ratio": s.get("pe_ratio"),
                            "tv_url": s.get("tv_url"),
                            "news_list": s.get("news", []),
                        },
                        "analysis_data": {
                            "interpretation": s.get("analysis", "").split("\n\nBeer มองว่า:")[0],
                            "beer_view": s.get("analysis", "").split("\n\nBeer มองว่า:")[1] if "\n\nBeer มองว่า:" in s.get("analysis", "") else "",
                            "homework_analysis": s.get("homework_checklist", []),
                        },
                        "chart_bytes": __import__("base64").b64decode(s["chart_b64"]) if s.get("chart_b64") else b"",
                        "chart_cid": f"chart_{s.get('ticker', '').replace('.BK','')}"
                    }
                safe_print(f"🔄 พบข้อมูลเดิม: ข้ามหุ้นที่วิเคราะห์ไปแล้ว {len(existing_results)} ตัว")
        except Exception as e:
            safe_print(f"⚠️ Resume error: {e}")

    safe_print("\n📚 โหลด knowledge base...")
    posts, embeddings, embed_model = load_knowledge()
    user_notes_db = load_user_notes()
    safe_print(f"   โน้ตของคุณ: {sum(len(v) for v in user_notes_db.values())} รายการ")

    safe_print("\n📊 จัดลำดับ Market Cap...")
    mkt_start = time.time()
    mktcaps = fetch_market_caps(TH_UNIVERSE)
    ranked_universe = sorted([t for t in TH_UNIVERSE if mktcaps.get(t, 0) > 0], key=lambda t: mktcaps[t], reverse=True)
    limit = args.limit or (5 if args.test else 100)
    top_stocks = ranked_universe[:limit]
    safe_print(f"   วิเคราะห์ {len(top_stocks)} หุ้น | อันดับ 1: {top_stocks[0]} ({_fmt_mktcap(mktcaps[top_stocks[0]])})")
    safe_print(f"   ⏱️ Fetch market cap: {time.time() - mkt_start:.1f}s")

    # Filter out already processed stocks
    stocks_to_process = [t for t in top_stocks if t not in existing_results]
    
    import yfinance as yf
    all_hist = None
    if stocks_to_process:
        safe_print(f"   ดึงข้อมูลราคา {len(stocks_to_process)} หุ้น (batch)...")
        hist_start = time.time()
        all_hist = yf.download(stocks_to_process, period="3mo", group_by='ticker', threads=True, progress=False)
        safe_print(f"   ⏱️ Batch history download: {time.time() - hist_start:.1f}s")

    stocks_data = list(existing_results.values())
    
    # ดึงดัชนีตลาดก่อน (เพื่อใช้ในการ save_to_web Incremental)
    market_indices = {}
    if not args.no_web:
        market_indices = fetch_market_indices()

    if stocks_to_process:
        safe_print(f"\n🔍 วิเคราะห์ {len(stocks_to_process)} หุ้นที่เหลือ (workers={args.workers})...")
        analysis_start = time.time()
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for t in stocks_to_process:
                rank = ranked_universe.index(t) + 1
                hist_df = extract_ticker_history(all_hist, t)
                futures.append(executor.submit(process_single_stock, t, rank, mktcaps[t], hist_df, "SET100 หุ้นไทย", posts, embeddings, embed_model, None, user_notes_db))
                time.sleep(0.5)
            for f in futures:
                res = f.result()
                if res: 
                    stocks_data.append(res)
                    # Incremental Save
                    if not args.no_web:
                        stocks_data.sort(key=lambda x: x["stock"]["rank"])
                        save_to_web(stocks_data, today, market_indices, test_run=args.test)
        safe_print(f"   ⏱️ Analysis completed in: {time.time() - analysis_start:.1f}s")
    else:
        safe_print("\n✅ ทุกหุ้นถูกวิเคราะห์ไปแล้ว")

    stocks_data.sort(key=lambda x: x["stock"]["rank"])

    if stocks_data:
        safe_print(f"\n🌐 บันทึก web archive (Final)...")
        archive_url = save_to_web(stocks_data, today, market_indices, test_run=args.test)
        if not args.no_history:
            save_history_data(stocks_data)
        
        # Build Report Email
        safe_print(f"\n📄 สร้างรายงาน ({len(stocks_data)} หุ้น)...")
        email_html = build_completion_email(date_str, archive_url, len(stocks_data), test_run=args.test)
        subject = f"🇹🇭 Thai Top 100 เสร็จแล้ว — {today.strftime('%d/%m/%Y')}"
        if args.test: subject = f"[TEST] {subject}"

        if args.out_html:
            report_html = build_html_report(stocks_data, date_str, archive_url)
            Path(args.out_html).write_text(report_html, encoding="utf-8")

        if not args.no_email:
            safe_print("📧 ส่ง email...")
            send_email(email_html, subject, None)
            
        safe_print(f"\n✅ เสร็จสิ้น! ใน {time.time() - start_all:.1f}s")

def process_single_stock(ticker, rank, mktcap, hist_df, query, posts, embeddings, embed_model, q_vec, notes_db):
    try:
        stock = _safe_get_stock_context(ticker, rank, mktcap, hist_df)
        # Surgical improvement: specific search query
        better_query = f"{stock['ticker']} {stock['sector']} {query}"
        ctx = search_knowledge(better_query, posts, embeddings, embed_model)
        analysis = combined_analysis(stock, ctx, notes_db.get(ticker))
        chart = generate_mini_chart_b64(ticker, hist_df)
        
        # Show usage in status line
        try:
            status_line = get_thai_usage_status_line()
            safe_print(f"   [{rank:3d}] {ticker:<10} → ✅ วิเคราะห์สำเร็จ | {status_line}")
        except Exception:
            safe_print(f"   [{rank:3d}] {ticker:<10} → ✅")
            
        return {"stock": stock, "analysis_data": analysis, "chart_bytes": chart, "chart_cid": f"chart_{rank}"}
    except Exception as e:
        safe_print(f"   [{rank:3d}] {ticker:<10} → ❌ {e}")
        return None

def send_email(text, subject, images):
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not user or not password: return
    msg = MIMEText(text)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = REPORT_TO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, password)
        server.sendmail(user, REPORT_TO, msg.as_string())

if __name__ == "__main__":
    main()
