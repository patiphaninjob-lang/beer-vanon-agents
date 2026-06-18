"""
Thai Beer homework framework.
Independent copy for the Thai Top 100 system.
"""

HOMEWORK_FRAMEWORK_TITLE = "บทที่ 34 — การบ้านที่ไม่มีอาจารย์ตรวจ (Thai Market)"

HOMEWORK_FRAMEWORK_TEXT = """กรอบการบ้านหลักที่ต้องใช้ทุกครั้ง:
1) ธุรกิจ — บริษัทขายอะไร ลูกค้าคือใคร แข่งกับใคร ทำเงินยังไง
2) ตัวเลข — รายได้ กำไร หนี้ กระแสเงินสด valuation ดีขึ้นหรือแย่ลง
3) การสื่อสาร — ผู้บริหารพูดอะไร ต้องไปฟัง call/read filing/ดู presentation อะไรเพิ่ม
4) คู่แข่ง — ใครดีกว่า ใครแย่กว่า ตัวนี้เสียเปรียบหรือได้เปรียบตรงไหน
5) ผู้บริหาร — ประวัติ การตัดสินใจ capital allocation ความน่าเชื่อถือ และความเสี่ยง
6) แผนของเรา — ตามดู ถือ งด รอจุดไหน และอะไรคือจุดที่ถ้าคิดผิดต้องยอมรับ

หลักคิด: ทำละเอียด 5 ตัว ดีกว่าทำผิวเผิน 50 ตัว และห้ามแต่งข้อมูลที่ยังไม่รู้ ให้บอกว่าต้องไปต่อ"""

HOMEWORK_SEARCH_QUERY = (
    "การบ้านหุ้นไทย เข้าใจธุรกิจ รายได้ กำไร หนี้ กระแสเงินสด ผู้บริหาร คู่แข่ง "
    "valuation conference call annual report filing ความเสี่ยง แผนการเทรด จุดที่คิดผิด SET100"
)


def homework_prompt_block(market_label: str = "หุ้นไทย") -> str:
    return f"""{HOMEWORK_FRAMEWORK_TITLE}
ใช้กรอบนี้กับ{market_label}ทุกตัว ไม่ใช่ดูกราฟอย่างเดียว:
{HOMEWORK_FRAMEWORK_TEXT}

เวลาตอบ ให้เชื่อมกรอบนี้กับข้อมูลจริงที่มีอยู่ ถ้าข้อมูลด้านใดยังไม่มี ให้เขียนเป็นการบ้านที่ต้องไปเติม ไม่เดาขึ้นมาเอง"""


def build_stock_homework_checklist(stock: dict) -> list[dict]:
    ticker = stock.get("ticker") or "หุ้นตัวนี้"
    sector = stock.get("sector") or "sector นี้"
    return [
        {
            "topic": "ธุรกิจ",
            "prompt": f"{ticker} ขายอะไร ลูกค้าคือใคร แข่งกับใคร และทำเงินจากอะไรใน {sector}",
        },
        {
            "topic": "ตัวเลข",
            "prompt": "เช็ครายได้ กำไร หนี้ กระแสเงินสด valuation และ P/E ว่ารองรับราคาตอนนี้ไหม",
        },
        {
            "topic": "การสื่อสาร",
            "prompt": "หา earnings call, OP Day, filing หรือ presentation ล่าสุดว่าผู้บริหารอธิบายอนาคตอย่างไร",
        },
        {
            "topic": "คู่แข่ง",
            "prompt": f"เทียบ {ticker} กับคู่แข่งหลักใน {sector}: ใครโตจริง ใครแพงเกิน ใครเสียเปรียบ",
        },
        {
            "topic": "ผู้บริหาร",
            "prompt": "ดู capital allocation, buyback, dilution, deal, ประวัติการตัดสินใจ และความน่าเชื่อถือ",
        },
        {
            "topic": "แผนของเรา",
            "prompt": "สรุปว่าจะตามดู ถือ งด หรือรออะไร และตั้งจุดที่ถ้าคิดผิดต้องยอมรับ",
        },
    ]


def homework_email_guide_html() -> str:
    items = build_stock_homework_checklist({"ticker": "หุ้นไทย", "sector": "sector"})
    rows = "".join(
        f'<div style="border-left:2px solid #30363d;background:#0d1117;border-radius:0 6px 6px 0;'
        f'padding:8px 10px;margin:6px 0">'
        f'<div style="color:#f0b90b;font-size:0.78em;font-weight:bold">{item["topic"]}</div>'
        f'<div style="color:#d1d5db;font-size:0.84em;line-height:1.5">{item["prompt"]}</div>'
        f'</div>'
        for item in items
    )
    return (
        '<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;'
        'padding:12px;margin:12px 0 18px">'
        f'<div style="color:#ffffff;font-weight:bold;margin-bottom:4px">{HOMEWORK_FRAMEWORK_TITLE}</div>'
        '<div style="color:#8a8f98;font-size:0.82em;line-height:1.5;margin-bottom:8px">'
        'ทำละเอียด 5 ตัว ดีกว่าทำผิวเผิน 50 ตัว — ทุกการบ้านต้องโยงธุรกิจ ตัวเลข ข่าว ผู้บริหาร คู่แข่ง และแผนของเรา'
        '</div>'
        f'{rows}'
        '</div>'
    )
