"""
beer_th_agent.py
รันทุกวันหลังตลาดหุ้นไทยปิด (17:00 น.) \\u2192 วิเคราะห์ top movers SET \\u2192 ส่ง email

Setup ตั้งเวลาอัตโนมัติใน Windows Task Scheduler:
  Program : pythonw
  Arguments: "C:\\Users\\Gazill0T\\Documents\\claude ai\\stock\\beer_th_agent.py"
  Start in : C:\\Users\\Gazill0T\\Documents\\claude ai\\stock
  Trigger  : ทุกวันจันทร์-ศุกร์ เวลา 17:30 น.

รันมือ: python beer_th_agent.py
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

load_dotenv()

# ─── Config ───────────────────────────────────────────────────
KNOWLEDGE_JSON  = "beervanon_cleaned.json"
EMBEDDINGS_FILE = "embeddings.npz"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL      = "llama-3.3-70b-versatile"
TOP_N           = 5
REPORT_TO       = os.getenv("GMAIL_USER", "patiphan.injob@gmail.com")

# SET Watchlist จัดตาม sector
SET_WATCHLIST = [
    # พลังงาน
    "PTT.BK", "PTTEP.BK", "TOP.BK", "IRPC.BK", "SPRC.BK",
    # ธนาคาร
    "KBANK.BK", "SCB.BK", "BBL.BK", "KTB.BK", "BAY.BK", "TISCO.BK", "KKP.BK",
    # อสังหาริมทรัพย์
    "LH.BK", "SPALI.BK", "QH.BK", "AP.BK", "SIRI.BK",
    # ค้าปลีก / ห้าง
    "CPALL.BK", "HMPRO.BK", "BJC.BK", "GLOBAL.BK", "CRC.BK",
    # สื่อสาร
    "ADVANC.BK", "TRUE.BK",
    # ขนส่ง / ท่องเที่ยว
    "AOT.BK", "BEM.BK", "BTS.BK", "AAV.BK",
    # วัสดุ / อุตสาหกรรม
    "SCC.BK", "SCCC.BK", "PTTGC.BK",
    # สุขภาพ
    "BDMS.BK", "BCH.BK", "BH.BK", "CHG.BK",
    # อาหาร / เครื่องดื่ม
    "CPF.BK", "MINT.BK", "M.BK", "OSP.BK",
    # การเงิน / สินเชื่อ
    "KTC.BK", "MTC.BK", "SAWAD.BK", "AEONTS.BK",
    # นิคมอุตสาหกรรม
    "WHA.BK", "AMATA.BK",
]

TH_INDICES = {
    "SET":   "^SET.BK",
    "SET50": "^SET50.BK",
    "mai":   "^MAI.BK",
}

SECTOR_MAP = {
    "PTT.BK":"พลังงาน","PTTEP.BK":"พลังงาน","TOP.BK":"พลังงาน","IRPC.BK":"พลังงาน","SPRC.BK":"พลังงาน",
    "KBANK.BK":"ธนาคาร","SCB.BK":"ธนาคาร","BBL.BK":"ธนาคาร","KTB.BK":"ธนาคาร",
    "BAY.BK":"ธนาคาร","TISCO.BK":"ธนาคาร","KKP.BK":"ธนาคาร",
    "LH.BK":"อสังหาฯ","SPALI.BK":"อสังหาฯ","QH.BK":"อสังหาฯ","AP.BK":"อสังหาฯ","SIRI.BK":"อสังหาฯ",
    "CPALL.BK":"ค้าปลีก","CRC.BK":"ค้าปลีก","HMPRO.BK":"ค้าปลีก","BJC.BK":"ค้าปลีก","GLOBAL.BK":"ค้าปลีก",
    "ADVANC.BK":"สื่อสาร","TRUE.BK":"สื่อสาร",
    "AOT.BK":"ขนส่ง","BEM.BK":"ขนส่ง","BTS.BK":"ขนส่ง","AAV.BK":"ขนส่ง",
    "SCC.BK":"วัสดุ","SCCC.BK":"วัสดุ","PTTGC.BK":"วัสดุ",
    "BDMS.BK":"สุขภาพ","BCH.BK":"สุขภาพ","BH.BK":"สุขภาพ","CHG.BK":"สุขภาพ",
    "CPF.BK":"อาหาร","MINT.BK":"อาหาร","M.BK":"อาหาร","OSP.BK":"อาหาร",
    "KTC.BK":"การเงิน","MTC.BK":"การเงิน","SAWAD.BK":"การเงิน","AEONTS.BK":"การเงิน",
    "WHA.BK":"นิคม","AMATA.BK":"นิคม",
}


# ─── Knowledge Base ───────────────────────────────────────────

def load_knowledge():
    path = Path(KNOWLEDGE_JSON)
    if not path.exists():
        print(f"ไม่พบ {KNOWLEDGE_JSON}")
        return [], None, None
    posts = json.loads(path.read_text(encoding="utf-8"))
    emb_path = Path(EMBEDDINGS_FILE)
    if not emb_path.exists():
        return posts, None, None
    from sentence_transformers import SentenceTransformer
    model      = SentenceTransformer(EMBED_MODEL)
    embeddings = np.load(emb_path)["embeddings"].astype("float32")
    return posts, embeddings, model


def search_knowledge(query, posts, embeddings, embed_model, top_k=4) -> str:
    if embed_model is not None and embeddings is not None:
        q_vec   = embed_model.encode([query], normalize_embeddings=True)[0].astype("float32")
        scores  = embeddings @ q_vec
        top_idx = np.argsort(scores)[::-1][:top_k]
        relevant = [posts[i] for i in top_idx]
    else:
        words   = set(query.lower().split())
        scored  = [(sum(1 for w in words if w in p.get("content","").lower() and len(w)>2), p)
                   for p in posts]
        relevant = [p for s,p in sorted(scored, reverse=True) if s > 0][:top_k]
    parts, total = [], 0
    for p in relevant:
        chunk = p.get("content","")[:600]
        if total + len(chunk) > 2500:
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n\n---\n\n".join(parts) or "ไม่พบข้อมูล"


# ─── Market Index Snapshot ────────────────────────────────────

def fetch_index_snapshot() -> dict:
    import yfinance as yf
    result = {}
    for name, ticker in TH_INDICES.items():
        try:
            h = yf.Ticker(ticker).history(period="5d")["Close"].dropna()
            if h.empty:
                continue
            price = float(h.iloc[-1])
            prev  = float(h.iloc[-2]) if len(h) > 1 else price
            result[name] = {
                "price":      round(price, 2),
                "pct_change": round((price - prev) / prev * 100, 2),
            }
        except Exception:
            pass
    return result


# ─── SET Movers ───────────────────────────────────────────────

def fetch_set_movers(top_n: int = TOP_N) -> dict:
    import yfinance as yf
    print(f"กำลังดึงข้อมูลหุ้น {len(SET_WATCHLIST)} ตัว...")
    raw    = yf.download(SET_WATCHLIST, period="2d",
                         auto_adjust=True, progress=False, threads=True)
    closes = raw["Close"]
    pct    = closes.pct_change().iloc[-1].dropna() * 100
    pct    = pct[pct.abs() < 20]   # กรองค่าผิดปกติ

    gainers = pct.nlargest(top_n)
    losers  = pct.nsmallest(top_n)
    print(f"  Gainers: {list(gainers.index)}")
    print(f"  Losers : {list(losers.index)}")
    return {"gainers": gainers, "losers": losers}


def get_stock_context_th(ticker: str) -> dict:
    import yfinance as yf
    tk   = yf.Ticker(ticker)
    info = tk.info or {}
    hist = tk.history(period="5d")

    price_now  = float(hist["Close"].iloc[-1])  if not hist.empty else 0
    price_prev = float(hist["Close"].iloc[-2])  if len(hist) > 1 else price_now
    pct_change = (price_now - price_prev) / price_prev * 100 if price_prev else 0
    volume     = int(hist["Volume"].iloc[-1])   if not hist.empty else 0

    # ข่าว
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

    symbol = ticker.replace(".BK", "")
    return {
        "ticker":     symbol,
        "full_ticker": ticker,
        "name":       info.get("longName") or info.get("shortName") or symbol,
        "sector":     SECTOR_MAP.get(ticker) or info.get("sector", "N/A"),
        "price":      price_now,
        "pct_change": pct_change,
        "volume":     volume,
        "market_cap": info.get("marketCap", 0),
        "pe_ratio":   info.get("trailingPE"),
        "news":       news_text,
        "news_list":  news_list,
        "tv_url":     get_tradingview_url_th(symbol),
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
        'letter-spacing:0.08em;margin-bottom:8px">📰 ข่าวล่าสุด</div>'
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

def get_tradingview_url_th(symbol: str) -> str:
    return f"https://www.tradingview.com/chart/?symbol=SET:{symbol}"


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
        print(f"  chart error [{ticker}]: {e}")
        return ""


# ─── Beer Analysis (Thai) ─────────────────────────────────────

def beer_analysis_th(stock: dict, knowledge_ctx: str) -> str:
    client    = Groq(api_key=os.getenv("GROQ_API_KEY"))
    direction = "ขึ้น" if stock["pct_change"] > 0 else "ลง"

    prompt = f"""คุณคือ Beer Vanon นักเทรดหุ้นไทยที่ถนัดตลาด SET มากเป็นพิเศษ
มีหลักการและ framework ชัดเจน พูดตรงๆ ไม่อ้อมค้อม

หลักการและ Framework ของคุณ (ใช้อ้างอิงเสมอ):
{BEER_DNA}

เนื้อหาเพิ่มเติมที่คุณเคยแชร์ไว้:
{knowledge_ctx}

---
ข้อมูลหุ้นที่ต้องวิเคราะห์:
- Ticker : {stock['ticker']} ({stock['name']})
- Sector : {stock['sector']}
- ราคา   : {stock['price']:.2f} บาท ({direction} {abs(stock['pct_change']):.1f}% วันนี้)
- Volume : {stock['volume']:,} หุ้น
- P/E    : {stock['pe_ratio'] or 'N/A'}
- ข่าว   :
{stock['news']}

---
วิเคราะห์ในมุมมอง Beer Vanon 4 ข้อ (กระชับ ไม่เกิน 150 คำ):
1. การขึ้น/ลงนี้มีเหตุผลชัดเจนหรือเป็น FOMO/Panic? ดู Bid-Offer เป็นอย่างไร?
2. SQ (Stock Quadrant) น่าจะเป็นอะไร? Trend บริบทตลาด SET ตอนนี้?
3. ถ้าเป็น Beer จะสนใจหรือผ่าน? (อ้าง Sniper Shot / Survivor mindset / Time Zone)
4. Risk ที่ต้องระวัง และรูปแบบหุ้นนี้ใกล้เคียงกับ pattern ไหน (บันได/ลิฟท์/เข็มฉีดยา)?

พูดตรงๆ เหมือน Beer คุยกับเพื่อนนักเทรด อ้างหลักการตัวเองชัดๆ"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()


# ─── Report Builder ───────────────────────────────────────────

def fmt_pct(pct: float) -> str:
    color = "#16c784" if pct >= 0 else "#ea3943"
    sign  = "+" if pct >= 0 else ""
    return f'<span style="color:{color};font-weight:bold">{sign}{pct:.2f}%</span>'


def stock_card_th(stock: dict, analysis: str, chart_b64: str = "", news_sentiment: str = "") -> str:
    arrow          = "▲" if stock["pct_change"] >= 0 else "▼"
    color          = "#16c784" if stock["pct_change"] >= 0 else "#ea3943"
    pe             = f"P/E {stock['pe_ratio']:.1f} &nbsp;|&nbsp;" if stock["pe_ratio"] else ""
    tv_url     = stock.get("tv_url", f"https://www.tradingview.com/chart/?symbol=SET:{stock['ticker']}")
    chart_html = (
        f'<a href="{tv_url}" target="_blank" style="display:block;margin-top:12px" title="เปิดกราฟใน TradingView">'
        f'<img src="data:image/png;base64,{chart_b64}" '
        f'style="width:100%;border-radius:6px;display:block;cursor:pointer"></a>'
        if chart_b64 else ""
    )
    news_html      = _news_section_html(stock.get("news_list", []))
    sentiment_html = _sentiment_section_html(news_sentiment)
    return f"""
<div style="background:#1a1f2e;border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid {color}">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
    <div>
      <span style="font-size:1.3em;font-weight:bold;color:#ffffff">{stock['ticker']}</span>
      <span style="color:#8a8f98;margin-left:8px;font-size:0.85em">{stock['name']}</span>
      <span style="background:#1e2329;color:#f0b90b;border-radius:4px;padding:1px 7px;
            font-size:0.75em;margin-left:6px">{stock['sector']}</span>
    </div>
    <div style="text-align:right">
      <div style="font-size:1.2em;color:#ffffff">฿{stock['price']:.2f}</div>
      <div style="color:{color};font-weight:bold">{arrow} {abs(stock['pct_change']):.2f}%</div>
    </div>
  </div>
  <div style="color:#a0a6b3;font-size:0.82em;margin-bottom:12px">
    {pe}Volume: {stock['volume']:,}
  </div>
  {news_html}
  {sentiment_html}
  <div style="background:#111827;border-radius:8px;padding:14px;color:#d1d5db;font-size:0.95em;line-height:1.6;margin-top:12px">
    <div style="color:#f0b90b;font-weight:bold;margin-bottom:8px">🍺 Beer มองว่า...</div>
    {analysis.replace(chr(10), '<br>')}
  </div>
  {chart_html}
</div>"""


def index_pill(name: str, d: dict | None) -> str:
    if not d:
        return ""
    c     = "#16c784" if d["pct_change"] >= 0 else "#ea3943"
    arrow = "▲" if d["pct_change"] >= 0 else "▼"
    return (f'<span style="background:#1a1f2e;border-radius:8px;padding:8px 14px;'
            f'display:inline-block;margin:4px">'
            f'<span style="color:#8a8f98;font-size:0.8em">{name} </span>'
            f'<span style="color:#fff;font-weight:bold">{d["price"]:,.2f}</span> '
            f'<span style="color:{c}">{arrow}{abs(d["pct_change"]):.2f}%</span></span>')


def build_html_report_th(gainers_data, losers_data, index_snap, date_str) -> str:
    gainer_cards = "".join(stock_card_th(s["stock"], s["analysis"], s.get("chart",""), s.get("news_sentiment","")) for s in gainers_data)
    loser_cards  = "".join(stock_card_th(s["stock"], s["analysis"], s.get("chart",""), s.get("news_sentiment","")) for s in losers_data)
    index_row    = "".join(index_pill(k, index_snap.get(k)) for k in ["SET","SET50","mai"])

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0d1117;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<div style="max-width:680px;margin:0 auto;padding:24px">

  <div style="text-align:center;padding:24px 0 16px">
    <div style="font-size:2em">🍺</div>
    <h1 style="color:#ffffff;margin:8px 0 4px;font-size:1.4em">Beer Vanon — รายงานหุ้นไทย</h1>
    <div style="color:#8a8f98;font-size:0.9em">{date_str}</div>
    <div style="margin-top:10px">{index_row}</div>
  </div>

  <div style="border-top:1px solid #21262d;margin:16px 0"></div>

  <h2 style="color:#16c784;font-size:1em;letter-spacing:0.05em;text-transform:uppercase">▲ Top Gainers วันนี้</h2>
  {gainer_cards}

  <div style="border-top:1px solid #21262d;margin:24px 0 16px"></div>

  <h2 style="color:#ea3943;font-size:1em;letter-spacing:0.05em;text-transform:uppercase">▼ Top Losers วันนี้</h2>
  {loser_cards}

  <div style="border-top:1px solid #21262d;margin:24px 0 0"></div>
  <div style="text-align:center;color:#484f58;font-size:0.8em;padding:16px 0">
    Beer Vanon AI — รายงานหุ้นไทยอัตโนมัติ เพื่อการศึกษา ไม่ใช่คำแนะนำลงทุน
  </div>
</div>
</body>
</html>"""


# ─── Email ────────────────────────────────────────────────────

def send_email(html: str, subject: str):
    user     = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not user or not password or "xxxx" in (password or ""):
        out = Path("beer_th_report.html")
        out.write_text(html, encoding="utf-8")
        print(f"ยังไม่ได้ตั้ง GMAIL_APP_PASSWORD — บันทึกเป็น {out}")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = user
    msg["To"]      = REPORT_TO
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, password)
        server.sendmail(user, REPORT_TO, msg.as_string())
    print(f"ส่ง email ถึง {REPORT_TO} แล้ว")


# ─── Main ─────────────────────────────────────────────────────

def main():
    today    = datetime.date.today()
    date_str = today.strftime("%A, %d %B %Y")
    print(f"\nBeer Vanon TH Agent — {date_str}\n{'='*50}")

    # Knowledge base
    print("\nโหลด knowledge base...")
    posts, embeddings, embed_model = load_knowledge()
    print(f"  {len(posts)} โพสต์ | embeddings: {'OK' if embeddings is not None else 'keyword only'}")

    # Index snapshot
    print("\nดึง SET Index...")
    index_snap = fetch_index_snapshot()
    for k, v in index_snap.items():
        print(f"  {k}: {v['price']:,.2f} ({v['pct_change']:+.2f}%)")

    # Movers
    print("\nดึง SET movers...")
    movers = fetch_set_movers(TOP_N)

    gainers_data, losers_data = [], []

    print(f"\nวิเคราะห์ Top {TOP_N} Gainers...")
    for ticker, pct in movers["gainers"].items():
        symbol = ticker.replace(".BK","")
        print(f"  [{symbol}] {pct:+.2f}%", end=" → ", flush=True)
        try:
            stock          = get_stock_context_th(ticker)
            query          = "หุ้นขึ้นแรง momentum FOMO วินัย trend ตลาดไทย"
            ctx            = search_knowledge(query, posts, embeddings, embed_model)
            analysis       = beer_analysis_th(stock, ctx)
            news_sentiment = analyze_news_sentiment(stock.get("news_list", []), symbol)
            chart          = generate_mini_chart_b64(ticker)
            gainers_data.append({"stock": stock, "analysis": analysis, "news_sentiment": news_sentiment, "chart": chart})
            print("OK")
        except Exception as e:
            print(f"Error: {e}")

    print(f"\nวิเคราะห์ Top {TOP_N} Losers...")
    for ticker, pct in movers["losers"].items():
        symbol = ticker.replace(".BK","")
        print(f"  [{symbol}] {pct:+.2f}%", end=" → ", flush=True)
        try:
            stock          = get_stock_context_th(ticker)
            query          = "หุ้นลง ตัดขาดทุน loss ยอมรับ จิตใจ อารมณ์ ตลาดไทย"
            ctx            = search_knowledge(query, posts, embeddings, embed_model)
            analysis       = beer_analysis_th(stock, ctx)
            news_sentiment = analyze_news_sentiment(stock.get("news_list", []), symbol)
            chart          = generate_mini_chart_b64(ticker)
            losers_data.append({"stock": stock, "analysis": analysis, "news_sentiment": news_sentiment, "chart": chart})
            print("OK")
        except Exception as e:
            print(f"Error: {e}")

    print("\nสร้างรายงาน...")
    html    = build_html_report_th(gainers_data, losers_data, index_snap, date_str)
    subject = f"Beer หุ้นไทย {today.strftime('%d/%m/%Y')} — {len(gainers_data)+len(losers_data)} หุ้น"

    print("ส่ง email...")
    send_email(html, subject)
    print(f"\nเสร็จ! วิเคราะห์ {len(gainers_data)+len(losers_data)} หุ้น")


if __name__ == "__main__":
    main()
