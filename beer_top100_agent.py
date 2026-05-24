"""
beer_top100_agent.py
100 หุ้น US ขนาดใหญ่สุด (Market Cap) เรียงจากใหญ่ไปเล็ก
วิเคราะห์ทุกตัว → ส่ง email ทุกวัน จ-ศ หลังตลาดปิด
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os, json, smtplib, datetime, time
import numpy as np
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from groq import Groq
from beer_dna import BEER_DNA

load_dotenv()

# ─── Config ───────────────────────────────────────────────────
KNOWLEDGE_JSON  = "beervanon_cleaned.json"
EMBEDDINGS_FILE = "embeddings.npz"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL      = "llama-3.1-8b-instant"   # higher daily token limit สำหรับ 100 หุ้น
REPORT_TO       = os.getenv("GMAIL_USER", "patiphan.injob@gmail.com")
TOP_N           = 100
CALL_DELAY      = 1.2   # วินาที ระหว่าง Groq call (ป้องกัน rate limit)

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


def search_knowledge(query: str, posts, embeddings, embed_model, top_k=3) -> str:
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

    print(f"  ดึง market cap {len(tickers)} หุ้น (parallel)...")
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


def get_stock_context(ticker: str, rank: int) -> dict:
    import yfinance as yf
    tk   = yf.Ticker(ticker)
    info = tk.info or {}
    hist = tk.history(period="5d")

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

def generate_mini_chart_b64(ticker: str) -> str:
    """Mini candlestick JPEG สไตล์ TradingView Screener — ~2.8KB ต่อรูป"""
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
        return base64.b64encode(buf.read()).decode()
    except Exception as e:
        print(f"  chart error [{ticker}]: {e}")
        return ""


# ─── Combined Analysis ────────────────────────────────────────

def combined_analysis(stock: dict, knowledge_ctx: str) -> str:
    """ONE Groq call: ข่าวคืออะไร + Beer มองว่า (ประหยัด token สำหรับ 100 หุ้น)"""
    client    = Groq(api_key=os.getenv("GROQ_API_KEY"))
    direction = "ขึ้น" if stock["pct_change"] > 0 else "ลง"

    prompt = f"""คุณคือ Beer Vanon วิเคราะห์หุ้น {stock['ticker']} ({stock['name']})

หลักการ Beer Vanon (อ้างอิง):
{BEER_DNA[:1200]}

เนื้อหาเพิ่มเติม:
{knowledge_ctx}

ข้อมูลหุ้น:
- ราคา: ${stock['price']:.2f} ({direction} {abs(stock['pct_change']):.1f}%) | Sector: {stock['sector']}
- Market Cap Rank: #{stock['rank']} ในตลาด | Volume: {stock['volume']:,}
- P/E: {stock['pe_ratio'] or 'N/A'}

ข่าวล่าสุด:
{stock['news']}

ตอบ 2 ส่วน (รวมไม่เกิน 160 คำ ภาษาไทย กระชับ ตรงประเด็น):

**📰 ข่าวคืออะไร + ตลาดจะตีความอย่างไร:**
อธิบายว่าข่าวพูดถึงอะไร เกิดอะไรขึ้น แล้วนักลงทุนจะมองบวก/ลบ/กลาง เพราะอะไร

**🍺 Beer มองว่า:**
SQ ของหุ้นนี้ น่าสนใจหรือผ่าน Circuit Breaker ที่ควรตั้ง พูดตรงๆ"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=280,
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


def _fmt_mktcap(cap: float) -> str:
    if cap >= 1e12:
        return f"${cap/1e12:.2f}T"
    if cap >= 1e9:
        return f"${cap/1e9:.1f}B"
    if cap > 0:
        return f"${cap/1e6:.0f}M"
    return "N/A"


def stock_card(stock: dict, analysis: str, chart_b64: str) -> str:
    sparkline_svg = chart_b64  # rename internally
    arrow  = "▲" if stock["pct_change"] >= 0 else "▼"
    color  = "#16c784" if stock["pct_change"] >= 0 else "#ea3943"
    pe_str = f" | P/E {stock['pe_ratio']:.1f}" if stock.get("pe_ratio") else ""
    cap_str = _fmt_mktcap(stock["market_cap"])

    tv_url  = stock.get("tv_url", f"https://www.tradingview.com/chart/?symbol={stock['ticker']}")
    chart_block = (
        f'<a href="{tv_url}" target="_blank" title="เปิดกราฟใน TradingView" style="display:block;margin-top:10px">'
        f'<img src="data:image/jpeg;base64,{sparkline_svg}" '
        f'style="width:100%;border-radius:5px;display:block;cursor:pointer"></a>'
        if sparkline_svg else
        f'<div style="margin-top:8px"><a href="{tv_url}" target="_blank" '
        f'style="color:#6366f1;font-size:0.82em;text-decoration:none">📊 ดูกราฟบน TradingView →</a></div>'
    )

    news_html = _news_html(stock.get("news_list", []))
    analysis_body = analysis.replace(chr(10), "<br>")

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
  {news_html}
  <div style="background:#111827;border-radius:8px;padding:12px;color:#d1d5db;font-size:0.92em;line-height:1.65;margin-top:10px">
    <div style="color:#f0b90b;font-weight:bold;margin-bottom:6px">🍺 วิเคราะห์</div>
    {analysis_body}
  </div>
</div>"""


# ─── HTML Report ──────────────────────────────────────────────

def build_html_report(stocks_data: list, date_str: str) -> str:
    cards = "".join(
        stock_card(s["stock"], s["analysis"], s.get("sparkline", ""))
        for s in stocks_data
    )

    gainers = [s for s in stocks_data if s["stock"]["pct_change"] > 0]
    losers  = [s for s in stocks_data if s["stock"]["pct_change"] < 0]
    avg_chg = np.mean([s["stock"]["pct_change"] for s in stocks_data]) if stocks_data else 0
    sentiment_color = "#16c784" if avg_chg >= 0 else "#ea3943"
    sentiment_label = f"{'▲' if avg_chg >= 0 else '▼'} {abs(avg_chg):.2f}% avg · {len(gainers)} ขึ้น / {len(losers)} ลง"

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
  </div>

  <div style="border-top:1px solid #21262d;margin:14px 0 20px"></div>

  {cards}

  <div style="border-top:1px solid #21262d;margin:20px 0 0"></div>
  <div style="text-align:center;color:#484f58;font-size:0.78em;padding:14px 0">
    Beer Vanon AI · Top 100 Market Cap · เพื่อการศึกษา ไม่ใช่คำแนะนำลงทุน
  </div>
</div>
</body>
</html>"""


# ─── Email ────────────────────────────────────────────────────

def send_email(html: str, subject: str):
    user     = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not user or not password or "xxxx" in (password or ""):
        out = Path("beer_top100_report.html")
        out.write_text(html, encoding="utf-8")
        print(f"  ยังไม่ได้ตั้ง GMAIL — บันทึกเป็น {out}")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = user
    msg["To"]      = REPORT_TO
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, password)
        server.sendmail(user, REPORT_TO, msg.as_string())
    print(f"  ✅ ส่ง email ถึง {REPORT_TO}")


# ─── Main ─────────────────────────────────────────────────────

def main():
    today    = datetime.date.today()
    date_str = today.strftime("%A, %d %B %Y")
    print(f"\n🍺 Beer Top 100 Agent — {date_str}\n{'='*55}")

    # 1. Knowledge base
    print("\n📚 โหลด knowledge base...")
    posts, embeddings, embed_model = load_knowledge()
    print(f"   {len(posts)} โพสต์ | embeddings: {'✅' if embeddings is not None else '⚠️'}")

    # 2. Market cap ranking
    print("\n📊 จัดลำดับ Market Cap...")
    mktcaps = fetch_market_caps(US_UNIVERSE)
    ranked  = sorted(US_UNIVERSE, key=lambda t: mktcaps.get(t, 0), reverse=True)
    top100  = [t for t in ranked if mktcaps.get(t, 0) > 0][:TOP_N]
    print(f"   Top {len(top100)} หุ้น | อันดับ 1: {top100[0]} ({_fmt_mktcap(mktcaps.get(top100[0],0))})")

    # 3. วิเคราะห์ทีละหุ้น
    stocks_data = []
    print(f"\n🔍 วิเคราะห์ {len(top100)} หุ้น...")
    for i, ticker in enumerate(top100, 1):
        rank = i
        print(f"   [{rank:3d}] {ticker:<8}", end=" → ", flush=True)
        try:
            stock     = get_stock_context(ticker, rank)
            query     = "trend momentum หุ้นใหญ่ market cap SQ วินัย"
            ctx       = search_knowledge(query, posts, embeddings, embed_model)
            analysis  = combined_analysis(stock, ctx)
            chart = generate_mini_chart_b64(ticker)
            stocks_data.append({"stock": stock, "analysis": analysis, "sparkline": chart})
            print(f"✅  {stock['pct_change']:+.1f}%")
            time.sleep(CALL_DELAY)
        except Exception as e:
            err = str(e)[:80]
            print(f"❌  {err}")
            if "rate_limit" in err.lower():
                print("      ⏳ rate limit — รอ 30 วินาที...")
                time.sleep(30)

    # 4. สร้างและส่ง email
    print(f"\n📄 สร้างรายงาน ({len(stocks_data)} หุ้น)...")
    html    = build_html_report(stocks_data, date_str)
    subject = f"🍺 Beer Top 100 Market Cap — {today.strftime('%d/%m/%Y')} ({len(stocks_data)} หุ้น)"
    print("📧 ส่ง email...")
    send_email(html, subject)

    print(f"\n✅ เสร็จสิ้น! วิเคราะห์ {len(stocks_data)}/{len(top100)} หุ้น")


if __name__ == "__main__":
    main()
