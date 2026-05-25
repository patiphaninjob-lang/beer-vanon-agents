"""
Beer Vanon US Stock Agent
รันทุกวันหลังตลาด US ปิด → วิเคราะห์ top movers ตาม mindset Beer Vanon → ส่ง email

Setup:
1. เพิ่มใน .env:
   GMAIL_USER=patiphan.injob@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

2. รัน: py beer_us_agent.py
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import json
import smtplib
import datetime
import numpy as np
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from groq import Groq
from beer_dna import BEER_DNA
from beer_homework_framework import (
    HOMEWORK_FRAMEWORK_TITLE,
    HOMEWORK_SEARCH_QUERY,
    build_stock_homework_checklist,
    homework_email_guide_html,
    homework_prompt_block,
)

load_dotenv()

# ─── Config ───────────────────────────────────────────────────
KNOWLEDGE_JSON  = "beervanon_cleaned.json"
EMBEDDINGS_FILE = "embeddings.npz"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL      = "llama-3.3-70b-versatile"
TOP_N           = 5   # gainers + losers แต่ละ N ตัว
REPORT_TO       = os.getenv("GMAIL_USER", "patiphan.injob@gmail.com")

# S&P 500 stocks ที่มี volume สูง — ใช้ดึง movers
SP500_WATCHLIST = [
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AMD","INTC","CRM",
    "ORCL","NFLX","ADBE","QCOM","TXN","MU","AMAT","LRCX","KLAC","MRVL",
    "JPM","BAC","WFC","GS","MS","V","MA","AXP","BRK-B","C",
    "JNJ","UNH","PFE","ABBV","MRK","LLY","BMY","AMGN","GILD","CVS",
    "WMT","COST","HD","MCD","NKE","SBUX","TGT","LOW","AMZN","DG",
    "XOM","CVX","COP","SLB","MPC","VLO","OXY","HAL","BKR","PSX",
    "CAT","DE","GE","HON","BA","LMT","RTX","NOC","GD","MMM",
    "DIS","CMCSA","NFLX","PARA","WBD","EA","TTWO","ATVI",
    "T","VZ","TMUS","AMT","CCI","EQIX",
    "SPY","QQQ","IWM",
]


# ─── Knowledge Base ───────────────────────────────────────────

def load_knowledge():
    """โหลด posts + embeddings"""
    path = Path(KNOWLEDGE_JSON)
    if not path.exists():
        print(f"ไม่พบ {KNOWLEDGE_JSON}")
        return [], None, None

    posts = json.loads(path.read_text(encoding="utf-8"))

    emb_path = Path(EMBEDDINGS_FILE)
    if not emb_path.exists():
        print("ไม่พบ embeddings.npz — ใช้ keyword search แทน")
        return posts, None, None

    from sentence_transformers import SentenceTransformer
    model      = SentenceTransformer(EMBED_MODEL)
    embeddings = np.load(emb_path)["embeddings"].astype("float32")
    return posts, embeddings, model


def search_knowledge(query: str, posts: list, embeddings, embed_model, top_k=4) -> str:
    """ค้นหา posts ที่เกี่ยวข้องกับ query"""
    if embed_model is not None and embeddings is not None:
        q_vec = embed_model.encode([query], normalize_embeddings=True)[0].astype("float32")
        scores = embeddings @ q_vec
        top_idx = np.argsort(scores)[::-1][:top_k]
        relevant = [posts[i] for i in top_idx]
    else:
        # keyword fallback
        words = set(query.lower().split())
        scored = []
        for p in posts:
            text = p.get("content", "").lower()
            score = sum(1 for w in words if w in text and len(w) > 2)
            if score > 0:
                scored.append((score, p))
        scored.sort(reverse=True)
        relevant = [p for _, p in scored[:top_k]]

    parts = []
    total = 0
    for p in relevant:
        chunk = p.get("content", "")[:600]
        if total + len(chunk) > 2500:
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n\n---\n\n".join(parts) if parts else "ไม่พบข้อมูลที่เกี่ยวข้อง"


# ─── Stock Data ───────────────────────────────────────────────

def fetch_sp500_movers(top_n: int = TOP_N) -> dict:
    """ดึง top gainers + losers จาก watchlist"""
    import yfinance as yf

    print(f"กำลังดึงข้อมูลหุ้น {len(SP500_WATCHLIST)} ตัว...")
    raw = yf.download(
        SP500_WATCHLIST,
        period="2d",
        auto_adjust=True,
        progress=False,
        threads=True,
    )

    closes = raw["Close"]
    pct    = closes.pct_change().iloc[-1].dropna() * 100

    gainers = pct.nlargest(top_n)
    losers  = pct.nsmallest(top_n)

    print(f"  Gainers: {list(gainers.index)}")
    print(f"  Losers:  {list(losers.index)}")
    return {"gainers": gainers, "losers": losers, "all_pct": pct}


def get_stock_context(ticker: str) -> dict:
    """ดึงรายละเอียดหุ้นแต่ละตัว"""
    import yfinance as yf

    tk   = yf.Ticker(ticker)
    info = tk.info or {}

    hist = tk.history(period="5d")
    price_now  = float(hist["Close"].iloc[-1]) if not hist.empty else 0
    price_prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price_now
    pct_change = (price_now - price_prev) / price_prev * 100 if price_prev else 0
    volume     = int(hist["Volume"].iloc[-1]) if not hist.empty else 0

    # ข่าวล่าสุด (max 3 ชิ้น)
    try:
        raw_news  = tk.news[:3] if tk.news else []
        news_list = [_parse_news(n) for n in raw_news]
        news_text = "\n".join(
            f"- [{n['provider']}] {n['title']}" + (f"\n  {n['summary']}" if n['summary'] else "")
            for n in news_list
        ) if news_list else "ไม่มีข่าวล่าสุด"
    except Exception:
        news_list = []
        news_text = "ไม่มีข่าวล่าสุด"

    exchange_code = info.get("exchange", "")
    return {
        "ticker":      ticker,
        "name":        info.get("longName", ticker),
        "sector":      info.get("sector", "N/A"),
        "price":       price_now,
        "pct_change":  pct_change,
        "volume":      volume,
        "market_cap":  info.get("marketCap", 0),
        "pe_ratio":    info.get("trailingPE", None),
        "news":        news_text,
        "news_list":   news_list,
        "tv_url":      get_tradingview_url(ticker, exchange_code),
    }


# ─── News Helper ─────────────────────────────────────────────

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


def _news_section_html(news_list: list) -> str:
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
        summary_row = (
            f'<div style="color:#6b7280;font-size:0.82em;line-height:1.4;margin-top:3px">{summ}</div>'
            if summ else ""
        )
        meta = " · ".join(filter(None, [src, date]))
        items.append(
            f'<div style="margin-bottom:10px">'
            f'{title_tag}{summary_row}'
            f'<div style="color:#4b5563;font-size:0.76em;margin-top:3px">{meta}</div>'
            f'</div>'
        )
    return (
        '<div style="margin-top:12px;padding-top:12px;border-top:1px solid #1e2532">'
        '<div style="color:#6b7280;font-size:0.75em;text-transform:uppercase;'
        'letter-spacing:0.08em;margin-bottom:8px">📰 News</div>'
        + "".join(items) + '</div>'
    )


def analyze_news_sentiment(news_list: list, ticker: str) -> str:
    """Groq อธิบายว่าข่าวแต่ละชิ้นคืออะไร + ตลาดจะตีความอย่างไร"""
    if not news_list:
        return ""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    news_block = "\n\n".join(
        f"ข่าว {i+1}: {n['title']}" + (f"\n{n['summary']}" if n.get("summary") else "")
        for i, n in enumerate(news_list)
    )
    prompt = f"""วิเคราะห์ข่าวของหุ้น {ticker} ต่อไปนี้:

{news_block}

ตอบ 2 ส่วน เป็นภาษาไทย ให้รายละเอียดเพียงพอที่จะเข้าใจว่าเกิดอะไรขึ้นจริงๆ:

**เนื้อข่าวคืออะไร:**
อธิบายแต่ละข่าวว่าพูดถึงอะไร เกิดเหตุการณ์อะไร มีตัวเลข/ข้อมูลสำคัญอะไรบ้าง (2-3 ประโยคต่อข่าว)

**ตลาดจะตีความอย่างไร:**
นักลงทุนส่วนใหญ่จะมองข่าวชุดนี้เป็น บวก/ลบ/เป็นกลาง? เพราะอะไร? อารมณ์ตลาดน่าจะเป็นอย่างไร — กลัว / โลภ / สับสน / รอดูท่าที? คาดการณ์ราคาระยะสั้นจะ react อย่างไร?"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()


def _sentiment_section_html(sentiment: str) -> str:
    if not sentiment:
        return ""
    body = sentiment.replace(chr(10), "<br>")
    return (
        '<div style="background:#12192a;border-radius:8px;padding:14px;margin-top:12px;'
        'border-left:3px solid #6366f1">'
        '<div style="color:#a5b4fc;font-size:0.78em;text-transform:uppercase;'
        'letter-spacing:0.08em;margin-bottom:8px;font-weight:600">🔍 วิเคราะห์ข่าว + อารมณ์ตลาด</div>'
        f'<div style="color:#c4c9d4;font-size:0.9em;line-height:1.7">{body}</div>'
        '</div>'
    )


# ─── Chart Generator ─────────────────────────────────────────

def _homework_section_html(stock: dict) -> str:
    items = build_stock_homework_checklist(stock)
    body = "".join(
        f'<div style="border-left:2px solid #30363d;padding:7px 10px;margin-bottom:6px;'
        f'border-radius:0 5px 5px 0;background:#0d1117">'
        f'<div style="color:#f0b90b;font-size:0.76em;font-weight:bold">{item["topic"]}</div>'
        f'<div style="color:#d1d5db;font-size:0.84em;line-height:1.5;margin-top:2px">{item["prompt"]}</div>'
        f'</div>'
        for item in items
    )
    return (
        '<div style="background:#111827;border-radius:8px;padding:12px;margin-top:12px">'
        f'<div style="color:#f0b90b;font-size:0.78em;font-weight:bold;margin-bottom:7px">🧭 {HOMEWORK_FRAMEWORK_TITLE}</div>'
        '<div style="color:#8a8f98;font-size:0.78em;line-height:1.5;margin-bottom:8px">'
        'โจทย์การบ้านที่ต้องตรวจต่อจากหุ้นตัวนี้</div>'
        f'{body}</div>'
    )


_TV_EXCHANGE = {
    "NMS": "NASDAQ", "NGM": "NASDAQ", "NCM": "NASDAQ",
    "NYQ": "NYSE",   "PCX": "NYSE",   "BTS": "NYSE",
    "ASE": "AMEX",
}

def get_tradingview_url(ticker: str, exchange_code: str = "") -> str:
    ex = _TV_EXCHANGE.get(exchange_code, "")
    symbol = f"{ex}:{ticker}" if ex else ticker
    return f"https://www.tradingview.com/chart/?symbol={symbol}"


def generate_mini_chart_b64(ticker: str) -> str:
    """Mini candlestick chart สไตล์ TradingView Screener → base64 PNG"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import io, base64
        import yfinance as yf

        hist = yf.Ticker(ticker).history(period="3mo")
        if len(hist) < 5:
            return ""

        BG    = "#131722"
        GREEN = "#26a69a"
        RED   = "#ef5350"

        fig, ax = plt.subplots(figsize=(5.5, 1.6))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        opens  = hist["Open"].values
        closes = hist["Close"].values
        highs  = hist["High"].values
        lows   = hist["Low"].values
        n      = len(hist)

        for i in range(n):
            up    = closes[i] >= opens[i]
            color = GREEN if up else RED
            body_lo = min(opens[i], closes[i])
            body_hi = max(opens[i], closes[i])
            body_h  = max(body_hi - body_lo, (highs[i] - lows[i]) * 0.05)

            ax.add_patch(mpatches.Rectangle(
                (i - 0.38, body_lo), 0.76, body_h,
                color=color, zorder=2
            ))
            ax.plot([i, i], [lows[i], highs[i]],
                    color=color, linewidth=0.7, zorder=1)

        pad = (highs.max() - lows.min()) * 0.04
        ax.set_xlim(-0.8, n - 0.2)
        ax.set_ylim(lows.min() - pad, highs.max() + pad)
        ax.axis("off")
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150,
                    facecolor=BG, edgecolor="none", bbox_inches="tight", pad_inches=0.04)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()
    except Exception as e:
        print(f"  ⚠️ chart error [{ticker}]: {e}")
        return ""


# ─── Beer Analysis ────────────────────────────────────────────

def beer_analysis(stock: dict, knowledge_context: str) -> str:
    """วิเคราะห์หุ้นตาม mindset Beer Vanon"""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    direction = "ขึ้น" if stock["pct_change"] > 0 else "ลง"
    prompt = f"""คุณคือ Beer Vanon นักเทรดที่เน้น mindset จิตวิทยา และ framework การเทรดที่ชัดเจน

หลักการและ Framework ของคุณ (ใช้อ้างอิงเสมอ):
{BEER_DNA}

กรอบการบ้านจากหนังสือผู้รอด บทที่ 34 ที่ต้องใช้เป็นแกน:
{homework_prompt_block("หุ้น US")}

เนื้อหาเพิ่มเติมที่คุณเคยแชร์ไว้:
{knowledge_context}

---
ข้อมูลหุ้นที่ต้องวิเคราะห์:
- Ticker: {stock['ticker']} ({stock['name']})
- Sector: {stock['sector']}
- ราคาปัจจุบัน: ${stock['price']:.2f} ({direction} {abs(stock['pct_change']):.1f}% วันนี้)
- Volume: {stock['volume']:,}
- P/E: {stock['pe_ratio'] or 'N/A'}
- ข่าวล่าสุด:
{stock['news']}

เวลาเขียนคำตอบ ต้องมีหัวข้อ "การบ้านบทที่ 34 ที่ต้องตรวจต่อ" เสมอ
เลือก 2-3 เรื่องจาก ธุรกิจ / ตัวเลข / การสื่อสารผู้บริหาร / คู่แข่ง / ผู้บริหาร / แผนของเรา
และห้ามเดาข้อมูลที่ยังไม่มี ให้บอกว่าต้องไปตรวจอะไรต่อ

---
วิเคราะห์ในมุมมอง Beer Vanon 5 ข้อ (กระชับ ไม่เกิน 190 คำ):
1. การเคลื่อนไหวนี้เป็น FOMO หรือมีเหตุผลชัดเจน?
2. SQ (Stock Quadrant) ของหุ้นนี้น่าจะเป็นอะไร และ Trend ชัดเจนแค่ไหน?
3. ถ้าเป็น Beer จะสนใจหรือผ่าน? เพราะอะไร? (อ้าง Sniper Shot / Survivor mindset)
4. Risk ที่ต้องระวัง และ Circuit Breaker ระดับไหนที่ควรตั้ง?
5. การบ้านบทที่ 34 ที่ต้องตรวจต่อคืออะไร?

พูดตรงๆ เหมือน Beer คุยกับเพื่อนนักเทรด ไม่ต้องขึ้นต้นด้วย "ในฐานะ Beer Vanon" """

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=520,
    )
    return response.choices[0].message.content.strip()


# ─── Report Builder ───────────────────────────────────────────

def format_pct(pct: float) -> str:
    color = "#16c784" if pct >= 0 else "#ea3943"
    sign  = "+" if pct >= 0 else ""
    return f'<span style="color:{color};font-weight:bold">{sign}{pct:.2f}%</span>'


def stock_card(stock: dict, analysis: str, chart_b64: str = "", news_sentiment: str = "") -> str:
    arrow          = "▲" if stock["pct_change"] >= 0 else "▼"
    color          = "#16c784" if stock["pct_change"] >= 0 else "#ea3943"
    pe_str         = f"P/E {stock['pe_ratio']:.1f} &nbsp;|&nbsp;" if stock.get("pe_ratio") else ""
    tv_url     = stock.get("tv_url", f"https://www.tradingview.com/chart/?symbol={stock['ticker']}")
    chart_html = (
        f'<a href="{tv_url}" target="_blank" style="display:block;margin-top:12px" title="เปิดกราฟใน TradingView">'
        f'<img src="data:image/png;base64,{chart_b64}" '
        f'style="width:100%;border-radius:6px;display:block;cursor:pointer"></a>'
        if chart_b64 else ""
    )
    news_html      = _news_section_html(stock.get("news_list", []))
    sentiment_html = _sentiment_section_html(news_sentiment)
    homework_html  = _homework_section_html(stock)
    return f"""
<div style="background:#1a1f2e;border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid {color}">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
    <div>
      <span style="font-size:1.3em;font-weight:bold;color:#ffffff">{stock['ticker']}</span>
      <span style="color:#8a8f98;margin-left:8px;font-size:0.9em">{stock['name']}</span>
    </div>
    <div style="text-align:right">
      <div style="font-size:1.2em;color:#ffffff">${stock['price']:.2f}</div>
      <div style="color:{color};font-weight:bold">{arrow} {abs(stock['pct_change']):.2f}%</div>
    </div>
  </div>
  <div style="color:#a0a6b3;font-size:0.85em;margin-bottom:12px">
    Sector: {stock['sector']} &nbsp;|&nbsp; {pe_str}Volume: {stock['volume']:,}
  </div>
  {news_html}
  {sentiment_html}
  {homework_html}
  <div style="background:#111827;border-radius:8px;padding:14px;color:#d1d5db;font-size:0.95em;line-height:1.6;margin-top:12px">
    <div style="color:#f0b90b;font-weight:bold;margin-bottom:8px">🍺 Beer มองว่า...</div>
    {analysis.replace(chr(10), '<br>')}
  </div>
  {chart_html}
</div>"""


def build_html_report(gainers_data: list, losers_data: list, date_str: str) -> str:
    gainer_cards = "".join(stock_card(s["stock"], s["analysis"], s.get("chart",""), s.get("news_sentiment","")) for s in gainers_data)
    loser_cards  = "".join(stock_card(s["stock"], s["analysis"], s.get("chart",""), s.get("news_sentiment","")) for s in losers_data)
    homework_guide = homework_email_guide_html()

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0d1117;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<div style="max-width:680px;margin:0 auto;padding:24px">

  <div style="text-align:center;padding:24px 0 16px">
    <div style="font-size:2em">🍺</div>
    <h1 style="color:#ffffff;margin:8px 0 4px;font-size:1.4em">Beer Vanon Daily Report</h1>
    <div style="color:#8a8f98;font-size:0.9em">{date_str} — US Market</div>
  </div>

  <div style="border-top:1px solid #21262d;margin:16px 0"></div>

  {homework_guide}

  <h2 style="color:#16c784;font-size:1em;letter-spacing:0.05em;text-transform:uppercase">▲ Top Gainers</h2>
  {gainer_cards}

  <div style="border-top:1px solid #21262d;margin:24px 0 16px"></div>

  <h2 style="color:#ea3943;font-size:1em;letter-spacing:0.05em;text-transform:uppercase">▼ Top Losers</h2>
  {loser_cards}

  <div style="border-top:1px solid #21262d;margin:24px 0 0"></div>
  <div style="text-align:center;color:#484f58;font-size:0.8em;padding:16px 0">
    รายงานนี้สร้างโดย Beer Vanon AI Agent — เพื่อการศึกษาวิธีคิด ไม่ใช่คำแนะนำการลงทุน
  </div>
</div>
</body>
</html>"""


# ─── Email ────────────────────────────────────────────────────

def send_email(html: str, subject: str):
    user     = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")

    if not user or not password or "xxxx" in (password or ""):
        print("⚠️  ยังไม่ได้ตั้ง GMAIL_APP_PASSWORD ใน .env")
        print("   1. เปิด Google Account → Security → 2-Step Verification → App Passwords")
        print("   2. สร้าง App Password แล้วใส่ใน .env")
        print("   บันทึก report.html แทน...")
        Path("report.html").write_text(html, encoding="utf-8")
        print("   บันทึกแล้ว: report.html")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = user
    msg["To"]      = REPORT_TO
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, password)
        server.sendmail(user, REPORT_TO, msg.as_string())

    print(f"✅ ส่ง email ถึง {REPORT_TO} แล้ว")


# ─── Main ─────────────────────────────────────────────────────

def main():
    today = datetime.date.today()
    date_str = today.strftime("%A, %d %B %Y")
    print(f"\n🍺 Beer Vanon US Stock Agent — {date_str}\n{'='*50}")

    # โหลด knowledge base
    print("\n📚 โหลด knowledge base...")
    posts, embeddings, embed_model = load_knowledge()
    print(f"   {len(posts)} โพสต์ | embeddings: {'✅' if embeddings is not None else '⚠️ ไม่มี'}")

    # ดึง movers
    print("\n📈 ดึง S&P 500 movers...")
    movers = fetch_sp500_movers(TOP_N)

    gainers_data, losers_data = [], []

    # วิเคราะห์ gainers
    print(f"\n🟢 วิเคราะห์ Top {TOP_N} Gainers...")
    for ticker, pct in movers["gainers"].items():
        print(f"   [{ticker}] {pct:+.2f}%", end=" → ", flush=True)
        try:
            stock         = get_stock_context(ticker)
            query         = f"หุ้นขึ้นแรง momentum FOMO วินัย trend การเทรด {HOMEWORK_SEARCH_QUERY}"
            ctx           = search_knowledge(query, posts, embeddings, embed_model)
            analysis      = beer_analysis(stock, ctx)
            news_sentiment = analyze_news_sentiment(stock.get("news_list", []), ticker)
            chart         = generate_mini_chart_b64(ticker)
            gainers_data.append({"stock": stock, "analysis": analysis, "news_sentiment": news_sentiment, "chart": chart})
            print("✅")
        except Exception as e:
            print(f"❌ {e}")

    # วิเคราะห์ losers
    print(f"\n🔴 วิเคราะห์ Top {TOP_N} Losers...")
    for ticker, pct in movers["losers"].items():
        print(f"   [{ticker}] {pct:+.2f}%", end=" → ", flush=True)
        try:
            stock         = get_stock_context(ticker)
            query         = f"หุ้นลง ตัดขาดทุน loss ยอมรับ จิตใจ อารมณ์ {HOMEWORK_SEARCH_QUERY}"
            ctx           = search_knowledge(query, posts, embeddings, embed_model)
            analysis      = beer_analysis(stock, ctx)
            news_sentiment = analyze_news_sentiment(stock.get("news_list", []), ticker)
            chart         = generate_mini_chart_b64(ticker)
            losers_data.append({"stock": stock, "analysis": analysis, "news_sentiment": news_sentiment, "chart": chart})
            print("✅")
        except Exception as e:
            print(f"❌ {e}")

    # สร้างรายงาน
    print("\n📄 สร้างรายงาน...")
    html    = build_html_report(gainers_data, losers_data, date_str)
    subject = f"🍺 Beer Daily Report — {today.strftime('%d/%m/%Y')}"

    # ส่ง email
    print("📧 ส่ง email...")
    send_email(html, subject)

    print(f"\n✅ เสร็จสิ้น! วิเคราะห์ทั้งหมด {len(gainers_data)+len(losers_data)} หุ้น")


if __name__ == "__main__":
    main()
