from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "knowledge" / "mindmaps"
OUT_HTML = ROOT / "mindmap_pages"
LESSON_DIR = ROOT / "knowledge" / "lessons"


MINDMAPS = [
    {
        "slug": "01_way_to_financial_freedom",
        "title": "สร้างพอร์ต 300 เท่า / Way to Financial Freedom",
        "central": "Technical เป็นเพียงส่วนหนึ่งของเกม อิสรภาพทางการเงินต้องเริ่มจากเป้าหมายชีวิต เวลา ระบบคิด risk/reward และการอยู่รอดครบ market cycle",
        "branches": [
            ("เหตุผลชีวิต", ["เวลาหาเงินมีจำกัด", "ไม่อยากเป็นทาสของเงิน", "ต้องมีเงินพอ support คนที่รัก", "ใช้ชีวิตในแบบที่ต้องการ"]),
            ("ตัวเลขอิสรภาพ", ["นิยาม 1 ล้านดอลลาร์", "ประมาณ 30 ล้านบาท", "ผลตอบแทนปลอดภัย 3 เปอร์เซ็นต์", "ค่าใช้จ่ายจริงขึ้นกับครอบครัว"]),
            ("เส้นทางสร้างพอร์ต", ["เริ่มจากเงินหลักแสน", "เฝ้าหน้าจอเอง", "อ่าน ticker และ bid offer", "จากกำไรเร็วสู่พอร์ตแตก"]),
            ("แก่นการเทรด", ["โดนให้น้อย", "ได้ให้หนัก", "ถูกทางค่อยเพิ่ม", "ผิดทางคืนเร็ว"]),
            ("ระบบความรู้", ["Macro", "Fundamental", "Technical", "Volume", "Psychology"]),
            ("Market Cycle", ["Super bull ต้องโกย", "Uptrend ถือ trend", "Sideway เล่นกรอบ", "ต้มกบเลือก outperform", "Crash พอร์ตควรว่าง"]),
        ],
        "destination": "เลิกถามแค่ว่าหุ้นตัวไหนดี แล้วถามว่าอยู่สนามไหน เงินก้อนนี้ทำหน้าที่อะไร ถ้าผิดเสียเท่าไร และ trade นี้พาเข้าใกล้อิสรภาพจริงไหม",
    },
    {
        "slug": "02_beer_wanon_trading",
        "title": "เคล็ดลับการเทรดในแบบ เบียร์ วนนท์",
        "central": "การเทรดแบบมืออาชีพไม่ได้เกิดจากสูตรเดียว แต่เกิดจากการสังเกตซ้ำ ตกผลึกเป็นระบบของตัวเอง และไม่หลอกตัวเองเวลาแพ้",
        "branches": [
            ("ตัวตนเทรดเดอร์", ["รู้ว่าตัวเองถนัดอะไร", "ไม่ copy คนอื่นทั้งดุ้น", "ยอมรับนิสัยตัวเอง", "สร้างระบบที่เข้ากับตัวเอง"]),
            ("วงจรชีวิตเทรดเดอร์", ["เริ่มจากกำไรง่าย", "มึนงง", "พอร์ตเสียหาย", "ตกผลึก", "ประคองตัว", "พุ่ง"]),
            ("Survivor Mindset", ["ก่อนโตต้องรอด", "ผิดต้องล้างหน้าไพ่", "อย่าสวนสงครามที่ไม่มีวันชนะ", "คิดถึงครอบครัวก่อนเสี่ยง"]),
            ("Focus", ["ไม่ต้องเก่งทุกแบบ", "เลือกสนามที่ถนัด", "ทำซ้ำจนเห็น pattern", "ไม่เปรียบเทียบกับคนอื่น"]),
            ("Journal", ["บันทึกเหตุผลเข้า", "บันทึกอารมณ์", "บันทึกผลลัพธ์", "แยก system error กับ mindset error"]),
        ],
        "destination": "เอาประสบการณ์คนอื่นมาเป็นกระจก แล้วสร้าง trading identity ของตัวเอง ไม่ใช่เป็นเงาของใคร",
    },
    {
        "slug": "03_safe_portfolio_growth",
        "title": "สูตรปั้นพอร์ตอย่างปลอดภัย",
        "central": "การปั้นพอร์ตที่แท้จริงคือการโตโดยไม่ตายก่อน ต้องคุม downside ก่อนเร่ง upside",
        "branches": [
            ("รอดก่อนรวย", ["รักษาทุนคือเงื่อนไขแรก", "พอร์ตเล็กพลาดได้แต่ต้องไม่หมด", "พอร์ตใหญ่ต้องยิ่งคุมวงเสียหาย"]),
            ("Risk Rule", ["รู้ risk per trade", "รู้ max loss ต่อวัน", "รู้ max drawdown", "มีจุดหยุดพัก"]),
            ("Position Sizing", ["ไม่ลงเท่ากันทุกไม้", "เพิ่มเมื่อถูกทาง", "ลดเมื่อสภาวะไม่ชัด", "ไม่ average down แบบไร้แผน"]),
            ("Circuit Breaker", ["เสียระดับแรกพัก", "เสียหนักลด size", "เสียถึงขีดต้องหยุด", "กลับมา paper trade ได้"]),
            ("Growth Engine", ["กำไรค่อย compound", "อย่าเร่งตอนตลาดไม่ให้", "รอช่วงที่ edge ชัด", "โตจาก process ไม่ใช่ดวง"]),
        ],
        "destination": "มีระบบที่ทำให้พอร์ตโตได้โดยยังอยู่ในเกม แม้เจอช่วงผิดทางหลายครั้ง",
    },
    {
        "slug": "04_set100_strategy",
        "title": "เทรดหุ้น SET100 ยังไงให้ได้หลักล้าน",
        "central": "หุ้นใหญ่ให้สนามที่มีสภาพคล่องและโครงสร้างชัด แต่ต้องเลือกตัวที่มีแรงและรอบ ไม่ใช่ซื้อเพราะใหญ่เฉย ๆ",
        "branches": [
            ("สนาม SET100", ["สภาพคล่องสูง", "เหมาะกับเงินก้อนใหญ่ขึ้น", "มี institutional flow", "แต่ไม่ใช่ทุกตัวน่าเล่น"]),
            ("การคัดหุ้น", ["ดู trend", "ดู volume", "ดู sector", "ดู relative strength"]),
            ("จังหวะเข้า", ["รอ breakout", "รอ pullback", "รอฐานชัด", "ไม่ไล่ปลายรอบ"]),
            ("การถือ", ["ถือเมื่อ trend ยังอยู่", "ขายเมื่อเสียทรง", "ไม่ถือหุ้นใหญ่ที่เป็นขาลง", "แบ่งไม้ตามแผน"]),
            ("เป้าหมายหลักล้าน", ["ต้องใช้ size ที่เหมาะ", "ต้องคุม downside", "ต้องเล่นรอบใหญ่", "ต้องมี patience"]),
        ],
        "destination": "ใช้ SET100 เป็นสนามเทรดที่มีวินัย เลือกเฉพาะตัวที่มีแรงและแผน ไม่ใช่สะสมทุกตัวที่ดูปลอดภัย",
    },
    {
        "slug": "05_prop_trade_professional",
        "title": "Prop Trade Professional",
        "central": "Prop trader คิดเป็น process และสถิติ ไม่คิดเป็นไม้เดียว ต้องมีวินัยก่อน ระหว่าง และหลัง trade",
        "branches": [
            ("Professional Mind", ["ไม่เทรดตามอารมณ์", "วัดผลเป็นชุด", "คิด probabilistic", "แพ้ได้แต่ต้องแพ้ตามระบบ"]),
            ("Daily Routine", ["เตรียมตลาด", "เลือก watchlist", "ตั้ง scenario", "กำหนด no trade condition"]),
            ("Execution", ["เข้าเมื่อ trigger ชัด", "ไม่ไล่ราคา", "ตัดสินใจตามแผน", "จัดการ slippage"]),
            ("Review", ["สรุปหลังตลาด", "ดู hit rate", "ดู RRR", "หา error ซ้ำ"]),
            ("Risk Desk", ["จำกัด loss", "จำกัดจำนวนไม้", "ลด size เมื่อหลุดวินัย", "หยุดเมื่อสภาพจิตไม่พร้อม"]),
        ],
        "destination": "เปลี่ยนจากคนอยากชนะรายไม้ เป็น operator ที่ทำตาม process ซ้ำจน edge แสดงผล",
    },
    {
        "slug": "06_swing_trade",
        "title": "Swing Trade Professional Trader",
        "central": "Swing trade คือการจับรอบที่ราคา โครงสร้าง และแรงสนับสนุนอยู่ข้างเดียวกัน แล้วถือให้พอดีกับรอบ",
        "branches": [
            ("ภาพรอบ", ["ดู timeframe ใหญ่", "หา trend", "หา key level", "แยกพักตัวกับกลับตัว"]),
            ("Setup", ["breakout", "pullback", "ฐานสะสม", "higher low"]),
            ("Timing", ["รอ trigger", "ไม่ซื้อกลางทาง", "ดู volume ยืนยัน", "ดูตลาดรวม"]),
            ("Holding", ["ถือจนเสีย trend", "ไม่รีบขายเพราะแกว่งเล็ก", "เลื่อน stop ตาม structure", "แบ่งขายตามเป้า"]),
            ("Risk Reward", ["stop ต้องชัด", "target ต้องคุ้ม", "ไม่เข้าเมื่อ reward ไม่พอ", "ไม่ถือถ้าผิด thesis"]),
        ],
        "destination": "มี playbook สำหรับจับรอบหลายวันถึงหลายสัปดาห์ โดยไม่กลายเป็นติดดอยระยะยาว",
    },
    {
        "slug": "07_money_game",
        "title": "Money Game บ้านหนึ่งหลัง รถสองคัน",
        "central": "เงินไม่ใช่แค่ตัวเลขในพอร์ต แต่เป็นเครื่องมือสร้างชีวิตที่ต้องการ เป้าหมายต้องแปลงเป็นระบบลงมือ",
        "branches": [
            ("ภาพชีวิต", ["บ้าน", "รถ", "ครอบครัว", "อิสระ", "คุณภาพชีวิต"]),
            ("ตัวเลขเป้าหมาย", ["ต้องใช้เงินเท่าไร", "ต้องมี cashflow เท่าไร", "ต้องใช้เวลานานแค่ไหน", "ต้องได้ผลตอบแทนเท่าไร"]),
            ("แผนพอร์ต", ["ทุนตั้งต้น", "เงินเติม", "ผลตอบแทนเป้าหมาย", "drawdown ที่รับได้"]),
            ("พฤติกรรม", ["ประหยัดในสิ่งไม่จำเป็น", "ลงทุนในสิ่งเพิ่ม edge", "ไม่ใช้เงินเกินตัว", "ไม่หลง lifestyle"]),
            ("สมดุลชีวิต", ["สุขภาพ", "ครอบครัว", "งาน", "การเรียน", "การเทรด"]),
        ],
        "destination": "ทำให้เป้าหมายการเงินมีหน้าตาเป็นชีวิตจริง แล้วใช้พอร์ตเป็นเครื่องมือ ไม่ใช่ปล่อยให้พอร์ตกลายเป็นเจ้าของชีวิต",
    },
    {
        "slug": "08_scalper",
        "title": "Scalper เทรดสั้น ปั้นพอร์ต",
        "central": "Scalping เป็นเกมของความเร็ว ความชัด และการยอมผิดทันที ต้องเอา process ชนะ impulse",
        "branches": [
            ("ธรรมชาติ scalping", ["เวลาสั้น", "กำไรต่อไม้เล็ก", "ผิดต้องออกเร็ว", "ค่าคอมและ slippage สำคัญ"]),
            ("ข้อมูลที่อ่าน", ["ticker", "bid offer", "volume", "แรงซื้อขาย", "จังหวะตลาด"]),
            ("Setup", ["momentum burst", "breakout สั้น", "pullback เร็ว", "stop hunt"]),
            ("Execution", ["เข้าเมื่อ trigger มา", "ไม่ลังเล", "ไม่ไล่เมื่อพลาด", "ไม่เฉลี่ยมั่ว"]),
            ("Mindset", ["ไม่เอาคืน", "ไม่ overtrade", "หยุดเมื่อหลุดวินัย", "ยอมพลาดโอกาส"]),
        ],
        "destination": "ฝึกความเฉียบของการตัดสินใจ โดยมีกฎออกชัดกว่าความอยากชนะ",
    },
    {
        "slug": "09_all_in_fundamental",
        "title": "วิธีการ All in ด้วย Fundamental",
        "central": "All in ที่ดีไม่ใช่ความกล้า แต่คือ conviction ที่มี thesis, catalyst, timing และ invalidation ครบ",
        "branches": [
            ("Thesis", ["กิจการดีเพราะอะไร", "รายได้โตไหม", "กำไรจริงไหม", "story ใหญ่คืออะไร"]),
            ("Catalyst", ["ผลประกอบการ", "อุตสาหกรรม", "นโยบาย", "การเปลี่ยนโครงสร้างธุรกิจ"]),
            ("Valuation", ["ถูกหรือแพง", "เทียบอดีต", "เทียบคู่แข่ง", "margin of safety"]),
            ("Timing", ["technical ยืนยัน", "volume สนับสนุน", "ตลาดรวมไม่ต้าน", "ไม่รีบก่อน trigger"]),
            ("Risk", ["thesis ผิดเมื่อไร", "ตัดเมื่อไร", "ขนาด position เท่าไร", "ข่าวไหนต้องทบทวน"]),
        ],
        "destination": "กล้าเพิ่มน้ำหนักเฉพาะเมื่อรู้ทั้งเหตุผลที่จะชนะและเงื่อนไขที่ต้องยอมรับว่าผิด",
    },
    {
        "slug": "10_day_trade_operator",
        "title": "อ่านใจเจ้ามือแบบ Day Trade",
        "central": "การอ่านเจ้ามือคืออ่านร่องรอย supply demand และ trap ในวัน ไม่ใช่เดาใจคน",
        "branches": [
            ("ภาพวัน", ["ตลาดเปิด", "ช่วงพัก", "บ่าย", "ก่อนปิด", "sentiment เปลี่ยน"]),
            ("ร่องรอยแรง", ["volume spike", "bid offer", "ticker", "ยืนราคา", "หลุดแล้วกลับ"]),
            ("Trap", ["หลอก breakout", "sweep stop", "ลากแล้วทุบ", "กดให้ขาย"]),
            ("Confirmation", ["ผ่านแนวต้านแล้วรับได้", "volume ตาม", "แรงขายไม่มา", "ตลาดรวมช่วย"]),
            ("Exit", ["ผิดทางออกทันที", "ได้เป้าแบ่งขาย", "หมดแรงไม่ฝืน", "ไม่ถือ day trade กลายเป็น swing โดยไม่ตั้งใจ"]),
        ],
        "destination": "อ่านพฤติกรรมระหว่างวันให้เป็นหลักฐาน เพื่อเลือกเข้าออก ไม่ใช่ปล่อยให้อารมณ์ของแท่งเทียนพาไป",
    },
    {
        "slug": "11_trading_strategy",
        "title": "Trading Strategy",
        "central": "กลยุทธ์ที่ใช้ได้จริงต้องตอบครบว่าเข้าเมื่อไร ออกเมื่อไร ผิดตรงไหน size เท่าไร และ review อย่างไร",
        "branches": [
            ("Setup", ["สภาวะตลาด", "หุ้นที่เลือก", "pattern", "volume", "fundamental support"]),
            ("Trigger", ["ราคาผ่านจุด", "ย่อแล้วรับ", "volume ยืนยัน", "timeframe พร้อมกัน"]),
            ("Risk", ["stop", "position size", "max loss", "no trade condition"]),
            ("Exit", ["target", "trailing stop", "ขายเมื่อเสีย structure", "ขายเมื่อ thesis เปลี่ยน"]),
            ("Review Loop", ["บันทึกก่อนเข้า", "บันทึกหลังออก", "สรุป error", "ปรับทีละจุด"]),
        ],
        "destination": "มี strategy card ที่ทำซ้ำได้ วัดผลได้ และแก้ได้ ไม่ใช่ระบบที่เปลี่ยนตามอารมณ์ตลาด",
    },
    {
        "slug": "12_elliott_wave_fibonacci",
        "title": "Elliott Wave + Fibonacci",
        "central": "Wave และ Fibonacci เป็นแผนที่ scenario ไม่ใช่คำทำนาย ต้องใช้เพื่อวางจุดคุ้มเสี่ยง",
        "branches": [
            ("Wave Structure", ["impulse", "correction", "คลื่นย่อย", "cycle ใหญ่เล็ก"]),
            ("Fibonacci", ["retracement", "extension", "โซนย่อ", "โซนเป้าหมาย"]),
            ("Scenario", ["bull case", "base case", "bear case", "จุด invalidate"]),
            ("Timing", ["รอคลื่นยืนยัน", "ไม่นับคลื่นเพื่อหลอกตัวเอง", "ใช้ volume ช่วย", "ดู timeframe ใหญ่"]),
            ("Risk", ["ถ้านับผิดต้องเสียจำกัด", "ไม่ all in เพราะ wave count", "ให้ราคาพิสูจน์ก่อน"]),
        ],
        "destination": "ใช้ wave/fibo เพื่อจัดความน่าจะเป็นและ risk ไม่ใช่เพื่อทำนายอนาคตแบบมั่นใจเกินจริง",
    },
    {
        "slug": "13_bid_offer_analysis",
        "title": "Bid Offer Analysis",
        "central": "Bid Offer คือข้อมูลใกล้ตลาดที่สุด แต่ต้องอ่านคู่กับราคา volume และ reaction เพราะกระดานถูกจัดฉากได้",
        "branches": [
            ("Bid Offer พื้นฐาน", ["bid หนา", "offer หนา", "เติม", "ดึง", "เคาะ", "โยน"]),
            ("แรงจริงแรงโชว์", ["ตั้งหลอก", "ยกเลิก order", "เคาะจริง", "ยืนราคาได้"]),
            ("ตำแหน่งราคา", ["ใกล้แนวรับ", "ใกล้แนวต้าน", "breakout", "ปลายรอบ"]),
            ("ใช้กับ timing", ["ช่วยเข้า", "ช่วยออก", "ช่วยดู stop hunt", "ช่วยยืนยันแรง"]),
            ("ข้อควรระวัง", ["อย่าอ่านกระดานเดี่ยว ๆ", "ต้องดู ticker", "ต้องดู volume", "ต้องดูภาพใหญ่"]),
        ],
        "destination": "ใช้ bid offer เป็นเลนส์ระยะใกล้ ไม่ใช่เป็นเหตุผลเดียวในการตัดสินใจ",
    },
    {
        "slug": "14_volume_wyckoff",
        "title": "Volume Analysis + Wyckoff",
        "central": "Wyckoff ทำให้เห็น story ของราคา volume และผู้เล่นใหญ่ ว่ากำลังสะสม ไล่ราคา แจกจ่าย หรือเริ่มลง",
        "branches": [
            ("Phase", ["accumulation", "markup", "distribution", "markdown", "reaccumulation"]),
            ("Volume Clue", ["vol สะสม", "vol breakout", "vol ขาย", "vol แห้ง", "effort vs result"]),
            ("ราคาและพฤติกรรม", ["ยืนได้", "หลุดแล้วกลับ", "ขึ้นแต่ vol ไม่ตาม", "ลงแต่แรงขายหมด"]),
            ("คนเล่นใหญ่", ["เก็บของ", "ลากราคา", "ซอยออก", "ออกของไม่หมด"]),
            ("Action", ["เข้าเมื่อ phase ชัด", "เลี่ยง distribution", "ดูจุด invalidation", "ไม่รับมีดเพราะคิดว่าถูก"]),
        ],
        "destination": "อ่านกราฟเป็นเรื่องราว ไม่ใช่แท่งแยกกัน และรู้ว่าเงินใหญ่กำลังทำอะไรกับราคา",
    },
    {
        "slug": "15_volume_analysis",
        "title": "Volume Analysis",
        "central": "Volume คือหลักฐานของความจริงจัง แต่ความหมายขึ้นกับตำแหน่งราคาและบริบทของ trend",
        "branches": [
            ("Volume สูง", ["breakout จริง", "ขายหนัก", "climax", "เปลี่ยนมือ"]),
            ("Volume ต่ำ", ["พักตัว", "ไม่มีคนสนใจ", "แรงหมด", "ก่อนเลือกทาง"]),
            ("เทียบกับราคา", ["ขึ้นพร้อม vol", "ขึ้นไร้ vol", "ลงพร้อม vol", "ลงไร้ vol"]),
            ("ตำแหน่ง", ["ต้นรอบ", "กลางรอบ", "ปลายรอบ", "แนวรับแนวต้าน"]),
            ("Decision", ["ยืนยัน setup", "เตือน trap", "ช่วยถือ", "ช่วยออก"]),
        ],
        "destination": "อ่าน volume เพื่อยืนยันหรือปฏิเสธ price action ไม่ใช่มองแท่ง volume แบบโดด ๆ",
    },
    {
        "slug": "16_financial_statement",
        "title": "ศิลปะการแกะงบหาหุ้น",
        "central": "งบการเงินทำให้เห็นคุณภาพกิจการและความจริงของ story ก่อนเอาเงินไปเชื่อ",
        "branches": [
            ("รายได้", ["โตจริงไหม", "โตจากอะไร", "โตยั่งยืนไหม", "seasonal หรือ one time"]),
            ("กำไร", ["gross margin", "net margin", "ค่าใช้จ่าย", "กำไรพิเศษ"]),
            ("ฐานะการเงิน", ["หนี้", "เงินสด", "ลูกหนี้", "สินค้าคงเหลือ"]),
            ("Cashflow", ["กำไรเป็นเงินสดไหม", "ลงทุนหนักไหม", "เก็บเงินได้ไหม", "ต้องเพิ่มทุนไหม"]),
            ("ใช้กับการเทรด", ["สร้าง thesis", "หา catalyst", "กำหนด invalidation", "เลือกหุ้นที่ตลาดยังไม่เห็น"]),
        ],
        "destination": "ไม่ซื้อเพราะ story สวย แต่ซื้อเมื่อ story งบ และราคามีหลักฐานสนับสนุนกัน",
    },
    {
        "slug": "17_basic_technical_2",
        "title": "Basic Technical 2",
        "central": "Technical ขั้นต่อยอดคือการอ่าน context ของราคา ไม่ใช่สะสม indicator",
        "branches": [
            ("Structure", ["higher high", "higher low", "lower high", "lower low", "ฐานราคา"]),
            ("เครื่องมือ", ["EMA", "MACD", "RSI", "trendline", "แนวรับแนวต้าน"]),
            ("หลาย timeframe", ["ภาพใหญ่", "ภาพกลาง", "จุดเข้า", "อย่าให้ timeframe ขัดกัน"]),
            ("Setup", ["breakout", "pullback", "reversal", "continuation"]),
            ("ข้อควรระวัง", ["indicator lag", "signal หลอก", "อย่าดูเครื่องมือมากกว่าราคา", "ต้องมี stop"]),
        ],
        "destination": "ใช้ technical เป็นภาษาอ่านตลาดและวางแผน ไม่ใช่เป็นเครื่องรางบอกซื้อขาย",
    },
    {
        "slug": "18_basic_technical_1",
        "title": "Basic Technical 1",
        "central": "พื้นฐาน technical คือการอ่านราคา แนวโน้ม แนวรับแนวต้าน และจุดผิดทางก่อนใช้เครื่องมือซับซ้อน",
        "branches": [
            ("ราคา", ["แท่งเทียน", "high low", "แรงซื้อแรงขาย", "พฤติกรรมซ้ำ"]),
            ("แนวโน้ม", ["ขาขึ้น", "ขาลง", "sideway", "เปลี่ยน trend"]),
            ("แนวรับแนวต้าน", ["จุดรับ", "จุดขาย", "break", "false break"]),
            ("จุดเข้าออก", ["เข้าใกล้ risk ต่ำ", "stop ชัด", "target คุ้ม", "ไม่ซื้อกลางอากาศ"]),
            ("พื้นฐานก่อนต่อยอด", ["อ่านกราฟเปล่า", "มาร์ก structure", "ค่อยใส่ indicator", "ฝึกซ้ำหลายกราฟ"]),
        ],
        "destination": "อ่านกราฟเปล่าให้เป็นก่อน แล้วค่อยใช้เครื่องมือเป็นตัวช่วย ไม่ใช่ตัวนำ",
    },
    {
        "slug": "19_strategist_analysis",
        "title": "การวิเคราะห์หุ้นในแบบฉบับนักกลยุทธ์",
        "central": "นักกลยุทธ์ไม่ถามว่าหุ้นจะขึ้นไหม แต่สร้าง scenario แล้วเลือกแผนที่คุ้มที่สุดตามหลักฐาน",
        "branches": [
            ("Scenario Thinking", ["bull", "base", "bear", "trigger ที่เปลี่ยนมุมมอง"]),
            ("ข้อมูลหลายมิติ", ["ตลาดรวม", "sector", "fundamental", "technical", "volume"]),
            ("แผน", ["เข้าเมื่อไร", "ออกเมื่อไร", "ถ้าผิดทำอะไร", "ถ้าถูกเพิ่มไหม"]),
            ("ความคุ้ม", ["reward/risk", "probability", "liquidity", "time cost"]),
            ("การปรับตัว", ["ข้อมูลใหม่", "ราคาไม่ยืนยัน", "thesis พัง", "ตลาดเปลี่ยนสนาม"]),
        ],
        "destination": "คิดเป็นแผนหลายทาง ไม่แต่งเรื่องทางเดียวเพื่อให้ตัวเองกล้าเข้า",
    },
    {
        "slug": "20_account_streaming_efin",
        "title": "การเปิดบัญชีซื้อขายหลักทรัพย์ Streaming EFin",
        "central": "เครื่องมือที่พร้อมทำให้การฝึกไม่สะดุด แต่เครื่องมือไม่ใช่ edge ต้องผูกกับระบบเรียนและระบบเทรด",
        "branches": [
            ("บัญชีซื้อขาย", ["เปิดบัญชี", "ยืนยันตัวตน", "เข้าใช้งาน", "รู้ข้อจำกัด"]),
            ("Streaming", ["ส่งคำสั่ง", "ดูพอร์ต", "ดู bid offer", "ดู ticker"]),
            ("EFin", ["ดูกราฟ", "ดูข้อมูลหุ้น", "scan", "ติดตามข่าว"]),
            ("Workspace", ["กราฟ", "กระดาน", "ข่าว", "journal"]),
            ("วินัยการใช้เครื่องมือ", ["ไม่กดมั่ว", "ตั้ง watchlist", "บันทึกเหตุผล", "ใช้เครื่องมือเพื่อ process"]),
        ],
        "destination": "จัดเครื่องมือให้พร้อมเพื่อฝึกและลงมือจริง แต่ให้ระบบคิดเป็นคนขับ ไม่ใช่หน้าจอเป็นคนสั่ง",
    },
]


def safe_node(text: str) -> str:
    text = re.sub(r"[\n\r\t]+", " ", text)
    text = re.sub(r"[(){}\[\]:;\"'`]", "", text)
    return text.strip()


def lesson_context(item: dict) -> dict:
    path = LESSON_DIR / f"{item['slug']}.md"
    if not path.exists():
        return {"phase": "", "category": "", "goals": [], "keywords": [], "quotes": []}

    text = path.read_text(encoding="utf-8")
    phase = ""
    category = ""
    for line in text.splitlines():
        if line.startswith("- Phase:"):
            phase = line.split(":", 1)[1].strip()
        if line.startswith("- Category:"):
            category = line.split(":", 1)[1].strip()

    def section(name: str) -> str:
        match = re.search(rf"^## {re.escape(name)}\n(.*?)(?=\n## |\Z)", text, re.S | re.M)
        return match.group(1).strip() if match else ""

    goals = [
        line[2:].strip()
        for line in section("เป้าหมายการเรียน").splitlines()
        if line.startswith("- ")
    ]
    keywords = [
        word.strip()
        for word in section("คำสำคัญที่ต้องจำ").replace("\n", " ").split(",")
        if word.strip()
    ][:12]
    quotes = []
    for block in re.findall(r"^> (.*?)(?=\n\n|\Z)", section("หลักฐานจาก transcript"), re.S | re.M):
        cleaned = re.sub(r"\s+", " ", block).strip()
        if len(cleaned) > 260:
            cleaned = cleaned[:260].rsplit(" ", 1)[0] + "..."
        if cleaned:
            quotes.append(cleaned)
        if len(quotes) == 3:
            break

    return {"phase": phase, "category": category, "goals": goals, "keywords": keywords, "quotes": quotes}


def leaf_depth(branch: str, leaf: str) -> list[str]:
    return [
        f"ต้องสังเกตอะไร: {leaf} ต้องถูกมองผ่านตำแหน่งราคา บริบทตลาด และหลักฐานที่เห็นจริง ไม่ใช่จำเป็นคำศัพท์",
        f"ใช้ตอนไหน: ใช้ {leaf} เพื่อช่วยตัดสินใจว่าแผนในกิ่ง {branch} ควรเดินต่อ รอ ย่อขนาด หรือยกเลิก",
        f"ถ้าผิดต้องทำอะไร: ถ้าหลักฐานไม่ยืนยัน {leaf} ให้ลดความมั่นใจทันที และกลับไปถามจุดผิดทางของแผน",
    ]


def branch_rule(branch: str, leaves: list[str]) -> str:
    joined = ", ".join(leaves[:3])
    return f"กิ่งนี้เชื่อมกับบทเรียนหลักเพราะ {branch} เป็นตัวแปลงความรู้ให้กลายเป็นการตัดสินใจ โดยเฉพาะเรื่อง {joined}"


def practice_steps(item: dict, context: dict) -> list[str]:
    first_branch = item["branches"][0][0]
    steps = [
        f"เปิดกราฟหรือกรณีศึกษาจริง 1 ตัว แล้วระบุว่าเกี่ยวกับกิ่ง '{first_branch}' ตรงไหน",
        "เขียนก่อนเข้าว่า thesis คืออะไร หลักฐานคืออะไร และถ้าผิดจะยอมรับตรงไหน",
        "แยกสิ่งที่เห็นจริงออกจากสิ่งที่อยากให้เกิด แล้วให้คะแนนความมั่นใจ 1-5",
        "หลังจบเคส ให้บันทึกว่าแพ้/ชนะเพราะระบบ หรือเพราะอารมณ์",
    ]
    if context["goals"]:
        steps.insert(0, f"ทวนเป้าหมายบทนี้ก่อนเริ่ม: {context['goals'][0]}")
    return steps


def decision_rules(item: dict) -> list[str]:
    rules = []
    for branch, leaves in item["branches"]:
        lead = leaves[0]
        confirm = leaves[1] if len(leaves) > 1 else leaves[0]
        invalid = leaves[-1]
        rules.append(
            f"{branch}: จะใช้กิ่งนี้ได้เมื่อเห็น {lead} และ {confirm} พร้อมกัน ถ้าเจอเงื่อนไขตรงข้ามกับ {invalid} ให้ลดขนาดหรือหยุด"
        )
    return rules


def common_mistakes(item: dict) -> list[str]:
    first = item["branches"][0][0]
    last = item["branches"][-1][0]
    return [
        f"จำชื่อบทได้ แต่ไม่รู้ว่า {first} ต้องเปลี่ยนพฤติกรรมการเทรดตรงไหน",
        "เห็นสัญญาณหนึ่งอย่างแล้วรีบสรุป ทั้งที่ยังไม่ได้เช็กบริบทและหลักฐานประกอบ",
        "วางแผนตอนใจเย็น แต่พอราคาเคลื่อนไหวจริงกลับเปลี่ยนกฎตามอารมณ์",
        f"สนใจ {last} แค่ตอนอยากเข้า แต่ไม่ใช้เป็นเงื่อนไขตอนต้องออกหรือหยุด",
    ]


def mermaid_mindmap(item: dict) -> str:
    lines = ["```mermaid", "mindmap", f"  root(({safe_node(item['title'])}))"]
    for branch, leaves in item["branches"]:
        lines.append(f"    {safe_node(branch)}")
        for leaf in leaves:
            lines.append(f"      {safe_node(leaf)}")
            for detail in leaf_depth(branch, leaf)[:1]:
                lines.append(f"        {safe_node(detail)}")
    lines.append("```")
    return "\n".join(lines)


def write_markdown(item: dict) -> None:
    context = lesson_context(item)
    branch_outline = []
    for branch, leaves in item["branches"]:
        branch_outline.append(f"### {branch}")
        branch_outline.append(f"- ภาพรวม: {branch_rule(branch, leaves)}")
        for leaf in leaves:
            branch_outline.append(f"- {leaf}")
            branch_outline.extend(f"  - {detail}" for detail in leaf_depth(branch, leaf))
        branch_outline.append("")

    goals = "\n".join(f"- {goal}" for goal in context["goals"]) or "- ยังไม่มีเป้าหมายจากไฟล์บทเรียนเดิม"
    keywords = ", ".join(context["keywords"]) if context["keywords"] else "ยังไม่มีคำสำคัญจากไฟล์บทเรียนเดิม"
    quotes = "\n\n".join(f"> {quote}" for quote in context["quotes"]) or "> ยังไม่มี quote จาก transcript ในไฟล์บทเรียนเดิม"
    practice = "\n".join(f"- {step}" for step in practice_steps(item, context))
    rules = "\n".join(f"- {rule}" for rule in decision_rules(item))
    mistakes = "\n".join(f"- {mistake}" for mistake in common_mistakes(item))

    questions = [
        "กิ่งไหนคือแก่นที่สุดของบทนี้",
        "กิ่งไหนเกี่ยวกับจุดอ่อนของ Patiphan มากที่สุด",
        "ถ้าจะเอาไปใช้กับกราฟจริง ต้องเห็นหลักฐานอะไร",
        "ถ้าทำผิด บทนี้เตือนให้หยุดตรงไหน",
        "ปลายทางของบทนี้จะเข้าไปอยู่ในระบบเทรดส่วนไหน",
    ]

    body = f"""# Mind Map: {item['title']}

## Central Idea
{item['central']}

## Learning Context
- Phase: {context['phase'] or 'ไม่ระบุ'}
- Category: {context['category'] or 'ไม่ระบุ'}

## Learning Goals
{goals}

## Keywords To Remember
{keywords}

{mermaid_mindmap(item)}

## Big Branches + Deep Branches
{chr(10).join(branch_outline)}

## Transcript Signals
{quotes}

## Decision Rules
{rules}

## Common Mistakes
{mistakes}

## Practice Checklist
{practice}

## Final Destination
{item['destination']}

## Questions for Patiphan
{chr(10).join(f'{i + 1}. {q}' for i, q in enumerate(questions))}
"""
    (OUT_MD / f"{item['slug']}_mindmap.md").write_text(body, encoding="utf-8")


def html_card(item: dict) -> str:
    context = lesson_context(item)
    branches = []
    for branch, leaves in item["branches"]:
        leaves_html = []
        leaves_html.append(f"<li class='branch-rule'>{html.escape(branch_rule(branch, leaves))}</li>")
        for leaf in leaves:
            detail_html = "".join(f"<li>{html.escape(detail)}</li>" for detail in leaf_depth(branch, leaf))
            leaves_html.append(
                f"<li><strong>{html.escape(leaf)}</strong><ul class='deep'>{detail_html}</ul></li>"
            )
        branches.append(f"<article class='branch'><h2>{html.escape(branch)}</h2><ul>{''.join(leaves_html)}</ul></article>")
    goals_html = "".join(f"<li>{html.escape(goal)}</li>" for goal in context["goals"])
    keywords_html = "".join(f"<span>{html.escape(word)}</span>" for word in context["keywords"])
    quotes_html = "".join(f"<blockquote>{html.escape(quote)}</blockquote>" for quote in context["quotes"])
    practice_html = "".join(f"<li>{html.escape(step)}</li>" for step in practice_steps(item, context))
    rules_html = "".join(f"<li>{html.escape(rule)}</li>" for rule in decision_rules(item))
    mistakes_html = "".join(f"<li>{html.escape(mistake)}</li>" for mistake in common_mistakes(item))
    return f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(item['title'])}</title>
  <link rel="stylesheet" href="../mindmap_pages.css">
</head>
<body>
  <header>
    <a href="index.html">กลับหน้ารวม</a>
    <p>Lesson Mind Map</p>
    <h1>{html.escape(item['title'])}</h1>
    <div class="central"><strong>Central Idea</strong><span>{html.escape(item['central'])}</span></div>
  </header>
  <main>
    <section class="lesson-context">
      <article><h2>Learning Goals</h2><ul>{goals_html}</ul></article>
      <article><h2>Keywords</h2><div class="keywords">{keywords_html}</div></article>
    </section>
    <section class="map">{''.join(branches)}</section>
    <section class="evidence">
      <h2>Transcript Signals</h2>
      {quotes_html}
    </section>
    <section class="lesson-context lower">
      <article><h2>Decision Rules</h2><ul>{rules_html}</ul></article>
      <article><h2>Common Mistakes</h2><ul>{mistakes_html}</ul></article>
    </section>
    <section class="destination">
      <h2>Practice Checklist</h2>
      <ul>{practice_html}</ul>
    </section>
    <section class="destination">
      <h2>Final Destination</h2>
      <p>{html.escape(item['destination'])}</p>
    </section>
  </main>
</body>
</html>
"""


def write_html(item: dict) -> None:
    (OUT_HTML / f"{item['slug']}.html").write_text(html_card(item), encoding="utf-8")


def write_index() -> None:
    links = []
    for i, item in enumerate(MINDMAPS, start=1):
        links.append(
            f"<a class='lesson-link' href='{item['slug']}.html'>"
            f"<span>{i:02d}</span><strong>{html.escape(item['title'])}</strong>"
            f"<em>{html.escape(item['destination'])}</em></a>"
        )
    index = f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>The Legend Mind Maps</title>
  <link rel="stylesheet" href="../mindmap_pages.css">
</head>
<body>
  <header>
    <p>The Legend</p>
    <h1>Mind Maps ครบ 20 บท</h1>
    <div class="central"><strong>Skill Format</strong><span>ภาพใหญ่ → กิ่งหลัก → กิ่งย่อย → ปลายทางของบท</span></div>
  </header>
  <main>
    <section class="lesson-list">{''.join(links)}</section>
  </main>
</body>
</html>
"""
    (OUT_HTML / "index.html").write_text(index, encoding="utf-8")


def write_css() -> None:
    css = """
:root{--bg:#f6f2ea;--ink:#17201d;--muted:#66716b;--line:#d9d0c1;--accent:#2f6f62;--gold:#bd832d;--card:#fffdf8}
*{box-sizing:border-box}body{margin:0;font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:var(--ink);background:var(--bg)}
header{padding:28px clamp(18px,4vw,48px);background:#17201d;color:#fffaf0}header a{color:#f4c982;font-weight:700;text-decoration:none}header p{margin:0 0 8px;color:#d9c6a5;font-weight:700}h1{margin:0 0 18px;font-size:clamp(30px,4vw,52px);line-height:1.1}.central{max-width:1100px;padding:18px;border:1px solid rgba(255,255,255,.24);border-radius:8px;background:rgba(255,255,255,.08)}.central strong{display:block;margin-bottom:6px;color:#f4c982}.central span{line-height:1.65}
main{padding:28px clamp(18px,4vw,48px) 54px}.lesson-context{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(280px,.8fr);gap:16px;margin-bottom:18px}.lesson-context.lower{margin-top:22px;margin-bottom:0}.lesson-context article,.branch,.destination,.evidence,.lesson-link{border:1px solid var(--line);border-radius:8px;background:var(--card)}.lesson-context article{padding:18px}.lesson-context h2,.destination h2,.evidence h2{margin:0 0 12px}.lesson-context li,.destination li{line-height:1.65;margin:7px 0}.keywords{display:flex;flex-wrap:wrap;gap:8px}.keywords span{border:1px solid #d8c5a5;background:#fbf3e4;border-radius:999px;padding:6px 10px;color:#5b482b;font-weight:700}.map{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px;align-items:start}.branch{overflow:hidden}.branch h2{margin:0;padding:14px 16px;background:#efe4d2;font-size:19px}.branch ul{margin:0;padding:14px 18px 18px 30px}.branch li{margin:9px 0;line-height:1.58}.branch li::marker{color:var(--accent)}.branch strong{color:#163f37}.branch-rule{color:var(--muted);font-weight:700}.deep{padding:7px 0 4px 22px!important}.deep li{font-size:14px;color:#46544e}.destination,.evidence{margin-top:22px;padding:22px}.destination p{line-height:1.75}.evidence blockquote{margin:12px 0;padding:14px 16px;border-left:4px solid var(--accent);background:#f3efe6;line-height:1.7;color:#32423c}.lesson-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px}.lesson-link{display:grid;gap:8px;padding:16px;text-decoration:none;color:var(--ink)}.lesson-link span{color:var(--gold);font-weight:800}.lesson-link strong{font-size:18px}.lesson-link em{color:var(--muted);font-style:normal;line-height:1.55}@media(max-width:760px){.lesson-context{grid-template-columns:1fr}.map{grid-template-columns:1fr}}
"""
    (ROOT / "mindmap_pages.css").write_text(css.strip() + "\n", encoding="utf-8")


def main() -> None:
    OUT_MD.mkdir(parents=True, exist_ok=True)
    OUT_HTML.mkdir(parents=True, exist_ok=True)
    write_css()
    for item in MINDMAPS:
        write_markdown(item)
        write_html(item)
    write_index()
    print(f"Generated {len(MINDMAPS)} mind maps")


if __name__ == "__main__":
    main()
