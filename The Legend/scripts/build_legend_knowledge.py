from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPTS = ROOT / "transcripts"
OUT = ROOT / "knowledge"
LESSONS_OUT = OUT / "lessons"


LESSON_GUIDE = {
    1: {
        "slug": "01_way_to_financial_freedom",
        "title": "สร้างพอร์ต 300 เท่า Way to Financial Freedom",
        "phase": "ตั้งเป้าหมายและระบบคิด",
        "category": "Mindset",
        "thesis": "Technical Analysis เป็นเพียงส่วนหนึ่งของความสำเร็จ การสร้างอิสรภาพทางการเงินต้องเริ่มจากเป้าหมายชีวิต เวลา ความเสี่ยง และระบบคิดต่อเงิน",
        "objectives": [
            "เข้าใจว่าทำไมการเรียนหุ้นต้องเริ่มจากเป้าหมาย ไม่ใช่เครื่องมือ",
            "แยกให้ออกว่า technical เป็นแค่ส่วนหนึ่งของระบบเทรด",
            "ตั้งกรอบเวลาและเหตุผลส่วนตัวว่าต้องการอิสรภาพทางการเงินเพื่ออะไร",
        ],
        "keywords": ["อิสรภาพ", "technical", "เทคนิค", "เวลา", "การเงิน", "แผน", "ความสำเร็จ"],
        "practice": "เขียนเป้าหมายพอร์ต 3 ระยะ: อยู่รอด, โตต่อเนื่อง, อิสรภาพ แล้วกำหนดความเสี่ยงที่ยอมรับได้ในแต่ละระยะ",
    },
    2: {
        "slug": "02_beer_wanon_trading",
        "title": "เคล็ดลับการเทรดในแบบ เบียร์ วนนท์",
        "phase": "เรียนจากประสบการณ์นักเทรด",
        "category": "Trader Mind",
        "thesis": "ประสบการณ์ของนักเทรดช่วยให้เห็นว่าความสำเร็จไม่ได้มาจากสูตรเดียว แต่มาจากการสังเกต ซ้ำ ทบทวน และปรับตัวกับตลาด",
        "objectives": [
            "จับหลักคิดจากกรณีศึกษาของนักเทรดจริง",
            "แยกพฤติกรรมที่ควรเลียนแบบออกจากรายละเอียดเฉพาะบุคคล",
            "แปลงประสบการณ์คนอื่นเป็น checklist ของตัวเอง",
        ],
        "keywords": ["เทรด", "ประสบการณ์", "วิธี", "ตลาด", "หุ้น", "กำไร", "ขาดทุน"],
        "practice": "เลือก 3 แนวคิดจากบทนี้ แล้วเขียนว่าแนวคิดนั้นจะเปลี่ยนวิธีเทรดของตัวเองอย่างไร",
    },
    3: {
        "slug": "03_safe_portfolio_growth",
        "title": "สูตรปั้นพอร์ตอย่างปลอดภัย",
        "phase": "วางระบบความเสี่ยง",
        "category": "Risk",
        "thesis": "การปั้นพอร์ตต้องชนะเกมระยะยาวก่อน ช่วงที่ผิดต้องเสียให้น้อยพอที่จะกลับมาเล่นต่อได้",
        "objectives": [
            "เข้าใจความต่างระหว่างโตเร็วกับโตอย่างอยู่รอด",
            "กำหนด risk per trade และจุดหยุดพัก",
            "รู้ว่าการรักษาทุนคือเงื่อนไขก่อนการเร่งพอร์ต",
        ],
        "keywords": ["ปลอดภัย", "พอร์ต", "ความเสี่ยง", "ขาดทุน", "กำไร", "เงิน", "ระบบ"],
        "practice": "สร้างกฎ 5 ข้อสำหรับหยุดเทรดเมื่อเสียจังหวะ เช่น แพ้ติดกันกี่ไม้ หรือเสียกี่เปอร์เซ็นต์ต่อวัน",
    },
    4: {
        "slug": "04_set100_strategy",
        "title": "เทรดหุ้น SET100 ยังไงให้ได้หลักล้าน",
        "phase": "เลือกสนามเทรด",
        "category": "Strategy",
        "thesis": "หุ้นขนาดใหญ่มีสภาพคล่องและพฤติกรรมเฉพาะตัว การเทรด SET100 ต้องใช้แผนที่เหมาะกับแรงและรอบของหุ้นใหญ่",
        "objectives": [
            "เข้าใจข้อดีข้อจำกัดของหุ้น SET100",
            "แยกหุ้นมีสภาพคล่องจริงออกจากหุ้นที่เคลื่อนไหวยาก",
            "วางแผนเทรดหุ้นใหญ่ด้วย reward/risk ที่เหมาะสม",
        ],
        "keywords": ["SET100", "หุ้น", "ล้าน", "สภาพคล่อง", "พอร์ต", "เทรด", "รอบ"],
        "practice": "เลือกหุ้น SET100 5 ตัว แล้วบันทึกว่าแต่ละตัวเหมาะกับ swing, day trade หรือหลีกเลี่ยง เพราะอะไร",
    },
    5: {
        "slug": "05_prop_trade_professional",
        "title": "Prop Trade Professional",
        "phase": "คิดแบบมืออาชีพ",
        "category": "Execution",
        "thesis": "Prop trader ไม่ได้คิดเป็นไม้เดี่ยว แต่คิดเป็นกระบวนการ วินัย สถิติ และการจัดการสถานะซ้ำ ๆ",
        "objectives": [
            "เข้าใจวิธีคิดแบบ professional trader",
            "แยกการตัดสินใจจากอารมณ์ระหว่างวัน",
            "สร้าง routine ก่อนเข้า ระหว่างถือ และหลังออก",
        ],
        "keywords": ["prop", "professional", "วินัย", "เทรด", "ระบบ", "กำไร", "ขาดทุน"],
        "practice": "ทำ trading routine 3 ช่วง: ก่อนตลาดเปิด, ระหว่างถือสถานะ, หลังปิดตลาด",
    },
    6: {
        "slug": "06_swing_trade",
        "title": "Swing Trade Professional Trader",
        "phase": "จับรอบราคา",
        "category": "Strategy",
        "thesis": "Swing trade คือการรอจังหวะที่ราคา โครงสร้าง และแรงสนับสนุนอยู่ข้างเดียวกัน แล้วถือให้พอเหมาะกับรอบ",
        "objectives": [
            "เข้าใจจังหวะเข้าออกของ swing trade",
            "ใช้โครงสร้างราคาเพื่อกำหนด stop และ target",
            "ฝึกความอดทนระหว่างถือรอบ",
        ],
        "keywords": ["swing", "รอบ", "แนวโน้ม", "กราฟ", "ถือ", "เป้า", "stop"],
        "practice": "เปิดกราฟย้อนหลัง 10 ตัวอย่าง แล้วมาร์กจุดเข้า จุดผิดทาง และจุดขายตาม swing setup",
    },
    7: {
        "slug": "07_money_game",
        "title": "Money Game บ้านหนึ่งหลัง รถสองคัน",
        "phase": "เชื่อมเงินกับชีวิต",
        "category": "Mindset",
        "thesis": "เป้าหมายการเงินต้องจับต้องได้พอที่จะเปลี่ยนพฤติกรรมรายวัน ไม่ใช่แค่ตัวเลขลอย ๆ ในพอร์ต",
        "objectives": [
            "แปลงเป้าหมายชีวิตเป็นเป้าหมายการเงิน",
            "เห็นความสัมพันธ์ระหว่างพฤติกรรมวันนี้กับทรัพย์สินอนาคต",
            "วางแผนเรียนหุ้นให้สอดคล้องกับเป้าหมายจริง",
        ],
        "keywords": ["บ้าน", "รถ", "เงิน", "เป้าหมาย", "ชีวิต", "พอร์ต", "อิสระ"],
        "practice": "เขียนเป้าหมายทรัพย์สิน 3 อย่าง แล้วคำนวณว่าต้องการผลตอบแทน/เงินทุนเท่าไรจึงจะไปถึง",
    },
    8: {
        "slug": "08_scalper",
        "title": "Scalper เทรดสั้น ปั้นพอร์ต",
        "phase": "ฝึกความเร็วและวินัย",
        "category": "Execution",
        "thesis": "Scalping เป็นเกมของความเร็ว ความชัด และการยอมผิดทันที ต้องมีเงื่อนไขเข้าออกที่แคบและวัดได้",
        "objectives": [
            "เข้าใจข้อจำกัดของการเทรดสั้น",
            "อ่านแรงซื้อขายระยะใกล้โดยไม่ไล่ราคาแบบไร้แผน",
            "สร้างกฎออกเร็วเมื่อ setup ไม่ทำงาน",
        ],
        "keywords": ["scalper", "สั้น", "เร็ว", "bid", "offer", "เด้ง", "คัท"],
        "practice": "จำลอง scalping ด้วย replay 20 ไม้ แล้วบันทึกว่าผิดเพราะช้า ไล่ราคา หรือไม่มีแผน",
    },
    9: {
        "slug": "09_all_in_fundamental",
        "title": "วิธีการ All in ด้วย Fundamental",
        "phase": "สร้าง conviction",
        "category": "Fundamental",
        "thesis": "การเพิ่มน้ำหนักด้วย fundamental ต้องมี thesis ชัด มีข้อมูลรองรับ และรู้เงื่อนไขที่ทำให้สมมติฐานผิด",
        "objectives": [
            "เข้าใจว่า conviction ต่างจากความมั่นใจลอย ๆ",
            "เชื่อมงบ กิจการ catalyst และ timing",
            "กำหนด invalidation point ของ thesis",
        ],
        "keywords": ["all in", "fundamental", "พื้นฐาน", "งบ", "กำไร", "กิจการ", "เติบโต"],
        "practice": "เขียน investment thesis 1 หน้าให้หุ้นหนึ่งตัว พร้อมเหตุผลเข้า เหตุผลออก และข้อมูลที่ต้องติดตาม",
    },
    10: {
        "slug": "10_day_trade_operator",
        "title": "อ่านใจเจ้ามือแบบ Day Trade",
        "phase": "อ่านพฤติกรรมรายวัน",
        "category": "Execution",
        "thesis": "การอ่านเจ้ามือคือการอ่านร่องรอยของ supply/demand, trap และ reaction ในวัน ไม่ใช่การเดาเจตนาคน",
        "objectives": [
            "อ่านแรงซื้อขายในวันผ่านราคาและ volume",
            "แยก breakout จริงออกจากการหลอก",
            "ตั้งแผน day trade ที่มีจุดผิดชัด",
        ],
        "keywords": ["เจ้ามือ", "day trade", "แรงซื้อ", "แรงขาย", "หลอก", "volume", "ราคา"],
        "practice": "เลือกกราฟ intraday 3 วัน แล้วเขียนว่าจุดไหนคือ trap จุดไหนคือ confirmation",
    },
    11: {
        "slug": "11_trading_strategy",
        "title": "Trading Strategy",
        "phase": "ประกอบระบบเทรด",
        "category": "Strategy",
        "thesis": "กลยุทธ์ที่ดีต้องตอบครบว่าเข้าเมื่อไร ออกเมื่อไร ผิดตรงไหน ขนาดสถานะเท่าไร และจะทบทวนผลอย่างไร",
        "objectives": [
            "ประกอบ entry, exit, stop, target และ sizing เป็นระบบเดียว",
            "แยก strategy ออกจากความรู้สึกระหว่างตลาดวิ่ง",
            "สร้าง journal เพื่อปรับระบบจากข้อมูลจริง",
        ],
        "keywords": ["strategy", "ระบบ", "เข้า", "ออก", "stop", "target", "journal"],
        "practice": "เขียน strategy card 1 ใบ: setup, trigger, stop, target, sizing, no-trade condition",
    },
    12: {
        "slug": "12_elliott_wave_fibonacci",
        "title": "Elliott Wave + Fibonacci",
        "phase": "อ่านโครงสร้างคลื่น",
        "category": "Technical",
        "thesis": "Wave และ Fibonacci เป็นแผนที่ความน่าจะเป็น ช่วยจัด scenario และจุดวัด ไม่ใช่เครื่องมือทำนายแบบตายตัว",
        "objectives": [
            "เข้าใจโครงสร้างคลื่นและจังหวะย่อ/ไปต่อ",
            "ใช้ Fibonacci เพื่อวัดโซน ไม่ใช่เส้นศักดิ์สิทธิ์",
            "สร้างหลาย scenario แล้วเลือกแผนที่ risk/reward คุ้ม",
        ],
        "keywords": ["Elliott", "Fibonacci", "คลื่น", "wave", "ย่อ", "แนวรับ", "แนวต้าน"],
        "practice": "มาร์ก wave count อย่างน้อย 2 scenario ในกราฟเดียว แล้วเขียนแผนรับมือทั้งสองแบบ",
    },
    13: {
        "slug": "13_bid_offer_analysis",
        "title": "Bid Offer Analysis",
        "phase": "อ่าน order flow",
        "category": "Order Flow",
        "thesis": "Bid/Offer คือข้อมูลใกล้ตลาดที่สุด แต่ต้องอ่านร่วมกับราคา volume และ reaction เพราะตัวเลขบนกระดานถูกจัดฉากได้",
        "objectives": [
            "เข้าใจ bid, offer, การดึง, การเติม และการชน",
            "แยกแรงจริงออกจากแรงโชว์",
            "ใช้ order flow เพื่อช่วย timing โดยไม่ลืมภาพใหญ่",
        ],
        "keywords": ["bid", "offer", "กระดาน", "แรงซื้อ", "แรงขาย", "เติม", "ดึง"],
        "practice": "ดูกระดาน 30 นาทีแล้วจดเหตุการณ์ bid/offer ที่สัมพันธ์กับราคาขยับจริง 10 เหตุการณ์",
    },
    14: {
        "slug": "14_volume_wyckoff",
        "title": "Volume Analysis + Wyckoff",
        "phase": "อ่านเกมสะสมและแจกจ่าย",
        "category": "Volume",
        "thesis": "Wyckoff ช่วยเล่าเรื่องระหว่างราคา volume และผู้เล่นใหญ่ ทำให้เห็น phase ของการสะสม ไล่ราคา และแจกจ่าย",
        "objectives": [
            "เข้าใจ accumulation, markup, distribution, markdown",
            "อ่าน volume เทียบตำแหน่งราคา",
            "มองกราฟเป็นเรื่องราว ไม่ใช่แท่งเทียนแยกกัน",
        ],
        "keywords": ["Wyckoff", "volume", "สะสม", "แจกจ่าย", "แรง", "ราคา", "phase"],
        "practice": "หา chart 1 ตัวที่มีช่วงสะสมชัด แล้ว label phase พร้อมเหตุผลจาก volume",
    },
    15: {
        "slug": "15_volume_analysis",
        "title": "Volume Analysis",
        "phase": "อ่านหลักฐานของแรง",
        "category": "Volume",
        "thesis": "Volume คือหลักฐานของความจริงจัง แต่ความหมายของ volume เปลี่ยนตามตำแหน่งราคาและบริบทของแนวโน้ม",
        "objectives": [
            "อ่าน volume สูง/ต่ำในบริบทต่างกัน",
            "แยกแรงซื้อจริง แรงขายจริง และแรงหมด",
            "ใช้ volume ยืนยันหรือปฏิเสธ price action",
        ],
        "keywords": ["volume", "แรงซื้อ", "แรงขาย", "ราคา", "เบรก", "ยืนยัน", "หลอก"],
        "practice": "ทำตารางตัวอย่าง volume 4 แบบ: ขึ้นพร้อม vol, ขึ้นไร้ vol, ลงพร้อม vol, ลงไร้ vol แล้วตีความ",
    },
    16: {
        "slug": "16_financial_statement",
        "title": "ศิลปะการแกะงบหาหุ้น",
        "phase": "อ่านคุณภาพกิจการ",
        "category": "Fundamental",
        "thesis": "งบการเงินช่วยให้เห็นคุณภาพกิจการ ความสามารถทำกำไร หนี้ กระแสเงินสด และ story ที่ราคาอาจกำลังสะท้อน",
        "objectives": [
            "อ่านงบเพื่อหาคุณภาพ ไม่ใช่แค่ตัวเลขสวย",
            "เชื่อมรายได้ กำไร หนี้ และ cash flow",
            "ใช้ fundamental เป็นฐานของ conviction ก่อนเพิ่มน้ำหนัก",
        ],
        "keywords": ["งบ", "กำไร", "รายได้", "หนี้", "กระแสเงินสด", "หุ้น", "กิจการ"],
        "practice": "เลือกหุ้นหนึ่งตัวแล้วสรุป 5 บรรทัด: รายได้โตไหม กำไรจริงไหม หนี้หนักไหม cash flow ดีไหม story คืออะไร",
    },
    17: {
        "slug": "17_basic_technical_2",
        "title": "Basic Technical 2",
        "phase": "ต่อยอดภาษาเทคนิค",
        "category": "Technical",
        "thesis": "Technical ที่ดีคือการอ่าน context ของราคา ไม่ใช่การเพิ่ม indicator จนมองไม่เห็นพฤติกรรมตลาด",
        "objectives": [
            "ต่อยอดจากแนวโน้ม แนวรับ แนวต้าน และ pattern",
            "ใช้เครื่องมือเพื่อช่วยตัดสินใจ ไม่ใช่แทนการคิด",
            "เชื่อม technical กับ strategy และ risk",
        ],
        "keywords": ["technical", "กราฟ", "แนวรับ", "แนวต้าน", "trend", "pattern", "indicator"],
        "practice": "เปิดกราฟเปล่าแล้วมาร์ก structure ก่อน จากนั้นค่อยใส่ indicator แล้วดูว่าเพิ่มคุณค่าจริงหรือไม่",
    },
    18: {
        "slug": "18_basic_technical_1",
        "title": "Basic Technical 1",
        "phase": "พื้นฐานการอ่านกราฟ",
        "category": "Technical",
        "thesis": "ก่อนใช้เครื่องมือซับซ้อน ต้องอ่านราคา แนวโน้ม จุดกลับตัว และโครงสร้างตลาดให้เป็นภาษาพื้นฐานก่อน",
        "objectives": [
            "เข้าใจ price structure เบื้องต้น",
            "อ่านแนวโน้ม แนวรับ แนวต้าน และ momentum",
            "วางพื้นฐานสำหรับ volume, wave และ strategy",
        ],
        "keywords": ["basic", "technical", "กราฟ", "แนวโน้ม", "แนวรับ", "แนวต้าน", "ราคา"],
        "practice": "เลือกกราฟ 20 ตัวแล้วตอบ 3 คำถาม: trend คืออะไร จุดผิดทางอยู่ไหน มีจุดเข้าไหม",
    },
    19: {
        "slug": "19_strategist_analysis",
        "title": "การวิเคราะห์หุ้นในแบบฉบับนักกลยุทธ์",
        "phase": "คิดเป็น scenario",
        "category": "Strategy",
        "thesis": "นักกลยุทธ์มองหุ้นเป็นหลาย scenario แล้วเลือกแผนที่คุ้มที่สุดตามข้อมูล ไม่ใช่ถามแค่ว่าหุ้นจะขึ้นหรือลง",
        "objectives": [
            "สร้าง bullish/base/bearish scenario",
            "เชื่อม technical, volume, fundamental และ timing",
            "ตัดสินใจจากความคุ้มค่า ไม่ใช่ความมั่นใจ",
        ],
        "keywords": ["กลยุทธ์", "วิเคราะห์", "scenario", "หุ้น", "แผน", "ความเสี่ยง", "โอกาส"],
        "practice": "ทำ scenario 3 แบบให้หุ้นหนึ่งตัว พร้อม trigger ที่ทำให้เปลี่ยนแผน",
    },
    20: {
        "slug": "20_account_streaming_efin",
        "title": "การเปิดบัญชีซื้อขายหลักทรัพย์ Streaming EFin",
        "phase": "เตรียมเครื่องมือ",
        "category": "Tools",
        "thesis": "เครื่องมือที่พร้อมทำให้การฝึกไม่สะดุด แต่เครื่องมือเป็นเพียงฐานปฏิบัติ ต้องถูกผูกกับระบบเรียนและระบบเทรด",
        "objectives": [
            "รู้เครื่องมือพื้นฐานสำหรับซื้อขายและดูข้อมูล",
            "จัด workspace ให้พร้อมฝึกตามบทเรียน",
            "ลด friction ระหว่างการเรียนกับการลงมือจริง",
        ],
        "keywords": ["บัญชี", "Streaming", "EFin", "เปิดบัญชี", "เครื่องมือ", "ซื้อขาย", "หลักทรัพย์"],
        "practice": "จัดหน้าจอเรียน 3 ส่วน: กราฟ, กระดาน/ข้อมูล, journal แล้วบันทึก template การใช้งาน",
    },
}


STOP_WORDS = {
    "ครับ", "ค่ะ", "นะ", "คือ", "ก็", "แล้ว", "ว่า", "ใน", "ของ", "ที่", "จะ", "เรา", "ผม",
    "มัน", "เป็น", "ได้", "ให้", "กับ", "มี", "ไม่", "ไป", "มา", "นี้", "นั้น", "เลย", "แบบ",
}


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def compact_lines(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return lines


def chunk_lines(lines: list[str], max_chars: int = 1400) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for line in lines:
        if current and size + len(line) > max_chars:
            chunks.append(" ".join(current))
            current = []
            size = 0
        current.append(line)
        size += len(line) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks


def extract_keyword_passages(chunks: list[str], keywords: list[str], limit: int = 5) -> list[str]:
    scored: list[tuple[int, int, str]] = []
    for i, chunk in enumerate(chunks):
        lowered = chunk.lower()
        score = sum(lowered.count(keyword.lower()) for keyword in keywords)
        if score:
            scored.append((score, -i, chunk))
    scored.sort(reverse=True)
    return [shorten_passage(item[2]) for item in scored[:limit]]


def shorten_passage(text: str, limit: int = 420) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def top_terms(text: str, keywords: list[str]) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z+/-]*|[ก-๙]{3,}", text.lower())
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    counts = Counter(words)
    for keyword in keywords:
        if keyword.lower() in text.lower():
            counts[keyword] += 8
    return [word for word, _ in counts.most_common(16)]


def parse_index(path: Path) -> int:
    match = re.match(r"(\d{3})_", path.name)
    if not match:
        raise ValueError(f"Cannot parse lesson index from {path.name}")
    return int(match.group(1))


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def build_lesson_markdown(lesson: dict, transcript_name: str, terms: list[str], passages: list[str], chunk_count: int) -> str:
    passage_md = "\n\n".join(f"> {passage}" for passage in passages) if passages else "> ยังไม่พบ passage ที่ตรง keyword โดยตรง ต้องอ่าน transcript เพิ่ม"
    review_questions = [
        f"แก่นของบท '{lesson['title']}' คืออะไร ถ้าต้องอธิบายให้คนไม่เคยเรียนหุ้นฟังใน 3 นาที?",
        "ความรู้นี้เชื่อมกับ risk, strategy หรือ execution อย่างไร?",
        "ถ้าจะเอาไปใช้กับกราฟจริงวันนี้ ต้องดูหลักฐานอะไรบ้าง?",
    ]
    return f"""# {lesson['title']}

## บทบาทของบทนี้
- Phase: {lesson['phase']}
- Category: {lesson['category']}
- Source transcript: `{transcript_name}`
- Transcript chunks: {chunk_count}

## แก่นความรู้ที่ตกผลึก
{lesson['thesis']}

## เป้าหมายการเรียน
{markdown_list(lesson['objectives'])}

## คำสำคัญที่ต้องจำ
{", ".join(terms)}

## หลักฐานจาก transcript
{passage_md}

## วิธีเรียนบทนี้ให้เข้าหัว
1. อ่านแก่นความรู้ก่อนหนึ่งรอบ
2. อ่าน passage จาก transcript แล้วขีดเส้นใต้คำที่เกี่ยวกับ `{lesson['category']}`
3. สรุปด้วยภาษาตัวเอง 5 บรรทัด
4. ทำแบบฝึกท้ายบทด้วยกราฟหรือหุ้นจริง

## แบบฝึก
{lesson['practice']}

## คำถามทบทวน
{markdown_list(review_questions)}

## เชื่อมไปบทอื่น
- ก่อนหน้า/พื้นฐาน: ใช้บท mindset และ risk เป็นกรอบ ไม่ให้เข้าใจเครื่องมือแบบแยกส่วน
- ต่อไป/ประยุกต์: นำบทนี้ไปประกอบกับ volume, strategy และ execution เพื่อสร้างระบบของตัวเอง
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    LESSONS_OUT.mkdir(parents=True, exist_ok=True)

    transcript_files = sorted(TRANSCRIPTS.glob("*.txt"), key=parse_index)
    all_chunks = []
    lessons_index = []

    for path in transcript_files:
        index = parse_index(path)
        lesson = LESSON_GUIDE[index]
        text = clean_text(path.read_text(encoding="utf-8"))
        lines = compact_lines(text)
        chunks = chunk_lines(lines)
        terms = top_terms(text, lesson["keywords"])
        passages = extract_keyword_passages(chunks, lesson["keywords"])

        lesson_path = LESSONS_OUT / f"{lesson['slug']}.md"
        lesson_path.write_text(
            build_lesson_markdown(lesson, path.name, terms, passages, len(chunks)),
            encoding="utf-8",
        )

        lessons_index.append({
            "index": index,
            "slug": lesson["slug"],
            "title": lesson["title"],
            "phase": lesson["phase"],
            "category": lesson["category"],
            "transcript": str(path.relative_to(ROOT)).replace("\\", "/"),
            "lesson_file": str(lesson_path.relative_to(ROOT)).replace("\\", "/"),
            "chunk_count": len(chunks),
            "keywords": terms,
            "thesis": lesson["thesis"],
        })

        for chunk_index, chunk in enumerate(chunks, start=1):
            all_chunks.append({
                "id": f"{index:03d}-{chunk_index:04d}",
                "lesson_index": index,
                "lesson_title": lesson["title"],
                "category": lesson["category"],
                "chunk_index": chunk_index,
                "chunk_count": len(chunks),
                "text": chunk,
            })

    (OUT / "lessons_index.json").write_text(
        json.dumps(lessons_index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT / "chunks.json").write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    curriculum = build_curriculum_markdown(lessons_index, all_chunks)
    (OUT / "curriculum_map.md").write_text(curriculum, encoding="utf-8")
    (OUT / "teaching_plan.md").write_text(build_teaching_plan(), encoding="utf-8")
    (OUT / "README.md").write_text(build_readme(len(transcript_files), len(all_chunks)), encoding="utf-8")


def build_curriculum_markdown(lessons_index: list[dict], all_chunks: list[dict]) -> str:
    phases = []
    for item in lessons_index:
        phases.append(f"| {item['index']} | {item['phase']} | {item['category']} | [{item['title']}](lessons/{item['slug']}.md) |")

    learning_route = [
        "1. Mindset: ตั้งเป้าหมายและเหตุผลส่วนตัวก่อนเรียนเครื่องมือ",
        "2. Risk: รู้ว่าผิดแล้วเสียเท่าไร และหยุดเมื่อไร",
        "3. Technical: อ่านโครงสร้างราคาโดยไม่จมกับ indicator",
        "4. Volume/Order Flow: อ่านแรงจริง แรงหลอก และพฤติกรรมผู้เล่น",
        "5. Fundamental: สร้าง thesis และ conviction จากกิจการ",
        "6. Strategy: ประกอบทุกอย่างเป็นระบบเข้าออกและการทบทวน",
        "7. Execution: ฝึกลงมือจริงด้วย routine, journal และวินัย",
    ]

    return f"""# The Legend Curriculum Map

ไฟล์นี้คือแผนที่เรียนจาก transcript ทั้งหมด โดยจัดให้เนื้อหาแตกฉานขึ้นจากคลิปเดิมที่กระจายอยู่หลายตอน

## ภาพรวม
- จำนวนบทเรียน: {len(lessons_index)}
- จำนวน transcript chunks ใหม่: {len(all_chunks)}
- Source of truth: `transcripts/*.txt`
- เป้าหมาย: ไม่ให้ผู้เรียนต้องกลับไปดูวิดีโอเอง แต่มีบทเรียนข้อความที่อ่าน ฝึก ทบทวน และโยงกันได้

## เส้นทางเรียนที่แนะนำ
{chr(10).join(learning_route)}

## ตารางบทเรียน
| บท | Phase | Category | Lesson |
|---:|---|---|---|
{chr(10).join(phases)}

## โครงสร้างความรู้
- Mindset: บท 1, 2, 7
- Risk: บท 3
- Technical: บท 12, 17, 18
- Volume/Order Flow: บท 13, 14, 15
- Fundamental: บท 9, 16
- Strategy: บท 4, 6, 11, 19
- Execution/Tools: บท 5, 8, 10, 20

## วิธีใช้ฐานความรู้นี้
1. อ่าน `curriculum_map.md` เพื่อเห็นภาพรวม
2. อ่านไฟล์บทเรียนใน `knowledge/lessons/`
3. ใช้ `knowledge/chunks.json` เป็นฐานข้อมูลสำหรับทำ search, flashcard, quiz หรือ RAG ต่อ
4. ทุกครั้งหลังอ่าน ให้ตอบ 3 คำถาม: รู้อะไร, ใช้อย่างไร, เสี่ยงตรงไหน
"""


def build_readme(lesson_count: int, chunk_count: int) -> str:
    return f"""# The Legend Knowledge Base

สร้างจาก transcript ภาษาไทยที่อ่านถูกใน `transcripts/*.txt`

## Output
- `curriculum_map.md`: แผนที่หลักสูตรและลำดับเรียน
- `lessons_index.json`: metadata ของบทเรียนทั้งหมด
- `chunks.json`: transcript chunks ภาษาไทยสำหรับค้นหา/ทำระบบเรียน
- `teaching_plan.md`: วิธีสอนและลำดับการย่อยความรู้ให้เข้าหัว
- `lessons/*.md`: บทเรียนตกผลึกรายคลิป

## Count
- Lessons: {lesson_count}
- Chunks: {chunk_count}

## Next Step
นำ `lessons_index.json` และ `chunks.json` ไปผูกกับเว็บแอพ เพื่อให้หน้าเว็บไม่ใช่แค่ roadmap แต่เป็นระบบเรียนจากเนื้อหาจริง
"""


def build_teaching_plan() -> str:
    return """# Teaching Plan: จะสอน The Legend ให้เข้าหัวอย่างไร

เป้าหมายไม่ใช่ให้จำ transcript ได้ทั้งก้อน แต่ให้เปลี่ยน transcript เป็นระบบคิดที่ใช้ตัดสินใจในตลาดจริงได้

## หลักการสอน
1. เริ่มจากภาพใหญ่ก่อนเครื่องมือ: ถ้ายังไม่รู้ว่าเล่นเกมอะไรอยู่ indicator จะยิ่งทำให้หลง
2. ทุกบทต้องตอบ 3 คำถาม: รู้อะไร, ใช้อย่างไร, เสี่ยงตรงไหน
3. แยกความรู้เป็นชั้น: Mindset, Risk, Technical, Volume, Fundamental, Strategy, Execution
4. ไม่สอนแบบดูคลิปตามลำดับอย่างเดียว แต่สอนแบบโยงความรู้ที่ปรบเปรอกันให้กลายเป็นระบบเดียว
5. ทุกบทต้องมีแบบฝึกจากกราฟหรือหุ้นจริง ไม่ใช่อ่านแล้วจบ

## ลำดับการเรียนที่ผมจะใช้สอน

### Phase 1: ตั้งระบบคิดและเป้าหมาย
- บท 1: Way to Financial Freedom
- บท 7: Money Game
- บท 2: เคล็ดลับการเทรดแบบ เบียร์ วนนท์

ผลลัพธ์ที่ต้องได้: คุณต้องตอบได้ว่าเรียนหุ้นไปเพื่ออะไร จะโตแบบไหน และอะไรคือพฤติกรรมที่ต้องสร้าง

### Phase 2: รอดก่อนรวย
- บท 3: สูตรปั้นพอร์ตอย่างปลอดภัย
- บท 5: Prop Trade Professional

ผลลัพธ์ที่ต้องได้: มีกรอบ risk, stop, routine และเงื่อนไขหยุดเทรด

### Phase 3: อ่านภาษาแรกของตลาด
- บท 18: Basic Technical 1
- บท 17: Basic Technical 2
- บท 12: Elliott Wave + Fibonacci

ผลลัพธ์ที่ต้องได้: อ่าน trend, structure, key level, scenario และจุดผิดทางได้

### Phase 4: อ่านแรงเบื้องหลังราคา
- บท 15: Volume Analysis
- บท 14: Volume Analysis + Wyckoff
- บท 13: Bid Offer Analysis

ผลลัพธ์ที่ต้องได้: แยกแรงจริง แรงหลอก การสะสม แจกจ่าย และ order flow เบื้องต้นได้

### Phase 5: สร้าง conviction จากกิจการ
- บท 16: ศิลปะการแกะงบหาหุ้น
- บท 9: All in ด้วย Fundamental

ผลลัพธ์ที่ต้องได้: เขียน thesis ได้ว่าหุ้นดีเพราะอะไร ผิดเมื่อไร และควรให้น้ำหนักแค่ไหน

### Phase 6: ประกอบเป็นกลยุทธ์
- บท 4: เทรดหุ้น SET100
- บท 6: Swing Trade
- บท 11: Trading Strategy
- บท 19: วิเคราะห์หุ้นแบบนักกลยุทธ์

ผลลัพธ์ที่ต้องได้: มี strategy card ที่ตอบ entry, exit, stop, target, sizing และ no-trade condition

### Phase 7: ลงมือจริงและทบทวน
- บท 8: Scalper
- บท 10: อ่านใจเจ้ามือแบบ Day Trade
- บท 20: Streaming / EFin

ผลลัพธ์ที่ต้องได้: มีหน้าจอฝึก, journal, replay routine และวิธีวัดผลจากไม้จริง

## รูปแบบบทเรียนที่ควรสร้างในเว็บแอพ
1. Lesson Brief: สรุปแก่นบทเรียน 1 หน้า
2. Deep Lesson: บทเรียนเต็มจาก transcript ที่ตกผลึกแล้ว
3. Source Evidence: passage จาก transcript ที่ใช้รองรับบทเรียน
4. Flashcard: คำถามจำแก่น
5. Scenario Quiz: คำถามแบบสถานการณ์ ไม่ใช่ถามจำคำ
6. Practice Journal: แบบฝึกที่ให้คุณตอบและเก็บประวัติ
7. Mastery Map: ดูว่าความรู้แต่ละแกนเชื่อมกันอย่างไร

## วิธีวัดว่าคุณเข้าใจจริง
- อธิบายแนวคิดได้โดยไม่ใช้ศัพท์เยอะ
- เปิดกราฟแล้วชี้หลักฐานที่สอดคล้องกับบทเรียนได้
- บอกจุดที่ตัวเองอาจผิดได้ก่อนเข้าเทรด
- เขียนแผนเข้าออกเป็นขั้นตอน ไม่ใช่แค่รู้สึกว่าหุ้นน่าขึ้น
- หลังเทรดแล้วทบทวนได้ว่าแพ้เพราะระบบผิด วินัยผิด หรือสภาวะตลาดไม่เหมาะ

## สิ่งที่ต้องทำต่อจากฐานข้อมูลนี้
1. ทำบทเรียนรายบทให้ลึกขึ้นจาก `knowledge/chunks.json`
2. สร้าง flashcard และ quiz จากบทเรียนจริง ไม่ใช่จากชื่อบท
3. ผูกฐานความรู้เข้าเว็บแอพเพื่อค้นหาและเรียนแบบเป็นขั้น
4. ทำระบบ journal ให้คุณตอบแบบฝึกและย้อนดูพัฒนาการ
"""


if __name__ == "__main__":
    main()
