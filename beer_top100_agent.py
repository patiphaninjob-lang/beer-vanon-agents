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

# ─── Global Lock for Output ──────────────────────────────────
print_lock = threading.Lock()

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
CALL_DELAY       = 1.2   # วินาที ระหว่าง Groq call (ป้องกัน rate limit)
GITHUB_PAGES_URL = "https://patiphaninjob-lang.github.io/beer-vanon-agents"

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
        chunk = p.get("content","")[:400]
        if total + len(chunk) > 1500:
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n\n---\n\n".join(parts) or "ไม่พบข้อมูล"


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


def get_stock_context(ticker: str, rank: int, hist_df=None) -> dict:
    import yfinance as yf
    tk   = yf.Ticker(ticker)
    info = tk.info or {}
    
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

    mktcap = info.get("marketCap", 0)
    return {
        "ticker":     ticker,
        "name":       info.get("longName") or info.get("shortName") or ticker,
        "sector":     info.get("sector", "N/A"),
        "price":      price_now,
        "pct_change": pct_change,
        "volume":     volume,
        "market_cap": mktcap,
        "pe_ratio":   info.get("trailingPE"),
        "news":       news_text,
        "news_list":  news_list,
        "rank":       rank,
        "tv_url":     _tv_url(ticker, info.get("exchange", "")),
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
    path = Path("docs/notes/notes.json")
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ─── Combined Analysis ────────────────────────────────────────

def combined_analysis(stock: dict, knowledge_ctx: str, user_notes: list = None) -> str:
    """ONE Groq call: ข่าวคืออะไร + Beer มองว่า (ประหยัด token สำหรับ 100 หุ้น)"""
    client    = Groq(api_key=os.getenv("GROQ_API_KEY"))
    direction = "ขึ้น" if stock["pct_change"] > 0 else "ลง"

    notes_ctx = ""
    if user_notes:
        lines = [
            f"- {n['date']} (ราคา ${n.get('price','?')}, {'+' if n.get('pct_change',0)>0 else ''}{n.get('pct_change','?')}%): {n['note']}"
            for n in user_notes[:3]
        ]
        notes_ctx = "\n\n🌡️ อารมณ์ตลาดที่นักลงทุนเคยจับได้:\n" + "\n".join(lines)

    note_review_section = """
**🌡️ อารมณ์ตลาดเมื่อก่อน vs วันนี้:**
ตอนนั้นจับอารมณ์ว่าอะไร (กลัว/โลภ/ไม่แน่ใจ) — ราคาที่เกิดขึ้นจริงยืนยันหรือหักล้างการอ่านอารมณ์ครั้งนั้น อารมณ์ตลาดตอนนี้เปลี่ยนไปอย่างไร""" if user_notes else ""

    prompt = f"""คุณคือ Beer Vanon วิเคราะห์หุ้น {stock['ticker']} ({stock['name']})

หลักการ Beer Vanon (อ้างอิง):
{BEER_DNA[:2000]}

กรอบการบ้านที่ต้องฝังในทุกบทวิเคราะห์:
{homework_prompt_block("หุ้น US")}

เนื้อหาเพิ่มเติม:
{knowledge_ctx}{notes_ctx}

ข้อมูลหุ้น:
- ราคา: ${stock['price']:.2f} ({direction} {abs(stock['pct_change']):.1f}%) | Sector: {stock['sector']}
- Market Cap Rank: #{stock['rank']} ในตลาด | Volume: {stock['volume']:,}
- P/E: {stock['pe_ratio'] or 'N/A'}

ข่าวล่าสุด:
{stock['news']}

ตอบ {'4' if user_notes else '3'} ส่วน (รวมไม่เกิน {'280' if user_notes else '230'} คำ ภาษาไทย กระชับ ตรงประเด็น):

**📰 ข่าวคืออะไร + ตลาดจะตีความอย่างไร:**
อธิบายว่าข่าวพูดถึงอะไร เกิดอะไรขึ้น แล้วนักลงทุนจะมองบวก/ลบ/กลาง เพราะอะไร

**🍺 Beer มองว่า:**
SQ ของหุ้นนี้ น่าสนใจหรือผ่าน Circuit Breaker ที่ควรตั้ง พูดตรงๆ

**🧭 การบ้านบทที่ 34 ที่ต้องเติม:**
จากธุรกิจ/ตัวเลข/การสื่อสาร/คู่แข่ง/ผู้บริหาร/แผนของเรา เลือก 2-3 เรื่องที่ต้องไปตรวจต่อ ห้ามเดาข้อมูลที่ยังไม่มี
{note_review_section}"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=520 if not user_notes else 650,
    )
    return resp.choices[0].message.content.strip()


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
        f'<div style="color:#d1d5db;font-size:0.84em;line-height:1.5;margin-top:2px">{item.get("prompt", "")}</div>'
        f'</div>'
        for item in homework_items
    )
    return (
        f'<div style="margin-top:10px;padding:10px;background:#111827;border-radius:8px">'
        f'<div style="color:#f0b90b;font-size:0.78em;font-weight:bold;margin-bottom:7px">'
        f'🧭 {HOMEWORK_FRAMEWORK_TITLE}</div>'
        f'<div style="color:#8a8f98;font-size:0.78em;line-height:1.5;margin-bottom:8px">'
        f'การบ้านที่ต้องตรวจต่อ ไม่ใช่คำตอบสำเร็จรูป</div>'
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


def stock_card(stock: dict, analysis: str, chart_cid: str, user_notes: list = None) -> str:
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

    homework_items = stock.get("homework_checklist") or build_stock_homework_checklist(stock)
    homework_html = _homework_html(homework_items)
    news_html = _news_html(stock.get("news_list", []))
    analysis_body = analysis.replace(chr(10), "<br>")

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
    <div style="color:#f0b90b;font-weight:bold;margin-bottom:6px">🍺 วิเคราะห์</div>
    {analysis_body}
  </div>
</div>"""


# ─── Web Archive ─────────────────────────────────────────────

def save_to_web(stocks_data: list, today: datetime.date, market_indices: dict = None) -> str:
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
                "analysis":   s["analysis"],
                "homework_checklist": s["stock"].get("homework_checklist") or build_stock_homework_checklist(s["stock"]),
                "chart_b64":  __import__("base64").b64encode(s["chart_bytes"]).decode() if s.get("chart_bytes") else "",
            }
            for s in stocks_data
        ],
    }

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


# ─── HTML Report ──────────────────────────────────────────────

def build_html_report(stocks_data: list, date_str: str, archive_url: str = "") -> str:
    cards = "".join(
        stock_card(s["stock"], s["analysis"], s.get("chart_cid", ""), s.get("user_notes"))
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

  {homework_guide}

  {cards}

  <div style="border-top:1px solid #21262d;margin:20px 0 0"></div>
  <div style="text-align:center;color:#484f58;font-size:0.78em;padding:14px 0">
    Beer Vanon AI · Top 100 Market Cap · เพื่อการศึกษา ไม่ใช่คำแนะนำลงทุน
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

def process_single_stock(ticker, rank, hist_df, query, posts, embeddings, embed_model, query_vector, user_notes_db):
    """Worker function สำหรับ parallel processing"""
    for attempt in range(3):
        try:
            stock     = get_stock_context(ticker, rank, hist_df=hist_df)
            ctx       = search_knowledge(query, posts, embeddings, embed_model, query_vector=query_vector)
            my_notes    = user_notes_db.get(ticker, [])
            
            # Groq call
            analysis    = combined_analysis(stock, ctx, my_notes if my_notes else None)
            
            chart_bytes = generate_mini_chart_b64(ticker, hist_df=hist_df)
            cid         = f"chart_{ticker.replace('-','_').replace('.','_')}"
            
            # log success
            safe_print(f"   [{rank:3d}] {ticker:<8} → ✅ {stock['pct_change']:+.1f}%")
            
            return {"stock": stock, "analysis": analysis, "chart_cid": cid, "chart_bytes": chart_bytes, "user_notes": my_notes or None}
        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower() or "429" in err:
                wait = 65 * (attempt + 1)
                safe_print(f"   [{rank:3d}] {ticker:<8} → ⏳ rate limit — รอ {wait}s...")
                time.sleep(wait)
            else:
                safe_print(f"   [{rank:3d}] {ticker:<8} → ❌ {err[:100]}")
                return None


# ─── Main ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run in test mode (5 stocks)")
    parser.add_argument("--limit", type=int, help="Limit number of stocks to analyze")
    parser.add_argument("--workers", type=int, default=2, help="Number of parallel workers (default 2)")
    args = parser.parse_args()

    today    = datetime.date.today()
    date_str = today.strftime("%A, %d %B %Y")
    safe_print(f"\n🍺 Beer Top 100 Agent — {date_str}\n{'='*55}")

    limit = 5 if args.test else (args.limit or TOP_N)

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
            hist_df = None
            if all_hist is not None:
                if len(top_stocks) > 1:
                    hist_df = all_hist[ticker]
                else:
                    hist_df = all_hist
            
            futures.append(executor.submit(
                process_single_stock, 
                ticker, i, hist_df, query, posts, embeddings, embed_model, query_vector, user_notes_db
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

    # 4a. ดึงดัชนีตลาด
    safe_print(f"\n📈 ดึงดัชนีตลาด (DJI/S&P/NASDAQ)...")
    market_indices = fetch_market_indices()
    idx_status = " | ".join(f"{k.upper()}:✅" if k in market_indices else f"{k.upper()}:❌" for k in ["dji","spx","ixic"])
    safe_print(f"   {idx_status}")

    safe_print(f"\n🌐 บันทึก web archive...")
    archive_url = save_to_web(stocks_data, today, market_indices)

    # 5. สร้างและส่ง email
    safe_print(f"\n📄 สร้างรายงาน ({len(stocks_data)} หุ้น)...")
    html    = build_html_report(stocks_data, date_str, archive_url)
    images  = [(s["chart_cid"], s["chart_bytes"]) for s in stocks_data if s.get("chart_bytes")]
    subject = f"🍺 Beer Top 100 Market Cap — {today.strftime('%d/%m/%Y')} ({len(stocks_data)} หุ้น)"
    if args.test:
        subject = f"[TEST] {subject}"

    safe_print("📧 ส่ง email...")
    send_email(html, subject, images)

    safe_print(f"\n✅ เสร็จสิ้น! วิเคราะห์ {len(stocks_data)}/{len(top_stocks)} หุ้น")


if __name__ == "__main__":
    main()
