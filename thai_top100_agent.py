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
from dotenv import load_dotenv
from groq import Groq
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
last_groq_call = 0.0

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

# ─── Config ───────────────────────────────────────────────────
KNOWLEDGE_JSON  = "beervanon_cleaned.json"
DATA_DIR        = Path("docs/thai-data")
EMBEDDINGS_FILE = "embeddings.npz"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL      = "llama-3.1-8b-instant"   # 6000 TPM limit
REPORT_TO        = os.getenv("GMAIL_USER", "patiphan.injob@gmail.com")
TOP_N            = 100
CALL_DELAY       = 10.0   # 10 วินาที เพื่อให้รอดจาก 6000 TPM (Token Per Minute)
GITHUB_PAGES_URL = "https://patiphaninjob-lang.github.io/beer-vanon-agents"
RUN_REQUEST_ID   = os.getenv("RUN_REQUEST_ID", "").strip()
RUN_REQUEST_SOURCE = os.getenv("RUN_REQUEST_SOURCE", "").strip()
RUN_REQUESTED_BY = os.getenv("RUN_REQUESTED_BY", "").strip()

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
    cache_file = Path("thai_metadata_cache.json")
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
    # หมายเหตุ: หุ้นไทยอาจใช้ notes เดียวกันหรือแยกก็น่าจะดี แต่ตอนนี้ใช้จาก docs/notes/notes.json ไปก่อน
    path = Path("docs/notes/notes.json")
    if not path.exists():
        return {}
    try:
        notes = json.loads(path.read_text(encoding="utf-8"))
        return notes if isinstance(notes, dict) else {}
    except Exception:
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
    client    = Groq(api_key=os.getenv("GROQ_API_KEY"))
    direction = "ขึ้น" if stock["pct_change"] > 0 else "ลง"
    fallback  = {
        "interpretation": f"วิเคราะห์ {stock['ticker']} กลุ่ม {stock['sector']} วันนี้ {direction} {abs(stock['pct_change']):.1f}%",
        "beer_view": "ใช้ framework สำรองเนื่องจาก API ขัดข้อง",
        "homework_analysis": _fallback_homework_analysis(stock, knowledge_ctx, user_notes),
        "note_review": None,
        "analysis_status": "fallback",
    }

    notes_ctx = ""
    if user_notes:
        lines = [f"- {n['date']}: {n['note']}" for n in user_notes[:3]]
        notes_ctx = "\n\n🌡️ อารมณ์ตลาดจากโน้ต:\n" + "\n".join(lines)

    prompt = f"""วิเคราะห์หุ้นไทย {stock['ticker']} ({stock['name']})
ราคา: {stock['price']:.2f} THB ({direction} {abs(stock['pct_change']):.1f}%) | Sector: {stock['sector']}
Mkt Cap Rank: #{stock['rank']} | Vol: {stock['volume']:,}

หลักการ Beer Vanon:
{BEER_DNA[:250]}

ข่าว/ความรู้:
{stock['news'][:400]}
{knowledge_ctx[:300]}{notes_ctx}

ให้ตอบเป็น JSON (ภาษาไทย) โครงสร้าง:
{{
  "interpretation": "สรุปรายละเอียดข่าว (Detail, Sentiment, Implication) บรรยายยาว",
  "beer_view": "ความเห็นสไตล์ Beer (SQ และจุด Circuit Breaker)",
  "homework_analysis": [
    {{ "topic": "ธุรกิจ", "insight": "..." }},
    {{ "topic": "ตัวเลข", "insight": "..." }},
    {{ "topic": "การสื่อสาร", "insight": "..." }},
    {{ "topic": "คู่แข่ง", "insight": "..." }},
    {{ "topic": "ผู้บริหาร", "insight": "..." }},
    {{ "topic": "แผนของเรา", "insight": "..." }}
  ],
  "note_review": "เทียบโน้ต (ถ้ามี)"
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
        data["interpretation"] = _flatten_content(data.get("interpretation"))
        data["beer_view"] = _flatten_content(data.get("beer_view"))
        data["homework_analysis"] = _normalize_homework_analysis(stock, data.get("homework_analysis"), knowledge_ctx, user_notes)
        return data
    except Exception as e:
        safe_print(f"   ⚠️ Groq Error [{stock['ticker']}]: {e}")
        return fallback


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
        f'<div style="border-left:2px solid #30363d;padding:5px 10px;margin-bottom:5px;background:#0d1117">'
        f'<div style="color:#f0b90b;font-size:0.75em;font-weight:bold">{item["topic"]}</div>'
        f'<div style="color:#d1d5db;font-size:0.82em">{item["insight"]}</div></div>'
        for item in analysis_data.get("homework_analysis", [])
    )

    return f"""
<div style="background:#1a1f2e;border-radius:12px;padding:15px;margin-bottom:12px;border-left:4px solid {color}">
  <div style="color:#ffffff;font-size:1.1em;font-weight:bold">#{stock['rank']} {stock['ticker']} <span style="font-size:0.75em;font-weight:normal;color:#8a8f98">{stock['name']}</span></div>
  <div style="color:{color};font-weight:bold">${stock['price']:.2f} ({arrow} {abs(stock['pct_change']):.2f}%)</div>
  <div style="color:#a0a6b3;font-size:0.78em;margin:5px 0">{stock['sector']} | Mkt Cap: {cap_str}</div>
  {chart_block}
  <div style="margin-top:10px;padding:10px;background:#111827;border-radius:8px">
    <div style="color:#f0b90b;font-size:0.8em;font-weight:bold;margin-bottom:5px">🧭 {HOMEWORK_FRAMEWORK_TITLE}</div>
    {hw_items}
  </div>
  <div style="margin-top:10px;padding:10px;background:#111827;border-radius:8px;color:#d1d5db;font-size:0.9em">
    <div style="color:#f0b90b;font-weight:bold">🍺 วิเคราะห์</div>
    {analysis_data.get('interpretation','')}<br><br>
    <strong>Beer มองว่า:</strong> {analysis_data.get('beer_view','')}
  </div>
</div>"""


def save_to_web(stocks_data: list, today: datetime.date, market_indices: dict = None) -> str:
    docs_dir = Path("docs/thai-data")
    docs_dir.mkdir(parents=True, exist_ok=True)
    date_key = today.strftime("%Y-%m-%d")

    payload = {
        "date": date_key,
        "generated": datetime.datetime.now().isoformat(),
        "homework_framework": HOMEWORK_FRAMEWORK_TITLE,
        "homework_guide": homework_prompt_block("หุ้นไทย"),
        "market_indices": market_indices or {},
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
                "analysis": f"{s['analysis_data'].get('interpretation','')}\n\nBeer มองว่า: {s['analysis_data'].get('beer_view','')}",
                "homework_checklist": s["analysis_data"].get("homework_analysis", []),
                "chart_b64": __import__("base64").b64encode(s["chart_bytes"]).decode() if s.get("chart_bytes") else "",
            }
            for s in stocks_data
        ],
    }
    (docs_dir / f"{date_key}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    
    idx_path = docs_dir / "index.json"
    dates = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else []
    if date_key not in dates:
        dates.insert(0, date_key)
        dates.sort(reverse=True)
    idx_path.write_text(json.dumps(dates, ensure_ascii=False), encoding="utf-8")

    return f"{GITHUB_PAGES_URL}/thai.html?date={date_key}"


def save_history_data(stocks_data: list) -> None:
    out_dir = Path("docs/thai-history-data")
    out_dir.mkdir(parents=True, exist_ok=True)
    import yfinance as yf
    tickers = [s["stock"]["ticker"] for s in stocks_data]
    all_hist = yf.download(tickers, period="5y", group_by="ticker", threads=True, progress=False)
    for ticker in tickers:
        hist = extract_ticker_history(all_hist, ticker)
        if hist is None or hist.empty: continue
        candles = [[idx.strftime("%Y-%m-%d"), round(row["Open"],4), round(row["High"],4), round(row["Low"],4), round(row["Close"],4), int(row["Volume"])]
                   for idx, row in hist.dropna(subset=["Close"]).iterrows()]
        payload = {"ticker": ticker, "timeframe": "1D", "period": "5y", "candles": candles}
        (out_dir / f"{ticker}.json").write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    today = datetime.date.today()
    
    # 0. Safety Net Check: ถ้าเป็นระบบ Auto (schedule) และวันนี้ทำไปแล้ว (กดมือ) ให้ข้าม
    is_scheduled = os.getenv("GITHUB_EVENT_NAME") == "schedule"
    today_file_str = today.strftime("%Y-%m-%d")
    report_path = DATA_DIR / f"{today_file_str}.json"

    if is_scheduled and report_path.exists():
        safe_print(f"⚠️ [Safety Net] ตรวจพบรายงานของวันนี้ ({today_file_str}) แล้ว (คุณน่าจะกดรันเองไปแล้ว)")
        safe_print("⏭️ ข้ามการรันอัตโนมัติเพื่อไม่ให้ส่งเมลซ้ำซ้อน")
        return

    date_str = today.strftime("%A, %d %B %Y")
    safe_print(f"\n🍺 Beer Thai Top 100 Agent — {date_str}\n{'='*55}")
    if RUN_REQUEST_ID or RUN_REQUEST_SOURCE or RUN_REQUESTED_BY:
        safe_print(
            f"  run request: id={RUN_REQUEST_ID or '-'} source={RUN_REQUEST_SOURCE or '-'} requested_by={RUN_REQUESTED_BY or '-'}"
        )

    posts, embeddings, embed_model = load_knowledge()
    user_notes_db = load_user_notes()
    
    mktcaps = fetch_market_caps(TH_UNIVERSE)
    top_stocks = sorted([t for t in TH_UNIVERSE if mktcaps.get(t, 0) > 0], key=lambda t: mktcaps[t], reverse=True)
    limit = args.limit or (5 if args.test else 100)
    top_stocks = top_stocks[:limit]

    import yfinance as yf
    all_hist = yf.download(top_stocks, period="3mo", group_by='ticker', threads=True, progress=False)

    stocks_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_single_stock, t, i+1, mktcaps[t], extract_ticker_history(all_hist, t), "SET100 หุ้นไทย", posts, embeddings, embed_model, None, user_notes_db) 
                   for i, t in enumerate(top_stocks)]
        for f in futures:
            res = f.result()
            if res: stocks_data.append(res)

    if stocks_data:
        market_indices = fetch_market_indices()
        archive_url = save_to_web(stocks_data, today, market_indices)
        save_history_data(stocks_data)
        
        # Simple Notify Email
        subject = f"🍺 Beer Thai Top 100 เสร็จแล้ว — {today.strftime('%d/%m/%Y')}"
        email_body = f"การบ้านหุ้นไทย SET100 เสร็จแล้ว {len(stocks_data)} ตัว\nดูผลลัพธ์: {archive_url}"
        send_email(email_body, subject, None)
        safe_print(f"\n✅ เสร็จสิ้น! ดูผลลัพธ์ที่: {archive_url}")

def process_single_stock(ticker, rank, mktcap, hist_df, query, posts, embeddings, embed_model, q_vec, notes_db):
    try:
        stock = _safe_get_stock_context(ticker, rank, mktcap, hist_df)
        ctx = search_knowledge(query, posts, embeddings, embed_model)
        analysis = combined_analysis(stock, ctx, notes_db.get(ticker))
        chart = generate_mini_chart_b64(ticker, hist_df)
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
