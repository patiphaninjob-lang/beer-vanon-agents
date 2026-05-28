"""
beer_top100_agent.py
100 หุ้น US ขนาดใหญ่สุด (Market Cap) เรียงจากใหญ่ไปเล็ก
วิเคราะห์ทุกตัว → ส่ง email ทุกวัน จ-ศ หลังตลาดปิด
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
from dotenv import load_dotenv
from groq import Groq
from beer_dna import BEER_DNA
from beer_homework_framework import (
    HOMEWORK_FRAMEWORK_TITLE,
    build_stock_homework_checklist,
    homework_email_guide_html,
    homework_prompt_block,
)

load_dotenv()

# ─── Global Lock for Output & Rate Limit ──────────────────────
print_lock = threading.Lock()
groq_lock = threading.Lock()
last_groq_call = 0.0

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

# ─── Config ───────────────────────────────────────────────────
KNOWLEDGE_JSON  = "beervanon_cleaned.json"
EMBEDDINGS_FILE = "embeddings.npz"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL      = "llama-3.1-8b-instant"   # higher daily token limit สำหรับ 100 หุ้น
REPORT_TO        = os.getenv("GMAIL_USER", "patiphan.injob@gmail.com")
TOP_N            = 100
CALL_DELAY       = 2.1   # วินาที ระหว่าง Groq call (ป้องกัน rate limit 30 RPM)
GITHUB_PAGES_URL = "https://patiphaninjob-lang.github.io/beer-vanon-agents"
RUN_REQUEST_ID   = os.getenv("RUN_REQUEST_ID", "").strip()
RUN_REQUEST_SOURCE = os.getenv("RUN_REQUEST_SOURCE", "").strip()
RUN_REQUESTED_BY = os.getenv("RUN_REQUESTED_BY", "").strip()

# ~140 หุ้น universe → sort by market cap → take 100
US_UNIVERSE = [
    # ─ Tech / AI ─
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","ORCL","CRM",
    "AMD","ADBE","QCOM","INTC","TXN","AMAT","KLAC","LRCX","MU","MRVL",
    "ADI","NOW","INTU","SNPS","CDNS","CRWD","PANW","FTNT","ZS","IBM",
    # ─ Healthcare ─
    "LLY","UNH","JNJ","ABBV","MRK","PFE","BMY","AMGN","GILD","ISRG",
    "SYK","BSX","BDX","DHR","ZTS","ELV","CI","HUM","CVS","HCA",
    # ─ Financials ─
    "BRK-B","JPM","BAC","WFC","C","GS","MS","AXP","V","MA",
    "BLK","SPGI","MCO","ICE","CME","COF","USB","TFC","PNC","SCHW",
    # ─ Consumer Discretionary ─
    "HD","MCD","NKE","SBUX","TGT","LOW","DG","BKNG","MAR","HLT",
    # ─ Consumer Staples ─
    "WMT","COST","PG","KO","PEP","PM","MO","CL","MDLZ","GIS",
    # ─ Energy ─
    "XOM","CVX","COP","SLB","MPC","VLO","OXY","PSX","HAL","BKR",
    # ─ Industrials ─
    "GE","CAT","HON","RTX","LMT","NOC","BA","UPS","DE","UNP",
    "CSX","NSC","ETN","EMR","MMM","ROP",
    # ─ Communication ─
    "NFLX","TMUS","T","VZ","CMCSA","DIS",
    # ─ Materials ─
    "LIN","APD","ECL","FCX","NEM","SHW",
    # ─ Real Estate ─
    "PLD","AMT","EQIX","CCI","SPG",
    # ─ Utilities ─
    "NEE","SO","DUK","AEP","EXC",
]
US_UNIVERSE = list(dict.fromkeys(US_UNIVERSE))   # deduplicate


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
            f"เปรียบเทียบ {stock['ticker']} กับคู่แข่งใน sector เดียวกันว่ามี moat, scale, "
            f"หรือความเชื่อมั่นตลาดต่างกันตรงไหน"
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

    safe_print(f"  ดึง market cap {len(tickers)} หุ้น (parallel)...")
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


_TV_EXCHANGE = {
    "NMS":"NASDAQ","NGM":"NASDAQ","NCM":"NASDAQ",
    "NYQ":"NYSE","PCX":"NYSE","BTS":"NYSE",
    "ASE":"AMEX",
}

def _tv_url(ticker: str, exchange_code: str = "") -> str:
    ex     = _TV_EXCHANGE.get(exchange_code, "")
    symbol = f"{ex}:{ticker}" if ex else ticker
    return f"https://www.tradingview.com/chart/?symbol={symbol}"


def get_stock_context(ticker: str, rank: int, mktcap: float = 0, hist_df=None) -> dict:
    import yfinance as yf
    tk = yf.Ticker(ticker)
    
    # Try to load from local cache to avoid slow tk.info
    cache_file = Path("stock_metadata_cache.json")
    cache = {}
    if cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    stock_info = cache.get(ticker, {})
    
    if not stock_info:
        # Only fetch info if not in cache (Slow network call)
        info = tk.info or {}
        stock_info = {
            "name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector", "N/A"),
            "pe_ratio": info.get("trailingPE"),
            "exchange": info.get("exchange", ""),
        }
        # Update cache safely
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
        raw_news  = tk.news[:3] if tk.news else []
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
    }


# ─── Chart Generator ─────────────────────────────────────────

def generate_mini_chart_b64(ticker: str, hist_df=None) -> bytes:
    """Mini candlestick JPEG สไตล์ TradingView Screener — ~2.8KB ต่อรูป"""
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
        return buf.read()   # raw bytes — ใช้กับ CID attachment
    except Exception as e:
        safe_print(f"  chart error [{ticker}]: {e}")
        return b""


# ─── Market Indices ───────────────────────────────────────────

def fetch_market_indices() -> dict:
    """ดึง DJI, S&P500, NASDAQ พร้อม mini chart สำหรับ web archive"""
    import yfinance as yf, base64
    indices = {"^DJI": "dji", "^GSPC": "spx", "^IXIC": "ixic"}
    result  = {}
    for symbol, key in indices.items():
        try:
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) < 2:
                continue
            price = float(hist["Close"].iloc[-1])
            pct   = (price - float(hist["Close"].iloc[-2])) / float(hist["Close"].iloc[-2]) * 100
            chart = generate_mini_chart_b64(symbol)
            result[key] = {
                "price":      round(price, 2),
                "pct_change": round(pct, 2),
                "chart_b64":  base64.b64encode(chart).decode() if chart else "",
            }
        except Exception as e:
            safe_print(f"   ⚠️ {symbol}: {e}")
    return result


# ─── User Notes ───────────────────────────────────────────────

def load_user_notes() -> dict:
    try:
        from urllib.request import urlopen

        url = "https://raw.githubusercontent.com/patiphaninjob-lang/beer-vanon-agents/main/docs/notes/notes.json"
        with urlopen(url, timeout=15) as resp:
            payload = resp.read().decode("utf-8")
        notes = json.loads(payload)
        if isinstance(notes, dict):
            return notes
    except Exception as e:
        safe_print(f"   ⚠️ online notes fallback: {e}")

    path = Path("docs/notes/notes.json")
    if not path.exists():
        return {}
    try:
        notes = json.loads(path.read_text(encoding="utf-8"))
        return notes if isinstance(notes, dict) else {}
    except Exception:
        return {}


def extract_ticker_history(all_hist, ticker: str):
    """Return one ticker's OHLCV frame from yfinance batch output."""
    if all_hist is None:
        return None
    try:
        columns = all_hist.columns
        if getattr(columns, "nlevels", 1) > 1:
            symbols = set(columns.get_level_values(0))
            if ticker in symbols:
                return all_hist[ticker]
            alt = ticker.replace(".", "-")
            if alt in symbols:
                return all_hist[alt]
        return all_hist
    except Exception:
        return None


# ─── Combined Analysis ────────────────────────────────────────

def combined_analysis(stock: dict, knowledge_ctx: str, user_notes: list = None) -> dict:
    """ONE Groq call with JSON mode: วิเคราะห์ครบทุกมิติ (News + Beer Opinion + Ch34 Homework)"""
    client    = Groq(api_key=os.getenv("GROQ_API_KEY"))
    direction = "ขึ้น" if stock["pct_change"] > 0 else "ลง"
    fallback  = {
        "interpretation": (
            f"{stock['ticker']} อยู่ในกลุ่ม {stock.get('sector', 'N/A')} "
            f"และวันนี้{direction} {abs(stock.get('pct_change', 0)):.1f}% "
            f"แต่โมเดลวิเคราะห์ไม่ผ่าน จึงใช้ข้อมูลพื้นฐานและ framework สำรองแทน"
        ),
        "beer_view": (
            f"Beer view แบบสำรอง: ใช้ rank #{stock.get('rank', '-')}, volume, ข่าว และ context "
            f"เพื่อตัดสิน thesis ก่อน ไม่ควรเดาเกินข้อมูลที่มี"
        ),
        "homework_analysis": _fallback_homework_analysis(stock, knowledge_ctx, user_notes),
        "note_review": None,
        "analysis_status": "fallback",
    }

    notes_ctx = ""
    if user_notes:
        lines = [
            f"- {n['date']} (ราคา ${n.get('price','?')}, {'+' if n.get('pct_change',0)>0 else ''}{n.get('pct_change','?')}%): {n['note']}"
            for n in user_notes[:3]
        ]
        notes_ctx = "\n\n🌡️ อารมณ์ตลาดที่นักลงทุนเคยจับได้:\n" + "\n".join(lines)

    prompt = f"""วิเคราะห์หุ้น {stock['ticker']} ({stock['name']})
ราคา: ${stock['price']:.2f} ({direction} {abs(stock['pct_change']):.1f}%) | Sector: {stock['sector']}
Mkt Cap Rank: #{stock['rank']} | Vol: {stock['volume']:,} | P/E: {stock['pe_ratio'] or 'N/A'}

หลักการ Beer Vanon:
{BEER_DNA[:250]}

ข่าว:
{stock['news'][:400]}

ความรู้เพิ่มเติม:
{knowledge_ctx[:300]}{notes_ctx}

ให้ตอบเป็น JSON (ภาษาไทย ตรงประเด็น) โครงสร้างดังนี้:
{{
  "interpretation": "วิเคราะห์เจาะลึกรายละเอียดข่าว (Detail, Sentiment, Implication)",
  "beer_view": "ความเห็นสั้นๆ (ความน่าสนใจ SQ และจุด Circuit Breaker)",
  "homework_analysis": [
    {{ "topic": "ธุรกิจ", "insight": "ขายอะไร ลูกค้าคือใคร" }},
    {{ "topic": "ตัวเลข", "insight": "รายได้ กำไร หนี้" }},
    {{ "topic": "การสื่อสาร", "insight": "ผู้บริหารพูดอะไร" }},
    {{ "topic": "คู่แข่ง", "insight": "ใครดีกว่า แย่กว่า" }},
    {{ "topic": "ผู้บริหาร", "insight": "ประวัติ การตัดสินใจ" }},
    {{ "topic": "แผนของเรา", "insight": "ตามดู ถือ งด จุดตัดขาดทุน" }}
  ],
  "note_review": "เทียบอารมณ์ตลาดอดีต vs ปัจจุบัน (ถ้าไม่มี user_notes ให้ null)"
}}"""

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
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=450,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        if not isinstance(data, dict):
            return fallback
        data["interpretation"] = str(data.get("interpretation") or fallback["interpretation"]).strip()
        data["beer_view"] = str(data.get("beer_view") or fallback["beer_view"]).strip()
        data["homework_analysis"] = _normalize_homework_analysis(
            stock,
            data.get("homework_analysis"),
            knowledge_ctx,
            user_notes,
        )
        data["analysis_status"] = "groq"
        return data
    except Exception as e:
        safe_print(f"   ⚠️ Groq Error [{stock['ticker']}]: {e}")
        fallback["analysis_error"] = str(e)
        return fallback


# ─── HTML Card ────────────────────────────────────────────────

def _news_html(news_list: list) -> str:
    if not news_list:
        return ""
    items = []
    for n in news_list:
        title = n.get("title") or "ข่าว"
        url   = n.get("url", "")
        src   = n.get("provider", "")
        date  = n.get("date", "")
        summ  = n.get("summary", "")
        title_tag = (
            f'<a href="{url}" style="color:#93c5fd;text-decoration:none;font-weight:500" target="_blank">{title}</a>'
            if url else f'<span style="color:#d1d5db;font-weight:500">{title}</span>'
        )
        summ_row = (
            f'<div style="color:#6b7280;font-size:0.81em;line-height:1.4;margin-top:2px">{summ}</div>'
            if summ else ""
        )
        meta = " · ".join(filter(None, [src, date]))
        items.append(
            f'<div style="margin-bottom:9px">{title_tag}{summ_row}'
            f'<div style="color:#4b5563;font-size:0.75em;margin-top:2px">{meta}</div></div>'
        )
    return (
        '<div style="margin-top:10px;padding-top:10px;border-top:1px solid #1e2532">'
        '<div style="color:#6b7280;font-size:0.73em;text-transform:uppercase;'
        'letter-spacing:0.08em;margin-bottom:7px">📰 News</div>'
        + "".join(items) + '</div>'
    )


def _homework_html(homework_items: list) -> str:
    if not homework_items:
        return ""
    items = "".join(
        f'<div style="border-left:2px solid #30363d;padding:7px 10px;margin-bottom:6px;'
        f'border-radius:0 5px 5px 0;background:#0d1117">'
        f'<div style="color:#f0b90b;font-size:0.76em;font-weight:bold">{item.get("topic", "")}</div>'
        f'<div style="color:#d1d5db;font-size:0.84em;line-height:1.5;margin-top:2px">{item.get("insight", "")}</div>'
        f'</div>'
        for item in homework_items
    )
    return (
        f'<div style="margin-top:10px;padding:10px;background:#111827;border-radius:8px">'
        f'<div style="color:#f0b90b;font-size:0.78em;font-weight:bold;margin-bottom:7px">'
        f'🧭 {HOMEWORK_FRAMEWORK_TITLE} (Beer วิเคราะห์ให้แล้ว)</div>'
        f'<div style="color:#8a8f98;font-size:0.78em;line-height:1.5;margin-bottom:8px">'
        f'ผลวิเคราะห์ 6 เสาหลักตามสไตล์ Beer Vanon</div>'
        f'{items}</div>'
    )


def _fmt_mktcap(cap: float) -> str:
    if cap >= 1e12:
        return f"${cap/1e12:.2f}T"
    if cap >= 1e9:
        return f"${cap/1e9:.1f}B"
    if cap > 0:
        return f"${cap/1e6:.0f}M"
    return "N/A"


def _fallback_stock_context(ticker: str, rank: int, mktcap: float = 0, hist_df=None) -> dict:
    """Return a minimal stock payload when live market data is unavailable."""
    price_now = 0.0
    pct_change = 0.0
    volume = 0

    try:
        if hist_df is not None and not hist_df.empty and "Close" in hist_df.columns:
            close = hist_df["Close"].dropna()
            if len(close) > 0:
                price_now = float(close.iloc[-1])
                price_prev = float(close.iloc[-2]) if len(close) > 1 else price_now
                pct_change = (price_now - price_prev) / price_prev * 100 if price_prev else 0.0
            if "Volume" in hist_df.columns:
                vol = hist_df["Volume"].dropna()
                if len(vol) > 1:
                    volume = int(vol.iloc[-1])
    except Exception:
        pass

    return {
        "ticker": ticker,
        "name": ticker,
        "sector": "N/A",
        "price": price_now,
        "pct_change": pct_change,
        "volume": volume,
        "market_cap": mktcap,
        "pe_ratio": None,
        "news": "ไม่มีข่าว",
        "news_list": [],
        "rank": rank,
        "tv_url": _tv_url(ticker, ""),
    }


def _safe_get_stock_context(ticker: str, rank: int, mktcap: float = 0, hist_df=None) -> dict:
    try:
        return get_stock_context(ticker, rank, mktcap=mktcap, hist_df=hist_df)
    except Exception as e:
        safe_print(f"   [{rank:3d}] {ticker:<8} -> ⚠️ stock context fallback: {e}")
        return _fallback_stock_context(ticker, rank, mktcap=mktcap, hist_df=hist_df)


def stock_card(stock: dict, analysis_data: dict, chart_cid: str, user_notes: list = None) -> str:
    arrow   = "▲" if stock["pct_change"] >= 0 else "▼"
    color   = "#16c784" if stock["pct_change"] >= 0 else "#ea3943"
    pe_str  = f" | P/E {stock['pe_ratio']:.1f}" if stock.get("pe_ratio") else ""
    cap_str = _fmt_mktcap(stock["market_cap"])

    tv_url  = stock.get("tv_url", f"https://www.tradingview.com/chart/?symbol={stock['ticker']}")
    chart_block = (
        f'<a href="{tv_url}" target="_blank" title="เปิดกราฟใน TradingView" style="display:block;margin-top:10px">'
        f'<img src="cid:{chart_cid}" '
        f'style="width:100%;border-radius:5px;display:block;cursor:pointer"></a>'
        if chart_cid else
        f'<div style="margin-top:8px"><a href="{tv_url}" target="_blank" '
        f'style="color:#6366f1;font-size:0.82em;text-decoration:none">📊 ดูกราฟบน TradingView →</a></div>'
    )

    homework_html = _homework_html(analysis_data.get("homework_analysis", []))
    news_html = _news_html(stock.get("news_list", []))
    
    analysis_text = f"**📰 ข่าวและการตีความ:**<br>{analysis_data.get('interpretation','')}<br><br>**🍺 Beer มองว่า:**<br>{analysis_data.get('beer_view','')}"
    if analysis_data.get("note_review"):
        analysis_text += f"<br><br>**🌡️ อารมณ์ตลาด (รีวิวจากโน้ตคุณ):**<br>{analysis_data.get('note_review','')}"
    
    analysis_body = analysis_text.replace(chr(10), "<br>")

    # user notes section in email
    notes_html = ""
    if user_notes:
        items = "".join(
            f'<div style="border-left:2px solid #f0b90b;padding:6px 10px;margin-bottom:6px;border-radius:0 4px 4px 0;background:#0d1117">'
            f'<div style="color:#6b7280;font-size:0.75em">📅 {n["date"]} · ${n.get("price","?")} ({("+" if n.get("pct_change",0)>0 else "")}{n.get("pct_change","?")}%)</div>'
            f'<div style="color:#d1d5db;font-size:0.88em;margin-top:3px">{n["note"]}</div>'
            f'</div>'
            for n in user_notes[:3]
        )
        notes_html = (
            f'<div style="margin-top:10px;padding:10px;background:#111827;border-radius:8px">'
            f'<div style="color:#f0b90b;font-size:0.78em;font-weight:bold;margin-bottom:7px">🌡️ อารมณ์ตลาดที่ฉันเคยจับได้</div>'
            f'{items}</div>'
        )

    return f"""
<div style="background:#1a1f2e;border-radius:12px;padding:18px;margin-bottom:14px;border-left:4px solid {color}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
    <div>
      <span style="font-size:0.72em;color:#6b7280;background:#111827;border-radius:3px;padding:1px 5px;margin-right:6px">#{stock['rank']}</span>
      <span style="font-size:1.25em;font-weight:bold;color:#ffffff">{stock['ticker']}</span>
      <span style="color:#8a8f98;margin-left:7px;font-size:0.85em">{stock['name']}</span>
    </div>
    <div style="text-align:right;flex-shrink:0;margin-left:12px">
      <div style="font-size:1.15em;color:#ffffff">${stock['price']:.2f}</div>
      <div style="color:{color};font-weight:bold;font-size:0.95em">{arrow} {abs(stock['pct_change']):.2f}%</div>
    </div>
  </div>
  <div style="color:#a0a6b3;font-size:0.80em;margin-bottom:8px">
    {stock['sector']} &nbsp;|&nbsp; Mkt Cap: <strong style="color:#d1d5db">{cap_str}</strong> &nbsp;|&nbsp; Vol: {stock['volume']:,}{pe_str}
  </div>
  {chart_block}
  {notes_html}
  {news_html}
  {homework_html}
  <div style="background:#111827;border-radius:8px;padding:12px;color:#d1d5db;font-size:0.92em;line-height:1.65;margin-top:10px">
    <div style="color:#f0b90b;font-weight:bold;margin-bottom:6px">🍺 วิเคราะห์เจาะลึก</div>
    {analysis_body}
  </div>
</div>"""


# ─── Web Archive ─────────────────────────────────────────────

def save_to_web(stocks_data: list, today: datetime.date, market_indices: dict = None, test_run: bool = False) -> str:
    """บันทึก JSON ลง docs/data/ สำหรับ GitHub Pages web archive"""
    docs_dir = Path("docs/data")
    docs_dir.mkdir(parents=True, exist_ok=True)

    date_key = today.strftime("%Y-%m-%d")
    avg_chg  = float(np.mean([s["stock"]["pct_change"] for s in stocks_data])) if stocks_data else 0
    gainers  = [s for s in stocks_data if s["stock"]["pct_change"] > 0]
    losers   = [s for s in stocks_data if s["stock"]["pct_change"] < 0]
    by_gain  = sorted(stocks_data, key=lambda s: s["stock"]["pct_change"], reverse=True)

    payload = {
        "date": date_key,
        "generated": datetime.datetime.now().isoformat(),
        "homework_framework": HOMEWORK_FRAMEWORK_TITLE,
        "homework_guide": homework_prompt_block("หุ้น US"),
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
                "rank":       s["stock"]["rank"],
                "ticker":     s["stock"]["ticker"],
                "name":       s["stock"]["name"],
                "sector":     s["stock"]["sector"],
                "price":      round(s["stock"]["price"], 2),
                "pct_change": round(s["stock"]["pct_change"], 2),
                "volume":     s["stock"]["volume"],
                "market_cap": s["stock"]["market_cap"],
                "pe_ratio":   round(s["stock"]["pe_ratio"], 1) if s["stock"].get("pe_ratio") else None,
                "tv_url":     s["stock"]["tv_url"],
                "news":       s["stock"]["news_list"],
                "analysis":   f"{s['analysis_data'].get('interpretation','')}\n\nBeer มองว่า: {s['analysis_data'].get('beer_view','')}",
                "homework_checklist": s["analysis_data"].get("homework_analysis", []),
                "chart_b64":  __import__("base64").b64encode(s["chart_bytes"]).decode() if s.get("chart_bytes") else "",
            }
            for s in stocks_data
        ],
    }
    if test_run:
        payload["test_run"] = True
        payload["test_note"] = "Generated by beer_top100_agent.py --test; limited smoke archive, not the full daily report."

    # daily file
    (docs_dir / f"{date_key}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # index file (sorted newest first)
    idx_path = docs_dir / "index.json"
    dates    = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else []
    if date_key not in dates:
        dates.insert(0, date_key)
        dates.sort(reverse=True)
    idx_path.write_text(json.dumps(dates, ensure_ascii=False), encoding="utf-8")

    url = f"{GITHUB_PAGES_URL}/?date={date_key}"
    safe_print(f"  ✅ บันทึก web archive: docs/data/{date_key}.json")
    return url


def save_history_data(stocks_data: list, period: str = "5y") -> None:
    """Save compact daily OHLCV files for the in-site stock thought history page."""
    if not stocks_data:
        return
    import yfinance as yf

    tickers = [s["stock"]["ticker"] for s in stocks_data if s.get("stock", {}).get("ticker")]
    if not tickers:
        return

    out_dir = Path("docs/history-data")
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_print(f"  ดึง history 1D {period} สำหรับ {len(tickers)} หุ้น...")

    try:
        all_hist = yf.download(tickers, period=period, group_by="ticker", threads=True, progress=False)
    except Exception as e:
        safe_print(f"  ⚠️ history download error: {e}")
        return

    saved = 0
    for ticker in tickers:
        hist = extract_ticker_history(all_hist, ticker)
        if hist is None or hist.empty:
            continue

        candles = []
        for idx, row in hist.dropna(subset=["Open", "High", "Low", "Close"]).iterrows():
            try:
                date_key = idx.strftime("%Y-%m-%d")
                candles.append([
                    date_key,
                    round(float(row["Open"]), 4),
                    round(float(row["High"]), 4),
                    round(float(row["Low"]), 4),
                    round(float(row["Close"]), 4),
                    int(row["Volume"]) if not np.isnan(row["Volume"]) else 0,
                ])
            except Exception:
                continue
        if not candles:
            continue

        payload = {
            "ticker": ticker,
            "timeframe": "1D",
            "period": period,
            "generated": datetime.datetime.now().isoformat(),
            "source": "yfinance",
            "candles": candles,
        }
        (out_dir / f"{ticker}.json").write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        saved += 1

    safe_print(f"  ✅ บันทึก history-data: {saved}/{len(tickers)} ไฟล์")


# ─── HTML Report ──────────────────────────────────────────────

def build_html_report(stocks_data: list, date_str: str, archive_url: str = "") -> str:
    cards = "".join(
        stock_card(s["stock"], s["analysis_data"], s.get("chart_cid", ""), s.get("user_notes"))
        for s in stocks_data
    )

    gainers = [s for s in stocks_data if s["stock"]["pct_change"] > 0]
    losers  = [s for s in stocks_data if s["stock"]["pct_change"] < 0]
    avg_chg = np.mean([s["stock"]["pct_change"] for s in stocks_data]) if stocks_data else 0
    sentiment_color = "#16c784" if avg_chg >= 0 else "#ea3943"
    sentiment_label = f"{'▲' if avg_chg >= 0 else '▼'} {abs(avg_chg):.2f}% avg · {len(gainers)} ขึ้น / {len(losers)} ลง"
    homework_guide = homework_email_guide_html()

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0d1117;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<div style="max-width:700px;margin:0 auto;padding:24px">

  <div style="text-align:center;padding:20px 0 14px">
    <div style="font-size:2em">🍺</div>
    <h1 style="color:#ffffff;margin:8px 0 4px;font-size:1.35em">Beer Vanon — Top 100 US Stocks</h1>
    <div style="color:#8a8f98;font-size:0.88em">{date_str} · เรียงตาม Market Cap</div>
    <div style="margin-top:10px;font-size:0.9em;color:{sentiment_color};font-weight:bold">{sentiment_label}</div>
    {f'<div style="margin-top:8px"><a href="{archive_url}" style="color:#6366f1;font-size:0.83em;text-decoration:none">📚 ดูย้อนหลังทั้งหมดบน Web Archive →</a></div>' if archive_url else ""}
  </div>

  <div style="border-top:1px solid #21262d;margin:14px 0 20px"></div>

  <div style="background:#161b22;border:1px solid #f0b90b;border-radius:10px;padding:15px;margin-bottom:20px;color:#f7d774;font-size:0.9em;line-height:1.5">
    💡 <strong>โหมดใหม่:</strong> ครั้งนี้ Beer Vanon วิเคราะห์ 6 เสาหลักของการบ้านบทที่ 34 (ธุรกิจ, ตัวเลข, ผู้บริหาร ฯลฯ) ให้ในแต่ละตัวหุ้นโดยตรง ไม่ใช่แค่หัวข้อคำถามเปล่าๆ ครับ
  </div>

  {homework_guide}

  {cards}

  <div style="border-top:1px solid #21262d;margin:20px 0 0"></div>
  <div style="text-align:center;color:#484f58;font-size:0.78em;padding:14px 0">
    Beer Vanon AI · Top 100 Market Cap · เพื่อการศึกษา ไม่ใช่คำแนะนำลงทุน
  </div>
</div>
</body>
</html>"""


def build_completion_email(date_str: str, archive_url: str, total_stocks: int, test_run: bool = False) -> str:
    label = "[TEST] Beer Top 100 homework completed" if test_run else "Beer Top 100 homework completed"
    title = "การบ้าน Beer Top 100 เสร็จแล้ว"
    note = "ระบบอัปโหลดผลลัพธ์ขึ้นเว็บ archive เรียบร้อยแล้ว"
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0d1117;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<div style="max-width:640px;margin:0 auto;padding:24px">
  <div style="background:#161b22;border:1px solid #21262d;border-radius:12px;padding:20px">
    <div style="font-size:2em;margin-bottom:6px">🍺</div>
    <div style="color:#f0b90b;font-weight:bold;font-size:1.05em;margin-bottom:8px">{title}</div>
    <div style="color:#e6edf3;font-size:0.95em;line-height:1.7;margin-bottom:10px">
      {note}<br>
      วันที่: {date_str}<br>
      จำนวนหุ้นที่ประมวลผล: {total_stocks} ตัว
    </div>
    <div style="color:#8a8f98;font-size:0.86em;line-height:1.6;margin-bottom:14px">
      อีเมลฉบับนี้เป็นเพียงรายงานสถานะ ไม่ส่งการบ้านฉบับเต็มอีกต่อไป
    </div>
    {f'<div style="margin:14px 0"><a href="{archive_url}" style="color:#6366f1;text-decoration:none;font-weight:bold">ดู archive บนเว็บ →</a></div>' if archive_url else ""}
    <div style="color:#4b5563;font-size:0.76em;margin-top:16px">{label}</div>
  </div>
</div>
</body>
</html>"""


# ─── Email ────────────────────────────────────────────────────

def send_email(html: str, subject: str, images: list = None):
    """images = list of (cid_string, jpeg_bytes) tuples"""
    user     = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not user or not password or "xxxx" in (password or ""):
        out = Path("beer_top100_report.html")
        out.write_text(html, encoding="utf-8")
        safe_print(f"  ยังไม่ได้ตั้ง GMAIL — บันทึกเป็น {out}")
        return

    # MIMEMultipart("related") keeps HTML body small — images are separate MIME parts
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"]    = user
    msg["To"]      = REPORT_TO
    msg.attach(MIMEText(html, "html", "utf-8"))

    for cid, jpeg_bytes in (images or []):
        if not jpeg_bytes:
            continue
        img_part = MIMEImage(jpeg_bytes, "jpeg")
        img_part.add_header("Content-ID", f"<{cid}>")
        img_part.add_header("Content-Disposition", "inline", filename=f"{cid}.jpg")
        msg.attach(img_part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, password)
        server.sendmail(user, REPORT_TO, msg.as_string())
    safe_print(f"  ✅ ส่ง email ถึง {REPORT_TO}")


# ─── Parallel Processing ──────────────────────────────────────

def process_single_stock(ticker, rank, mktcap, hist_df, query, posts, embeddings, embed_model, query_vector, user_notes_db):
    """Worker function สำหรับ parallel processing"""
    for attempt in range(3):
        try:
            stock     = _safe_get_stock_context(ticker, rank, mktcap=mktcap, hist_df=hist_df)
            ctx       = search_knowledge(query, posts, embeddings, embed_model, query_vector=query_vector)
            my_notes    = user_notes_db.get(ticker, [])
            
            # Groq call (JSON Mode)
            analysis_data = combined_analysis(stock, ctx, my_notes if my_notes else None)
            analysis_data["homework_analysis"] = _normalize_homework_analysis(
                stock,
                analysis_data.get("homework_analysis"),
                ctx,
                my_notes if my_notes else None,
            )
            
            chart_bytes = generate_mini_chart_b64(ticker, hist_df=hist_df)
            cid         = f"chart_{ticker.replace('-','_').replace('.','_')}"
            
            # log success
            safe_print(f"   [{rank:3d}] {ticker:<8} → ✅ {stock['pct_change']:+.1f}%")
            
            return {"stock": stock, "analysis_data": analysis_data, "chart_cid": cid, "chart_bytes": chart_bytes, "user_notes": my_notes or None}
        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower() or "429" in err:
                wait = 65 * (attempt + 1)
                safe_print(f"   [{rank:3d}] {ticker:<8} → ⏳ rate limit — รอ {wait}s...")
                time.sleep(wait)
            else:
                import traceback
                safe_print(f"   [{rank:3d}] {ticker:<8} → ❌ FATAL ERROR:\n{traceback.format_exc()}")
                return None


# ─── Main ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run in test mode (5 stocks)")
    parser.add_argument("--limit", type=int, help="Limit number of stocks to analyze")
    parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers (default 5)")
    parser.add_argument("--date", help="Archive/report date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--no-web", action="store_true", help="Do not write docs/data archive")
    parser.add_argument("--no-history", action="store_true", help="Do not write docs/history-data files")
    parser.add_argument("--no-email", action="store_true", help="Build the report without sending email")
    parser.add_argument("--out-html", help="Optional path to save the generated HTML report")
    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit must be greater than 0")
    if args.workers <= 0:
        parser.error("--workers must be greater than 0")

    if args.date:
        try:
            today = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            parser.error("--date must use YYYY-MM-DD format")
    else:
        today = datetime.date.today()

    date_str = today.strftime("%A, %d %B %Y")
    safe_print(f"\n🍺 Beer Top 100 Agent — {date_str}\n{'='*55}")
    if RUN_REQUEST_ID or RUN_REQUEST_SOURCE or RUN_REQUESTED_BY:
        safe_print(
            f"  run request: id={RUN_REQUEST_ID or '-'} source={RUN_REQUEST_SOURCE or '-'} requested_by={RUN_REQUESTED_BY or '-'}"
        )

    limit = args.limit if args.limit is not None else (5 if args.test else TOP_N)

    # 1. Knowledge base + user notes
    safe_print("\n📚 โหลด knowledge base...")
    posts, embeddings, embed_model = load_knowledge()
    safe_print(f"   {len(posts)} โพสต์ | embeddings: {'✅' if embeddings is not None else '⚠️'}")
    
    query = "trend momentum หุ้นใหญ่ market cap SQ วินัย"
    query_vector = None
    if embed_model is not None:
        safe_print("   Pre-encoding search query...")
        query_vector = embed_model.encode([query], normalize_embeddings=True)[0].astype("float32")

    user_notes_db = load_user_notes()
    notes_count   = sum(len(v) for v in user_notes_db.values())
    safe_print(f"   โน้ตของคุณ: {notes_count} รายการ ({len(user_notes_db)} หุ้น)")

    # 2. Market cap ranking
    safe_print("\n📊 จัดลำดับ Market Cap...")
    mktcaps = fetch_market_caps(US_UNIVERSE)
    ranked  = sorted(US_UNIVERSE, key=lambda t: mktcaps.get(t, 0), reverse=True)
    top_stocks = [t for t in ranked if mktcaps.get(t, 0) > 0][:limit]
    safe_print(f"   วิเคราะห์ {len(top_stocks)} หุ้น | อันดับ 1: {top_stocks[0]} ({_fmt_mktcap(mktcaps.get(top_stocks[0],0))})")

    # 2.1 Batch fetch history
    import yfinance as yf
    safe_print(f"   ดึงข้อมูลราคา {len(top_stocks)} หุ้น (batch)...")
    try:
        all_hist = yf.download(top_stocks, period="3mo", group_by='ticker', threads=True, progress=False)
    except Exception as e:
        safe_print(f"   ⚠️ Batch fetch error: {e}")
        all_hist = None

    # 3. วิเคราะห์หุ้นแบบ Parallel
    stocks_data = []
    safe_print(f"\n🔍 วิเคราะห์ {len(top_stocks)} หุ้น (parallel workers={args.workers})...")
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        for i, ticker in enumerate(top_stocks, 1):
            hist_df = extract_ticker_history(all_hist, ticker)
            
            futures.append(executor.submit(
                process_single_stock, 
                ticker, i, mktcaps.get(ticker, 0), hist_df, query, posts, embeddings, embed_model, query_vector, user_notes_db
            ))
            # ใส่ delay เล็กน้อยตอนเริ่ม submit เพื่อกระจายโหลด Groq
            time.sleep(0.5)
            
        for f in futures:
            res = f.result()
            if res:
                stocks_data.append(res)

    # 4. บันทึก web archive
    if not stocks_data:
        safe_print("\n❌ ไม่มีข้อมูลหุ้นที่วิเคราะห์ได้สำเร็จ")
        return

    archive_url = ""
    if args.no_web:
        safe_print(f"\n🌐 ข้ามการบันทึก web archive (--no-web)")
    else:
        # 4a. ดึงดัชนีตลาด
        safe_print(f"\n📈 ดึงดัชนีตลาด (DJI/S&P/NASDAQ)...")
        market_indices = fetch_market_indices()
        idx_status = " | ".join(f"{k.upper()}:✅" if k in market_indices else f"{k.upper()}:❌" for k in ["dji","spx","ixic"])
        safe_print(f"   {idx_status}")

        safe_print(f"\n🌐 บันทึก web archive...")
        archive_url = save_to_web(stocks_data, today, market_indices, test_run=args.test)
        if not args.no_history:
            save_history_data(stocks_data)

    # 5. สร้างและส่ง email
    safe_print(f"\n📄 สร้างรายงาน ({len(stocks_data)} หุ้น)...")
    homework_complete = sum(1 for s in stocks_data if len(s["analysis_data"].get("homework_analysis", [])) == 6)
    safe_print(f"   homework completeness: {homework_complete}/{len(stocks_data)}")
    if homework_complete != len(stocks_data):
        safe_print(f"   ⚠️ Homework ไม่ครบทุกหุ้น: ขาด {len(stocks_data) - homework_complete} ตัว")
    report_html = build_html_report(stocks_data, date_str, archive_url)
    email_html   = build_completion_email(date_str, archive_url, len(stocks_data), test_run=args.test)
    subject = f"🍺 Beer Top 100 เสร็จแล้ว — {today.strftime('%d/%m/%Y')} ({len(stocks_data)} หุ้น)"
    if args.test:
        subject = f"[TEST] {subject}"

    if args.out_html:
        Path(args.out_html).write_text(report_html, encoding="utf-8")
        safe_print(f"  ✅ บันทึก HTML preview: {args.out_html}")

    if args.no_email:
        safe_print("📧 ข้ามการส่ง email (--no-email)")
    else:
        safe_print("📧 ส่ง email แจ้งเตือน...")
        send_email(email_html, subject, None)

    safe_print(f"\n✅ เสร็จสิ้น! วิเคราะห์ {len(stocks_data)}/{len(top_stocks)} หุ้น")


if __name__ == "__main__":
    main()
