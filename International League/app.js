"use strict";

// ─── LESSON DATA ──────────────────────────────────────────────────────────────

const lessons = [
  {
    id: "open-world",
    index: 1,
    ep: "02",
    title: "เปิดโลกการลงทุนกับตลาดต่างประเทศ",
    instructor: "อ.นัท ณัฐกฤษ · โค้ชแทม สธนธร",
    category: "Foundation",
    minutes: 194,
    focus: "ทำไมนักลงทุนไทยควรมองออกนอกตลาดไทย ข้อจำกัดที่มีอยู่ และข้อได้เปรียบของตลาด US",
    takeaway: "อ.นัทย้ายเงิน 80% ออกจากตลาดไทยไปตลาด US เพราะ options เปิดโอกาสทำกำไรได้ทุกสภาวะตลาด",
    videoUrl: "https://www.youtube.com/watch?v=ea8Cet25Mpw"
  },
  {
    id: "us-opportunity",
    index: 2,
    ep: "07",
    title: "ตลาดหุ้นอเมริกา โอกาสที่นักลงทุนไม่ควรมองข้าม",
    instructor: "อ.เศรษฐทวิต — เพจ ทันโลกกับ Tender HP",
    category: "Foundation",
    minutes: 175,
    focus: "ภาพรวมตลาด US: ขนาด สภาพคล่อง โอกาส และสิ่งที่แตกต่างจากตลาดไทยอย่างมีนัยสำคัญ",
    takeaway: "ตลาด US มีหุ้น 6,000+ ตัว options รายตัว ETF ครอบคลุม short selling เต็มรูปแบบ — ครบเครื่องทำกำไรทุกสภาวะ",
    videoUrl: "https://www.youtube.com/watch?v=TqruzhoIHjE"
  },
  {
    id: "macro-system",
    index: 3,
    ep: "05",
    title: "รู้ทัน ระบบการเงินโลก และกลยุทธ์การวาง Asset Allocation",
    instructor: "อ.T (สพรวัฒน์) — CFA Level 2 · VI & Macro Investor",
    category: "Macro",
    minutes: 187,
    focus: "Macroeconomics ตามหลัก CFA Level 2 และการวาง asset allocation ให้สอดคล้องกับ economic cycle โลก",
    takeaway: "เข้าใจ 4 phases ของ economic cycle ก่อน allocate — macro คือ top-down filter ที่กรอง sector และ asset ให้ถูก cycle",
    videoUrl: "https://www.youtube.com/watch?v=846KoVsDIPI"
  },
  {
    id: "tech-stocks",
    index: 4,
    ep: "04",
    title: "หุ้นเทคเปลี่ยนโลก อวสานหรือโอกาส 10 เด้ง!!",
    instructor: "VI Investor — US & Global Markets",
    category: "Sector",
    minutes: 168,
    focus: "วิเคราะห์หุ้นเทคโนโลยีใน US ว่าตัวไหนเป็น winner ระยะยาว ตัวไหนร่วงแล้วไม่กลับ",
    takeaway: "หุ้นเทคมีทั้ง winner กับ loser — ดู moat, revenue growth, gross margin, free cash flow ก่อนตัดสินใจ",
    videoUrl: "https://www.youtube.com/watch?v=51b5D_PoWoI"
  },
  {
    id: "ev-disruption",
    index: 5,
    ep: "06",
    title: "หาหุ้นเข้าพอร์ต กับการมาของ EV อะไรจะปลิว อะไรจะรอด?",
    instructor: "อ.กฤษดา (Well Done) — อดีต R&D Toyota",
    category: "Sector",
    minutes: 170,
    focus: "ผลกระทบของ EV revolution ต่อทุก industry ใน supply chain และวิธีหาหุ้นที่ได้ประโยชน์",
    takeaway: "EV ไม่ใช่แค่ Tesla — เปลี่ยนทั้ง ecosystem: แบตเตอรี่ ชิป charging กริดไฟฟ้า ขณะที่น้ำมัน/ICE/ดีลเลอร์เดิมถูก disrupt",
    videoUrl: "https://www.youtube.com/watch?v=QtaK4ZPGZfs"
  },
  {
    id: "momentum-mtf",
    index: 6,
    ep: "01",
    title: "Momentum Based Multi Time Frame",
    instructor: "วิทยากร — Institutional Trader",
    category: "Technical",
    minutes: 182,
    focus: "การใช้ momentum ร่วมกับหลาย timeframe เพื่อยืนยัน direction ก่อนหา entry",
    takeaway: "ดู trend ใน TF ใหญ่ → รอ alignment ใน TF กลาง → จับ trigger ใน TF เล็ก — ห้ามเทรดทวน trend ใน TF ใหญ่",
    videoUrl: "https://www.youtube.com/watch?v=iTUbZfvHHfw"
  },
  {
    id: "stock-screener",
    index: 7,
    ep: "03",
    title: "เทคนิคการทำกำไรในตลาดต่างประเทศ — Stock Screener & EMA",
    instructor: "โค้ชเนส · โค้ชเฟรม (กิตติชัยวัฒน์)",
    category: "Technical",
    minutes: 165,
    focus: "การ scan หาหุ้นใน US ด้วย EMA และ Stock Screener เพื่อลด watchlist จากหมื่นตัวเหลือแค่ที่ actionable",
    takeaway: "EMA ใช้ได้กับทุกตลาดทั่วโลก — scan ด้วย EMA alignment ตาม sector ที่กำลัง outperform แล้วค่อย drill down รายตัว",
    videoUrl: "https://www.youtube.com/watch?v=l9eN3iHvDOY"
  },
  {
    id: "macd-strategy",
    index: 8,
    ep: "09",
    title: "MMA + MACD Strategy Tester",
    instructor: "โค้ชเฟรม · พี่เนต",
    category: "Technical",
    minutes: 131,
    focus: "การ backtest ระบบ MMA และ MACD เพื่อทดสอบความน่าเชื่อถือและประสิทธิภาพก่อนใช้กับเงินจริง",
    takeaway: "ระบบที่ดีต้อง backtest ผ่านก่อน — ดูทั้ง win rate, profit factor, max drawdown และ consistency ข้าม market condition",
    videoUrl: "https://www.youtube.com/watch?v=xe1o8QSPVEA"
  },
  {
    id: "options-1",
    index: 9,
    ep: "08",
    title: "สร้างกำไร 10 เด้ง ด้วย Options หุ้นอเมริกา — ตอนที่ 1",
    instructor: "โค้ชเฟรม (กิตติชัยวัฒน์) · พี่เนต",
    category: "Options",
    minutes: 175,
    focus: "พื้นฐาน options, compound interest, 4 มิติหลักของการใช้ options และทำไมนักลงทุนถือหุ้น US แต่ไม่ใช้ options คือเสียเปรียบ",
    takeaway: "Options คือ derivative (ตราสารอนุพันธ์) — มี 4 มิติ ตอบสภาวะตลาดต่างกันครบทุกทิศทาง และให้ leverage ที่รู้ max loss ล่วงหน้า",
    videoUrl: "https://www.youtube.com/watch?v=YCDpUAtGdJw"
  },
  {
    id: "options-2",
    index: 10,
    ep: "08",
    title: "สร้างกำไร 10 เด้ง ด้วย Options หุ้นอเมริกา — ตอนที่ 2",
    instructor: "วิทยากร",
    category: "Options",
    minutes: 168,
    focus: "กลยุทธ์ options ระดับกลาง-สูง การ manage position บริหาร premium และ risk/reward",
    takeaway: "เมื่อเข้าใจ 4 มิติแล้ว เลือก strategy ที่ match กับ thesis และ risk ของตัวเอง — sell premium เมื่อ IV สูง buy เมื่อ IV ต่ำ",
    videoUrl: "https://www.youtube.com/watch?v=4ePBQJqBL_o"
  },
  {
    id: "options-3",
    index: 11,
    ep: "10",
    title: "สร้างกำไร 10 เด้ง ด้วย Options หุ้นอเมริกา — Advanced",
    instructor: "อ.นัท ณัฐกฤษ · โค้ชแฮม",
    category: "Options",
    minutes: 193,
    focus: "มุมมอง options จากผู้เชี่ยวชาญในฐานะ perspective ไม่ใช่แค่ product — options เป็นได้ทั้ง risk reducer และ profit magnifier",
    takeaway: "Options ไม่ใช่ให้เลือกระหว่างหุ้น vs options — มันคือ 'config' เพิ่มเติมที่ซ้อนบนหุ้น เหมือนเลือก package รถยนต์ตามต้องการ",
    videoUrl: "https://www.youtube.com/watch?v=OtgBqZIEXbc"
  }
];

// ─── LESSON CONTENT (distilled from transcripts) ─────────────────────────────

const lessonContent = {
  "open-world": {
    forYou: "คุณเทรด US อยู่แล้ว — บทนี้ไม่ใช่เรื่องใหม่ แต่เป็นการตรวจสอบว่าเหตุผลที่คุณออกมาอยู่ตลาด US นั้น \"ถูกต้อง\" ตามที่ผู้เชี่ยวชาญ 10+ ปีคิดอยู่ด้วยหรือไม่ คำถามที่ต้องถามตัวเอง: คุณใช้ options แล้วหรือยัง?",
    concepts: [
      {
        title: "ข้อจำกัดของตลาดไทย",
        body: "ตลาดหุ้นไทยทำกำไรได้หลักในขาขึ้นเท่านั้น ทางเลือกขาลงมีแต่ DW และ TFEX ซึ่งมีข้อจำกัดสูง อ.นัทเคยติดหุ้นไทยตัวหนึ่ง ดอยอยู่แสนกว่าบาทในพอร์ตล้านกว่าบาท ออกไม่ได้เพราะถ้าออกก็คือทุบหุ้นตัวเอง — นั่นคือข้อจำกัดที่ไม่มีวันแก้ได้ในตลาดไทย"
      },
      {
        title: "ข้อดีของตลาด US ที่ตลาดไทยไม่มี",
        body: "ตลาด US ทำกำไรได้ทั้งขาขึ้น ขาลง และไซด์เวย์ด้วย options ในหุ้นรายตัว มี short selling เต็มรูปแบบ มี ETF ครอบคลุมทุก sector มีสภาพคล่องสูงมาก และไม่มี circuit breaker ห้ามขาย"
      },
      {
        title: "วิธีเข้าถึงตลาด US: 2 ช่องทาง",
        body: "ช่องทางที่ 1 คือผ่านโบรกเกอร์ต่างประเทศโดยตรง (Interactive Brokers, Schwab ฯลฯ) — ซื้อได้ตั้งแต่ 1 หุ้น มีเศษหุ้น (fractional shares) ราคา Apple 100+ USD ก็ซื้อได้ด้วยเงิน 4-5 พันบาท ช่องทางที่ 2 คือผ่านโบรกเกอร์ไทย — มี DR (Depositary Receipt) เช่น BABA DR ที่ราคาเป็นบาท แต่มีข้อจำกัดและค่าใช้จ่ายต่างกัน"
      },
      {
        title: "Fractional Shares คืออะไร",
        body: "ถ้าหุ้น 1 ตัวราคา 100,000 บาท แต่เรามีแค่ 40,000 บาท ก็ซื้อเศษหุ้นได้ 0.4 ตัว พอร์ตจะแสดงว่าถือ 0.4 shares — นี่คือความยืดหยุ่นที่ตลาดไทยไม่มี"
      }
    ],
    rules: [
      "โบรกเกอร์ต่างประเทศโดยตรงดีกว่า DR เพราะใช้ options ได้เต็มรูปแบบ",
      "ถ้ายังใช้ DR อยู่ = ยังไม่สามารถใช้ options ในหุ้นรายตัวได้",
      "ตลาด US เปิด 20:30-03:00 น. ไทย (21:30-04:00 ช่วง DST สหรัฐ)"
    ],
    numbers: ["80% พอร์ตที่อ.นัทย้ายไป US", "10-12 ปี ประสบการณ์ต่างประเทศของอ.นัท", "1 หุ้น คือขั้นต่ำที่ซื้อได้", "0.4 ตัวอย่าง fractional shares"]
  },

  "us-opportunity": {
    forYou: "บทนี้ให้ภาพใหญ่ว่าทำไม US จึงเป็น default ของนักลงทุนระดับโลก ตัวเลข GDP ไทย, ประชากร, และขนาดตลาด US จะช่วยให้คุณ articulate ได้ชัดขึ้นว่าทำไมจึงต้องลงทุนนอกประเทศ",
    concepts: [
      {
        title: "ปัญหาเชิงโครงสร้างของเศรษฐกิจไทย",
        body: "ไทยมีปัญหาเชิงโครงสร้างระยะยาว: อัตราการเกิดลดลง ผู้สูงอายุเพิ่มขึ้นต่อเนื่อง แรงงานที่มีคุณภาพ migrate ออกนอกประเทศ GDP โตช้าลง ~3% ต่อปี และหนี้ครัวเรือนสูง 89.2% ของ GDP สิ่งเหล่านี้กดดัน revenue growth ของบริษัทไทยระยะยาว"
      },
      {
        title: "ขนาดตลาด US เทียบกับไทย",
        body: "NYSE มี market cap $23 Trillion, NASDAQ $16.3 Trillion, S&P 500 คิดเป็น ~80% ของ market cap หุ้นทั้งหมดใน US ในขณะที่ SET มี market cap ประมาณ 5 แสนล้าน USD — ตลาด US ใหญ่กว่า SET มากกว่า 70 เท่า"
      },
      {
        title: "S-Curve และการ disrupt ตัวเอง",
        body: "บริษัทเทคโนโลยี US ที่แข็งแกร่งมักสร้าง S-Curve ใหม่ซ้อนบน S-Curve เดิม ตัวอย่างชัดเจนที่สุดคือ Amazon: เริ่มจาก Online Retail → สร้าง AWS (cloud) → ต่อยอดไปสู่ AI/ML platform ทุก S-Curve ใหม่ทำให้บริษัทไม่ถูก disrupt โดยคนอื่น"
      },
      {
        title: "VC/Startup Funnel → IPO",
        body: "ระบบนิเวศ Startup ใน US แข็งแกร่งมาก: Seed Round → Series A/B/C → Pre-IPO → IPO บริษัทที่ IPO ใน US มักผ่านการกลั่นกรองจาก VC ระดับโลกมาแล้ว ทำให้มีคุณภาพสูงกว่าบริษัทในตลาดเล็กหลายประเทศ"
      }
    ],
    rules: [
      "GDP ไทยโตช้า → หุ้นไทยส่วนใหญ่ Revenue growth จำกัด",
      "ตลาด US มีหุ้น 6,000+ ตัว → screener จำเป็นต้องใช้",
      "S&P 500 คือ benchmark โลก — ถ้าพอร์ตแพ้ S&P 500 ต้องทบทวนกลยุทธ์"
    ],
    numbers: ["$23T NYSE", "$16.3T NASDAQ", "80% S&P 500 ใน US market cap", "89.2% หนี้ครัวเรือนไทยต่อ GDP", "~3% GDP growth ไทยต่อปี", "19% ผู้สูงอายุของประชากรไทย (12.52 ล้านคน)"]
  },

  "macro-system": {
    forYou: "อ.T เกษียณตอนอายุ 34 หลังจาก exit ธุรกิจ และสอบ CFA Level 2 เพื่อลงทุนจริงๆ ไม่ใช่ทำตำรา บทนี้คือ framework ที่คุณต้องใช้กรอง sector และ asset ก่อนเทรดทุกครั้ง",
    concepts: [
      {
        title: "4 Phases ของ Economic Cycle",
        body: "Expansion (GDP โต, อัตราดอกเบี้ยต่ำ) → หุ้น growth, commodities ดี | Slowdown (GDP ชะลอ, เฟดเริ่มขึ้นดอกเบี้ย) → ระวัง speculative growth stocks | Contraction/Recession (GDP ติดลบ, ว่างงานสูง) → bonds, defensive stocks, cash | Recovery (เฟดลดดอกเบี้ย, stimulus) → cyclical stocks, small caps กลับมาก่อน"
      },
      {
        title: "Top-Down Analysis Framework",
        body: "อ.T ใช้ analysis แบบ top-down: เริ่มจาก Global Macro → ดู Economic Phase → กำหนด Asset Allocation (หุ้น/bond/commodity/cash สัดส่วนเท่าไร) → เลือก Sector ที่ outperform ใน phase นั้น → drill down หา stock รายตัว → สุดท้ายค่อยหา entry จาก technical"
      },
      {
        title: "Macro Economic Cycle ใหญ่ — วัฏจักร 100 ปี",
        body: "นักลงทุนระดับโลกอย่าง Ray Dalio พูดถึง long-term debt cycle ที่เกิดขึ้นทุก ~100 ปี (Great Depression 1930 คือตัวอย่าง) ประวัติศาสตร์การเงินซ้ำรอยได้เพราะมนุษย์ตอบสนองต่อความโลภและความกลัวเหมือนเดิมเสมอ — การอ่านประวัติศาสตร์การเงินจึงสำคัญกว่าการอ่าน indicator"
      },
      {
        title: "Portfolio Management หลักๆ 3 ด้าน",
        body: "อ.T สอน 3 เรื่องหลัก: 1) Macro Economic (อ่านว่าโลกอยู่ใน phase ใด) 2) Portfolio Management (จัดสัดส่วน asset class ให้ถูก) 3) Investment Asset Class Allocation (รู้ว่าสินทรัพย์แต่ละประเภทตอบสนองกับ macro phase อย่างไร)"
      }
    ],
    rules: [
      "Macro phase กำหนดก่อนทุกครั้งก่อน allocate เงิน",
      "ถ้าดูแค่ TF เล็กโดยไม่รู้ macro ใหญ่ = เหมือนดู 15 นาทีโดยไม่รู้ TF Day ขยับ",
      "ความรู้ macro ไม่มีประโยชน์ถ้าไม่ลงมือลงทุนจริงให้ขาดทุนจริงก่อน"
    ],
    numbers: ["34 ปี อายุที่อ.T เกษียณ", "CFA Level 2", "4 phases ของ economic cycle", "~100 ปี วัฏจักรใหญ่ตาม Ray Dalio"]
  },

  "tech-stocks": {
    forYou: "ช่วงปี 2022 tech crash เป็นบทเรียนที่สำคัญมาก — หุ้นเทคที่เคยเป็นดาวร้าย -50% ถึง -90% มีทั้งตัวที่กลับมาใหม่และตัวที่หายไปเลย บทนี้สอนวิธีแยก winner จาก loser ก่อนที่จะ cycle ถัดไปมาถึง",
    concepts: [
      {
        title: "Tech Crash 2022 — บทเรียนราคาแพง",
        body: "ปี 2022 เป็นช่วง Contraction ที่เฟดขึ้นดอกเบี้ยแรงที่สุดในรอบ 40 ปี หุ้นเทคร่วงหนัก: Amazon -50%, Google -50%, Meta/Nvidia -70%, NASDAQ ลง 30%+ จาก High ปลายปี 2021 ในขณะที่ small-cap fintech บางตัว -90% แบบไม่กลับ สิ่งที่ต้องรู้คือ: ทำไมบางตัวฟื้น บางตัวไม่ฟื้น"
      },
      {
        title: "Value Investing กับ Tech Stocks",
        body: "หลักการของ Ben Graham (บิดา Value Investing) คือซื้อหุ้นเมื่อราคาตลาดต่ำกว่ามูลค่าที่แท้จริง แต่สำหรับ Tech stocks ใน US ต้องปรับ framework: ไม่ใช่แค่ดู book value แต่ดู: 1) Moat (ข้อได้เปรียบที่ป้องกันได้) 2) Revenue growth consistency 3) Gross margin trend 4) Free cash flow 5) S-curve potential ใหม่"
      },
      {
        title: "Tech Winner vs Tech Loser — แยกยังไง?",
        body: "Tech Winner มักมี: network effect (ยิ่งมีคนใช้ยิ่งดีขึ้น), switching cost สูง (ออกไปแล้วเจ็บปวด), scalable revenue model (ต้นทุน marginal ต่ำมาก), gross margin 60%+ Tech Loser มักเป็น: burn cash โดยไม่มี path to profitability, สร้าง revenue growth โดย discount มหาศาล, ไม่มี moat ชัดเจน, อยู่ใน commodity business ที่มีคู่แข่งมาก"
      }
    ],
    rules: [
      "ดู Free Cash Flow ก่อน — บริษัทที่ burn cash ไม่มีกำหนดคือความเสี่ยงสูง",
      "Tech crash คือโอกาสซื้อ winner ราคาถูก ไม่ใช่สัญญาณหนี",
      "เปรียบบริษัทกับ S-curve: มันอยู่ตรงไหน และยังมี S-curve ใหม่รออยู่ไหม?"
    ],
    numbers: ["-50% Amazon ช่วง 2022", "-70% Meta/Nvidia ช่วง 2022", "-90% small-cap fintech บางตัว", "-30%+ NASDAQ จาก High ปลาย 2021", "60%+ gross margin ที่ดี"]
  },

  "ev-disruption": {
    forYou: "EV disruption คือ thematic mega-trend ที่ใหญ่กว่าที่คนส่วนใหญ่คิด ผู้สอน (อดีต Toyota R&D) เห็นมันจากข้างในวงการมาก่อน บทนี้ให้ mental model ว่าเมื่อ megatrend มา ใครได้ ใครเสีย และจะหาหุ้นจากจุดไหน",
    concepts: [
      {
        title: "4 Industrial Revolutions — เราอยู่ตรงไหน?",
        body: "ยุคที่ 1 (1700s): เครื่องจักรไอน้ำ → รถไฟ, โรงงาน | ยุคที่ 2 (1800s): ไฟฟ้า → GE, Edison | ยุคที่ 3 (1990s): Computing, Internet, Mobile | ยุคที่ 4 (ปัจจุบัน): AI, IoT, Autonomous Vehicle, Biotech, Quantum — EV คือส่วนหนึ่งของการปฏิวัติครั้งที่ 4 ผู้ที่ปรับตัวทัน = เศรษฐีรุ่นใหม่"
      },
      {
        title: "EV Ecosystem — ใครได้ประโยชน์?",
        body: "EV ไม่ใช่แค่บริษัทรถ มันเปลี่ยน supply chain ทั้งหมด: Battery (lithium, manganese, nickel, cobalt), Power Semiconductor/Chips สำหรับ EV, Charging Infrastructure, Utility/Power Grid ที่ต้องรองรับโหลดเพิ่ม, Heat Pump (แทน ICE heating), Software/AI สำหรับ autonomous driving"
      },
      {
        title: "EV Ecosystem — ใครเสียหาย?",
        body: "น้ำมัน/ปิโตรเคมี, ชิ้นส่วน ICE engine (gasket, exhaust, transmission, crankshaft), ร้านซ่อม ICE, ปั๊มน้ำมัน, ดีลเลอร์รถยนต์แบบดั้งเดิม — รายได้จากการซ่อมบำรุง ICE จะหายไป ไทยมีคน 500,000 คนในอุตสาหกรรมรถยนต์ที่ได้รับผลกระทบ"
      },
      {
        title: "S-Curve การลงทุนใน EV Theme",
        body: "วิธีหาหุ้น: ต้องอยู่ในช่วง S-Curve ขาขึ้น ไม่ใช่ขาลง ดูว่าบริษัทอยู่ใน ecosystem ที่ได้ประโยชน์หรือเสียหาย ดูการเปลี่ยนแปลงใน supply chain ว่า demand จะไปทางไหน Indonesia มีแร่ nickel เยอะ Vietnam มีรถ EV แบรนด์ตัวเอง (VinFast) ไทยต้องปรับตัว"
      }
    ],
    rules: [
      "EV disruption เป็น megatrend ที่ใช้เวลา 10-20 ปี — ซื้อก่อน mass adoption ดีกว่าซื้อตอนดัง",
      "อย่าแค่ดูผู้ผลิต EV — ดู upstream supply chain (แร่, ชิป, แบต) ด้วย",
      "บริษัทที่อยู่ใน 'loser' side ของ disruption ควรหลีกเลี่ยง แม้ราคาถูก"
    ],
    numbers: ["500,000 คนไทยในอุตสาหกรรมรถยนต์", "4 ครั้ง การปฏิวัติอุตสาหกรรม", "World Economic Forum ครั้งที่ 50"]
  },

  "momentum-mtf": {
    forYou: "บทนี้ตรงกับสไตล์การเทรดของคุณมากที่สุด ก่อนจะใช้ MTF ต้องถามตัวเองให้ชัดก่อน: คุณเป็น day trader, swing trader หรือ position trader? ถ้ายังไม่ชัด — ผลลัพธ์คือเละ",
    concepts: [
      {
        title: "เคลียร์ Framework ก่อน — Day/Swing/Position",
        body: "นักเทรดส่วนใหญ่เสียเงินเพราะ 'มั่ว' — วันนี้ day trade พรุ่งนี้ swing trade ไม่มี consistency ต้องเคลียร์ตัวเองก่อนว่าถนัดอะไร: Day Trader = ปิด position ภายในวัน, Swing Trader = ถือ 2-10 วัน, Position Trader = ถือหลายสัปดาห์ถึงหลายเดือน แล้วค่อย allocate ระบบและเวลาให้ตรงกัน"
      },
      {
        title: "Multi Time Frame (MTF) — วิธีใช้ถูกต้อง",
        body: "MTF ทำงาน 3 ระดับ: TF ใหญ่ (Weekly/Daily) = กำหนด direction หลัก ห้ามเทรดทวนทิศนี้ | TF กลาง (Daily/4H) = รอ momentum align กับทิศใน TF ใหญ่ | TF เล็ก (1H/15min/5min) = จับ trigger entry เท่านั้น ข้อผิดพลาดที่พบบ่อย: เห็น signal ใน TF เล็กแล้วรีบ entry โดยไม่ดู TF ใหญ่"
      },
      {
        title: "ตลาดเล่นได้ทั้ง 2 ฝั่ง",
        body: "ถ้ามองขึ้นอย่างเดียว = เสียเปรียบครึ่ง ตลาด US ในช่วง down trend ก็มี bear market rally (ขึ้นชั่วคราวใน down trend) ที่ทำกำไรได้ ใน US options ช่วยได้มาก: Long Put ตอนขาลง, Long Call ตอนขาขึ้น — ไม่ต้องรอตลาดขึ้นอย่างเดียวอีกต่อไป"
      },
      {
        title: "ศาสตร์ของการขาย = สำคัญเท่าการซื้อ",
        body: "ผู้สอนเคยถือหุ้น 10 ตัว กำไรตัวละ 100%+ แต่ไม่ได้วางแผนขาย พอตลาด collapse ต้องหนีตายทุกราคา สุดท้ายกำไรหายหมด บทเรียน: ต้องกำหนด exit rule ตั้งแต่ก่อน entry เสมอ ทั้ง take profit และ stop loss"
      }
    ],
    rules: [
      "เคลียร์ style ตัวเองก่อน: day/swing/position — อย่าผสม",
      "TF ใหญ่กำหนด direction → TF กลาง filter → TF เล็ก entry เท่านั้น",
      "ห้ามเทรดทวน trend ใน TF ใหญ่ ไม่ว่า signal TF เล็กจะสวยแค่ไหน",
      "กำหนด exit rule (TP/SL) ก่อน entry ทุกครั้ง"
    ],
    numbers: ["3 ระดับ TF ที่ต้องดู", "20% ประมาณ day trader ในห้อง", "100% กำไรที่หายเพราะไม่มี exit plan"]
  },

  "stock-screener": {
    forYou: "ตลาด US มีหุ้น 6,000+ ตัว — ถ้าไม่มี screener คือทำงานตาบอด บทนี้โค้ชเนส+โค้ชเฟรมสอน EMA ในเชิง practical บน TradingView ซึ่งคุณน่าจะใช้อยู่แล้ว ตรวจสอบว่าคุณใช้ถูก timeframe และ setting หรือเปล่า",
    concepts: [
      {
        title: "EMA — เครื่องมือสากลที่ใช้ได้ทุกตลาด",
        body: "EMA (Exponential Moving Average) ใช้ได้กับทุกตลาดทั่วโลก เพราะ price action เป็นภาษาสากล ไม่ว่าจะเป็นหุ้นไทย US ยุโรป Crypto กราฟก็ตอบสนองต่อ momentum ด้วยหลักการเดียวกัน ราคาเหนือ EMA = uptrend, ราคาต่ำกว่า EMA = downtrend"
      },
      {
        title: "EMA Sizes ที่ใช้บ่อย",
        body: "เทรดสั้น (5-10 วัน): EMA 8/13 หรือ EMA 50 | เทรดกลาง (swing): EMA 20/50 | ระยะยาว/direction: EMA 89, EMA 200 | Beer Vanon ใช้ EMA 5/15/35/89 | ข้อสำคัญ: EMA ดีมากช่วงมี trend แต่ส่ง signal ผิดมากช่วง sideway"
      },
      {
        title: "TradingView — ต้องใช้ Paid Plan",
        body: "TradingView Free ไม่สามารถใช้ Strategy Tester/Backtest ได้ ต้องซื้อ Pro ขึ้นไป (Pro/Pro+/Premium) ถึงจะ backtest strategy และดู historical performance ได้ โค้ชเฟรมแนะนำ TradingView Pro เป็นขั้นต่ำในการเทรด US"
      },
      {
        title: "Stock Screener Workflow",
        body: "ขั้นตอน: 1) กำหนด macro phase ว่าตอนนี้ตลาดอยู่ใน phase ใด 2) เลือก sector ที่ outperform ใน phase นั้น 3) scan หุ้นใน sector นั้นด้วย EMA alignment (ราคาเหนือ EMA89 daily) 4) กรองด้วย volume สูง (liquidity) 5) drill down ดู fundamental รายตัว 6) หา entry ด้วย technical"
      }
    ],
    rules: [
      "ใช้ EMA 89 Daily เป็น direction filter หลัก — ราคาต่ำกว่า EMA89 = ไม่ซื้อ",
      "Volume ต้องสูงพอ: หุ้นที่ volume ต่ำช่วง premarket/aftermarket = สภาพคล่องต่ำ",
      "EMA ใช้ไม่ได้ช่วง sideway — ต้องรู้จัก filter ก่อน"
    ],
    numbers: ["6,000+ หุ้นใน US ที่ต้องกรอง", "EMA 89 คือ direction filter หลัก", "TradingView Pro คือขั้นต่ำที่ต้องการ"]
  },

  "macd-strategy": {
    forYou: "โค้ชเฟรมและพี่เนตสร้าง custom indicator (MA Back Test) จาก TradingView Pine Script เพื่อแก้ปัญหาที่นักเทรดทั่วไปเจอ: เชื่อ indicator มากเกินไปโดยไม่ backtest บทนี้สอนวิธีคิดเกี่ยวกับการทดสอบระบบ ไม่ใช่แค่ใช้ indicator ตามที่คนอื่นบอก",
    concepts: [
      {
        title: "ปัญหาหลักของนักเทรดกับ Indicator",
        body: "นักเทรดส่วนใหญ่เจอปัญหาเดียวกัน: เรียนมาจากหลายที่, ได้ indicator หลายตัว แต่ไม่รู้ว่าใช้ถูกไหม พอลองใช้แล้วได้กำไรครั้งแรก → over-confident → All-in ครั้งถัดไป → ขาดทุนหนัก สาเหตุ: ไม่เคย backtest ว่า indicator ตัวนั้น work จริงไหมใน market conditions ต่างๆ"
      },
      {
        title: "MA Back Test Indicator",
        body: "โค้ชเฟรมเขียน Pine Script ขึ้นมาสร้าง custom indicator ที่ backtest ระบบ MA ย้อนหลังหลายปีได้ เห็น win rate, profit factor, max drawdown, และ consistency ข้าม market conditions ต่างๆ ต้องใช้ TradingView Pro+ ขึ้นไป และต้อง share username กับทีมงานก่อนเพื่อรับ access"
      },
      {
        title: "4 สิ่งที่ต้อง backtest",
        body: "1) Win Rate: ชนะกี่% ของ trades ทั้งหมด 2) Profit Factor: กำไรรวม ÷ ขาดทุนรวม (ต้องมากกว่า 1.5 ถึงจะ viable) 3) Max Drawdown: ขาดทุนสูงสุดจาก peak คือเท่าไร (ยิ่งต่ำยิ่งดี) 4) Consistency: ทำงานดีใน trending market ด้วยไหม หรือดีแค่ใน sideways"
      }
    ],
    rules: [
      "ไม่มีระบบไหนที่ดีกับทุก market condition — ต้อง backtest ก่อน live เสมอ",
      "Profit Factor < 1.5 = ระบบไม่ดีพอ ควรปรับก่อน",
      "Backtest ต้องครอบคลุม: bull market, bear market, และ sideways"
    ],
    numbers: ["Profit Factor > 1.5 เกณฑ์ขั้นต่ำ", "TradingView Pro+ สำหรับ backtest", "4 metrics ที่ต้องดูใน backtest"]
  },

  "options-1": {
    forYou: "บทนี้คือจุดเปลี่ยน ถ้าคุณถือหุ้น US อยู่แต่ยังไม่ใช้ options คุณกำลัง 'leave money on the table' ทุกวัน บทนี้สร้าง mental model พื้นฐานที่ถูกต้องก่อนเรียน options จริงๆ",
    concepts: [
      {
        title: "Compound Interest + Options = พลังที่ไม่สิ้นสุด",
        body: "โค้ชเฟรมยกตัวอย่าง: ถ้าลงทุน 100,000 บาท ได้กำไร 10%/เดือน ทบต้น: 12 เดือน = 313,843 บาท | 24 เดือน = 984,973 บาท (เกือบ 1 ล้าน) | 36 เดือน = 3 ล้านบาท | 48 เดือน = 9.7 ล้านบาท | 60 เดือน = 30 ล้านบาท เงินฝากธนาคาร 1-2%/ปี, ตราสารหนี้ 2-3%/ปี, กองทุนรวม 3-5%/ปี, หุ้น 5-7%/ปี — ล้วนไม่ตอบโจทย์นี้"
      },
      {
        title: "Options คือ Derivative (ตราสารอนุพันธ์)",
        body: "Options คือสัญญาสิทธิ์ที่เกิดจากการตกลงระหว่างผู้ซื้อและผู้ขาย กำหนด: สินค้าอ้างอิง (underlying asset เช่นหุ้น AAPL), ราคาใช้สิทธิ์ (strike price), จำนวน, และวันหมดอายุ (expiration date) ผู้ซื้อ Call/Put มีสิทธิ์แต่ไม่มีภาระ ผู้ขาย (Short) มีภาระแต่ได้ premium"
      },
      {
        title: "4 มิติของ Options",
        body: "Long Call (Buy Call): คาดหุ้นขึ้น max loss = premium ที่จ่าย max gain = ไม่จำกัด | Long Put (Buy Put): คาดหุ้นลง max loss = premium max gain = ราคาหุ้น - premium | Short Call (Sell Call): คาดหุ้นไม่ขึ้นหรือขึ้นช้า ได้ premium เป็น income | Short Put (Sell Put): คาดหุ้นไม่ลง ได้ premium เป็น income — 4 มิตินี้ครอบคลุมทุกสภาวะตลาด"
      },
      {
        title: "ตลาดไทย vs ตลาด US เรื่อง Options",
        body: "ตลาดไทยมี options เฉพาะ SET50 index ตัวเดียว (มีมาแล้ว 10+ ปีแต่ยังไม่ค่อยได้รับความนิยม) ตลาด US มี options ในหุ้นรายตัวหลายพันตัว, ETF options, index options ครบ — ช่องว่างนี้คือสาเหตุที่อ.นัทย้ายพอร์ต 80% ออกมา"
      }
    ],
    rules: [
      "Long Call/Put: max loss = premium ที่จ่าย — รู้ risk ก่อน entry เสมอ",
      "เริ่มจาก Long Call และ Long Put ก่อน — ไม่มี margin call, max loss จำกัด",
      "ถือหุ้น US แต่ไม่ใช้ options = ขับรถโดยไม่ใช้เบรก"
    ],
    numbers: ["100k → 30 ล้าน ใน 60 เดือน (10%/เดือน ทบต้น)", "1-2%/ปี เงินฝาก", "5-7%/ปี หุ้นทั่วไป", "4 มิติ options", "10+ ปีที่ SET50 options มีแต่ไม่ดัง"]
  },

  "options-2": {
    forYou: "บทนี้ต่อยอดจาก 4 มิติที่รู้แล้ว ไปสู่การบริหาร position จริงๆ คำถามหลักที่บทนี้ตอบ: เมื่อเปิด position ไปแล้ว จะ manage อย่างไร และ IV (Implied Volatility) สำคัญอย่างไรในการเลือก strategy",
    concepts: [
      {
        title: "IV (Implied Volatility) กำหนด strategy",
        body: "IV คือ 'ราคาความกลัว' ของตลาด เมื่อ IV สูง (เช่นช่วง earnings หรือวิกฤต): premium ของ options แพง → ควร Sell Premium (Short Call หรือ Short Put) เพื่อ collect premium | เมื่อ IV ต่ำ (ตลาดสงบ): premium ถูก → ควร Buy Options (Long Call หรือ Long Put) เพื่อ leverage"
      },
      {
        title: "Covered Call — สร้าง Income จากหุ้นที่ถืออยู่",
        body: "ถ้าถือหุ้นอยู่แล้ว สามารถ Sell Call ต่อ (ชื่อ Covered Call) เพื่อสร้าง income เพิ่ม ตัวอย่าง: ถือ AAPL 100 หุ้น → Sell Call strike 200 หมดอายุ 30 วัน → เก็บ premium $200 ทันที ถ้าหุ้นไม่ขึ้นถึง 200 premium ก็หมดอายุ ได้เงิน ถ้าขึ้นเกิน 200 ต้องขายหุ้นให้ที่ราคา 200"
      },
      {
        title: "Call Spread — จำกัด Risk/Reward",
        body: "แทนที่จะซื้อ Long Call ตรงๆ ซึ่งแพง ใช้ Call Spread แทน: Buy Call strike 110 + Sell Call strike 115 ราคาหุ้นปัจจุบัน 100 ตัวอย่าง: ต้นทุน (premium) $50, max gain ถ้าหุ้นขึ้นเกิน 115 = $500 → R:R = 1:10 แต่ถ้าหุ้นไม่ขึ้นถึง 110 เสีย $50 ทั้งหมด"
      },
      {
        title: "Protective Put — ป้องกันขาลง",
        body: "ถ้าถือหุ้นและกลัวลง ซื้อ Long Put เป็น insurance ตัวอย่าง: ถือ AAPL 100 หุ้น ที่ $150 ซื้อ Put strike $140 จ่าย premium $3 ถ้าหุ้นลงต่ำกว่า $140 Put จะกำไร ช่วยชดเชยขาดทุนจากหุ้น max loss ของทั้งพอร์ต = $10 (140-150) + $3 (premium) = $13/หุ้น"
      }
    ],
    rules: [
      "IV สูง = Sell Premium | IV ต่ำ = Buy Options — อย่าสลับ",
      "กำหนด max loss ก่อน entry ทุกครั้ง ไม่ถือขาดทุนรอ options หมดอายุ",
      "Covered Call คือ strategy แรกที่ปลอดภัยสำหรับนักลงทุนที่ถือหุ้นอยู่"
    ],
    numbers: ["$50 ต้นทุน Call Spread ตัวอย่าง", "$500 max gain Call Spread ตัวอย่าง", "R:R 1:10 ตัวอย่าง Call Spread", "30 วัน อายุ Covered Call ที่นิยม"]
  },

  "options-3": {
    forYou: "อ.นัทสรุป options perspective ไว้ชัดที่สุด: options ไม่ใช่สินค้าที่ต้องเลือกระหว่าง 'เล่นหุ้น vs เล่น options' แต่มันคือ 'config' ที่คุณเลือกว่าต้องการเพิ่มอะไรเข้าไปในพอร์ตของคุณ",
    concepts: [
      {
        title: "Options Perspective — Analogy รถยนต์",
        body: "อ.นัทเปรียบ: ซื้อรถ = ถือหุ้น Options ในรถ = Package เสริมที่คุณเลือกตามต้องการ ถ้าต้องการ Safety → เพิ่ม options ที่เน้นความปลอดภัย (เซ็นเซอร์, ถุงลม) ถ้าต้องการ Performance → เพิ่ม options ด้านสมรรถนะ (เครื่องยนต์ดีกว่า, ช่วงล่าง) เช่นเดียวกัน: ถือหุ้นแล้วต้องการ Protection → ซื้อ Put | ต้องการ Income → Sell Covered Call | ต้องการ Leverage → ซื้อ Call"
      },
      {
        title: "4 มิติ Deep Dive — ใช้เมื่อไร?",
        body: "Long Call: ใช้เมื่อ bullish แต่ไม่อยาก risk เงินเต็มก้อน | Long Put: ใช้เมื่อ bearish หรือต้องการ hedge พอร์ต | Short Call (Covered): ใช้เมื่อถือหุ้นและต้องการ income เพิ่ม หรือคาดว่าหุ้นจะไม่ขึ้น | Short Put: ใช้เมื่อต้องการซื้อหุ้นในราคาที่ต่ำกว่าปัจจุบัน และพร้อมรับหุ้นถ้าหุ้นลงมาถึงราคานั้น"
      },
      {
        title: "Greeks — ตัวเลขที่ต้องรู้",
        body: "Delta: options เคลื่อนที่กี่บาทเมื่อหุ้นเปลี่ยน $1 (0-1 สำหรับ Call, -1 ถึง 0 สำหรับ Put) | Theta: options สูญเสียมูลค่าเท่าไรต่อวัน (time decay — ผู้ซื้อเสียเปรียบ ผู้ขายได้เปรียบ) | Vega: options เปลี่ยนมูลค่าเท่าไรเมื่อ IV เปลี่ยน 1% | Gamma: Delta เปลี่ยนเร็วแค่ไหน"
      }
    ],
    rules: [
      "Options ไม่ใช่ gambling — มันคือ risk management tool ที่ออกแบบมาอย่างแม่นยำ",
      "ผู้ซื้อ options: max loss = premium, time เป็นศัตรู (theta decay)",
      "ผู้ขาย options: รับ premium เป็น income, time เป็นเพื่อน แต่ risk ไม่จำกัด (ถ้าไม่ hedge)"
    ],
    numbers: ["Delta 0.5 = ATM options (at-the-money)", "Theta: options เสียมูลค่าทุกวัน", "4 Greeks หลัก: Delta, Theta, Vega, Gamma"]
  }
};

// ─── TOPIC DATA ───────────────────────────────────────────────────────────────

const topics = [
  {
    name: "Foundation",
    label: "ทำไมต้องนอก TH",
    color: "#2563EB",
    angle: 270,
    lessons: ["open-world", "us-opportunity"],
    prompt: "ตอบให้ได้ว่าทำไมต้องออกไปลงทุนนอกประเทศไทย และตลาด US ให้โอกาสอะไรที่ตลาดไทยไม่มี — นี่คือ why ก่อน how"
  },
  {
    name: "Macro",
    label: "ระบบการเงินโลก",
    color: "#7C3AED",
    angle: 342,
    lessons: ["macro-system"],
    prompt: "เข้าใจ economic cycle 4 phases และ allocate สินทรัพย์ให้ถูก phase — macro คือ top-down framework ก่อนเลือก sector และหุ้น"
  },
  {
    name: "Sector",
    label: "วิเคราะห์เซกเตอร์",
    color: "#059669",
    angle: 54,
    lessons: ["tech-stocks", "ev-disruption"],
    prompt: "หาหุ้น sector ที่ thematic trend หนุนหลัง — Tech disruption และ EV revolution เปลี่ยน supply chain ทั้งโลก รู้ก่อนได้ก่อน"
  },
  {
    name: "Technical",
    label: "ระบบเทคนิค",
    color: "#D97706",
    angle: 126,
    lessons: ["momentum-mtf", "stock-screener", "macd-strategy"],
    prompt: "ใช้ momentum, EMA, MACD และ screener ในการหาจังหวะเข้าออก backtest ให้ผ่านก่อน live — เครื่องมือสากล ใช้ได้ทุกตลาด"
  },
  {
    name: "Options",
    label: "Options US Stocks",
    color: "#DC2626",
    angle: 198,
    lessons: ["options-1", "options-2", "options-3"],
    prompt: "เข้าใจ 4 มิติ options แล้วใช้เป็น strategic tool ทำกำไรได้ทุกสภาวะตลาด — เรียน 3 ตอน เริ่มจาก beginner ถึง advanced"
  }
];

// ─── FLASHCARDS ───────────────────────────────────────────────────────────────

const cards = [
  // Foundation
  {
    q: "อ.นัท ณัฐกฤษ ย้ายเงินสัดส่วนเท่าไรออกจากตลาดไทย และเพราะอะไร?",
    a: "80% ของพอร์ต — เพราะ options ใน US ให้ความได้เปรียบที่ตลาดไทยไม่มี: ทำกำไรได้ขาขึ้น ขาลง และไซด์เวย์ hedge position ได้ และมีสภาพคล่องสูงกว่ามาก ตลาดไทยมี options เฉพาะ SET50 ตัวเดียว"
  },
  {
    q: "Fractional Shares คืออะไร และช่วยนักลงทุนรายย่อยอย่างไร?",
    a: "คือการซื้อเศษหุ้น เช่นถ้าหุ้นราคา 100,000 บาท/ตัว แต่เรามีเงินแค่ 40,000 บาท ก็ซื้อได้ 0.4 ตัว พอร์ตแสดงว่าถือ 0.4 shares ทำให้เข้าถึงหุ้นทุกตัวใน US ได้ตั้งแต่เงินหลักพัน"
  },
  {
    q: "ตลาดหุ้นไทยมีข้อจำกัดอะไรที่ทำให้ควรออกไปลงทุนต่างประเทศ?",
    a: "1) ทำกำไรได้หลักในขาขึ้นเท่านั้น 2) Short ทำได้จำกัดผ่าน DW/TFEX มีข้อจำกัดสูง 3) ไม่มี options ในหุ้นรายตัว มีแค่ SET50 4) ตลาดขนาดเล็ก สภาพคล่องน้อยกว่า US มาก 5) บางตัวสภาพคล่องต่ำจนขายทีก็ทุบหุ้นตัวเอง"
  },
  {
    q: "ตัวเลขขนาดตลาด US เทียบกับตลาดไทย มีความแตกต่างกันอย่างไร?",
    a: "NYSE มี market cap $23 Trillion, NASDAQ $16.3 Trillion, S&P 500 = 80% ของ US market cap ทั้งหมด ในขณะที่ SET มี market cap ประมาณ 5 แสนล้าน USD ตลาด US ใหญ่กว่า SET ประมาณ 70+ เท่า"
  },
  {
    q: "S-Curve ของ Amazon แสดงให้เห็นอะไรเกี่ยวกับบริษัทเทค?",
    a: "Amazon สร้าง S-Curve ใหม่ซ้อนบน S-Curve เดิมตลอดเวลา: Online Retail → AWS (cloud) → AI/ML platform แต่ละ S-Curve ใหม่ทำให้ revenue diversify และทำให้ไม่ถูก disrupt โดยคนอื่น ผู้สอนใช้แนวคิดนี้ในการเลือกหุ้นเทคใน US"
  },
  {
    q: "ปัญหาเชิงโครงสร้างของเศรษฐกิจไทยที่ทำให้ตลาดหุ้นไทยโตช้า?",
    a: "อัตราการเกิดลดลง ผู้สูงอายุ (60+ ปี) มี 12.52 ล้านคน = 19% ของประชากร 66 ล้านคน แรงงานลดลงและ migrate ออกนอกประเทศ GDP โตช้า ~3%/ปี หนี้ครัวเรือน 89.2% ของ GDP ทำให้ domestic consumption อ่อนแอ"
  },
  // Macro
  {
    q: "Economic cycle 4 phases คืออะไร และแต่ละ phase สินทรัพย์ไหน outperform?",
    a: "Expansion (GDP โต, rate ต่ำ) → หุ้น growth, commodities | Slowdown (GDP ชะลอ, เฟดขึ้น rate) → ระวัง growth stocks | Contraction/Recession (GDP ติดลบ) → bonds, defensive stocks, cash | Recovery (เฟดลด rate) → cyclical stocks, small caps กลับมาก่อน"
  },
  {
    q: "Top-Down Analysis ของ อ.T ทำงานอย่างไรในทางปฏิบัติ?",
    a: "เริ่มจาก Global Macro → ดู Economic Phase → กำหนด Asset Allocation (หุ้น/bond/commodity/cash สัดส่วนเท่าไร) → เลือก Sector ที่ outperform ใน phase นั้น → drill down รายตัว → หา entry ด้วย technical อย่าข้ามขั้นตอน — เลือกหุ้นก่อนดู macro คือผิด"
  },
  {
    q: "ทำไม อ.T บอกว่า macro economic สำคัญสำหรับนักลงทุนต่างประเทศโดยเฉพาะ?",
    a: "เพราะค่าเงิน, อัตราดอกเบี้ย, และนโยบายของแต่ละประเทศส่งผลต่อผลตอบแทนจริงของพอร์ต อ.T ยกตัวอย่าง: เทรด TF 15 นาทีแล้วได้กำไรตลอด แต่พอ TF Day ขยับใหญ่ TF 15 นาทีส่ง signal ผิดหมด macro เหมือน TF ที่ใหญ่ที่สุด"
  },
  {
    q: "Ray Dalio พูดถึง long-term debt cycle อย่างไร?",
    a: "Dalio บอกว่ามีวัฏจักรใหญ่ที่เกิดทุก ~100 ปี (Great Depression 1930 คือตัวอย่าง) มนุษย์ไม่เคยเปลี่ยน — ตอบสนองต่อความโลภและความกลัวเหมือนเดิมเสมอ ทำให้ประวัติศาสตร์การเงินซ้ำรอย การอ่านประวัติศาสตร์จึงสำคัญกว่า indicator"
  },
  // Sector
  {
    q: "Tech Crash ปี 2022 เกิดขึ้นเพราะอะไร และหุ้นไหนบ้างที่ร่วงหนัก?",
    a: "เพราะเฟดขึ้นดอกเบี้ยแรงที่สุดในรอบ 40 ปีเพื่อสู้เงินเฟ้อ ทำให้ discount rate สูงขึ้น กดมูลค่า growth stocks ลงหนัก Amazon -50%, Google -50%, Meta/Nvidia -70%, NASDAQ -30%+ จาก High ปลายปี 2021 small-cap fintech บางตัว -90% แบบไม่ฟื้น"
  },
  {
    q: "อะไรคือปัจจัยที่แยก Tech Winner ออกจาก Tech Loser?",
    a: "Tech Winner: moat ชัดเจน (network effect/switching cost สูง), revenue growth consistent, gross margin 60%+ แสดงถึง scalability, Free Cash Flow เป็นบวก, มี S-curve ใหม่ Tech Loser: burn cash ไม่มี path to profitability, สร้าง revenue ด้วย discount มหาศาล, ไม่มี moat จริง"
  },
  {
    q: "4 Industrial Revolutions คืออะไร และ EV อยู่ใน revolution ไหน?",
    a: "ยุค 1 (1700s): ไอน้ำ → รถไฟ, โรงงาน | ยุค 2 (1800s): ไฟฟ้า → GE, Edison | ยุค 3 (1990s): Computing, Internet, Mobile | ยุค 4 (ปัจจุบัน): AI, IoT, Autonomous Vehicle, Biotech, Quantum — EV เป็นส่วนหนึ่งของยุคที่ 4 ที่เราอยู่ตอนนี้"
  },
  {
    q: "EV Disruption ส่งผลให้กลุ่มธุรกิจใดได้ประโยชน์ และใดเสียหาย?",
    a: "ได้ประโยชน์: Battery supply chain (lithium, nickel, cobalt), Power Semiconductors/chips สำหรับ EV, Charging Infrastructure, Utility/Power Grid, Software สำหรับ autonomous | เสียหาย: น้ำมัน/ปิโตรเคมี, ชิ้นส่วน ICE (gasket, exhaust, transmission), ร้านซ่อม ICE, ปั๊มน้ำมัน, ดีลเลอร์ดั้งเดิม"
  },
  {
    q: "ทำไมไทยถึงอยู่ในความเสี่ยงสูงจาก EV Disruption?",
    a: "ไทยมีคน 500,000 คนในอุตสาหกรรมรถยนต์ ICE ซึ่งจะได้รับผลกระทบหนักจาก EV ยิ่งไปกว่านั้นคู่แข่งอย่าง Indonesia มีแร่ nickel เยอะ Vietnam มีรถ EV แบรนด์ตัวเอง (VinFast) ไทยต้องปรับตัวเร็วหรือถูกทิ้งไว้ข้างหลัง"
  },
  // Technical
  {
    q: "ก่อนใช้ Momentum MTF ต้องเคลียร์อะไรกับตัวเองก่อน?",
    a: "ต้องกำหนดชัดว่าตัวเองเป็น Day Trader (ปิดใน 1 วัน), Swing Trader (ถือ 2-10 วัน) หรือ Position Trader (ถือหลายสัปดาห์ถึงเดือน) ถ้ายังไม่ชัดหรือผสมกัน = ผลลัพธ์เละ เพราะแต่ละ style ใช้ indicator, timeframe, และ risk management ต่างกัน"
  },
  {
    q: "MTF (Multi Time Frame) ทำงานอย่างไร และแต่ละ TF มีหน้าที่อะไร?",
    a: "TF ใหญ่ (Weekly/Daily) = กำหนด direction หลัก ห้ามเทรดทวน | TF กลาง (Daily/4H) = รอ momentum align กับ TF ใหญ่ | TF เล็ก (1H/15min/5min) = จับ trigger entry เท่านั้น ข้อผิดพลาดที่พบบ่อย: เห็น signal ใน TF เล็กแล้ว entry โดยไม่ดู TF ใหญ่"
  },
  {
    q: "ทำไม EMA จึงใช้ได้กับทุกตลาดทั่วโลก ไม่ว่าจะไทย US หรือ Crypto?",
    a: "เพราะ price action เป็นภาษาสากล ไม่ว่าจะเป็นหุ้นไทย US ยุโรป หรือ Crypto กราฟตอบสนองต่อ momentum และ supply/demand ด้วยหลักการเดียวกัน EMA วัด momentum ของราคาโดยไม่ขึ้นกับ country-specific factor"
  },
  {
    q: "EMA ใช้ได้ดีในสภาวะตลาดไหน และไม่ดีในสภาวะใด?",
    a: "ดีมาก: ช่วงที่ตลาดมี trend ชัดเจน (ขึ้นชัด/ลงชัด) ไม่ดี: ช่วงที่ตลาด sideway เพราะ EMA ส่ง false signal ตลอด ทำให้ cut loss บ่อยโดยไม่ได้กำไร ต้องมี filter เพิ่มเติม เช่น ADX หรือ volume เพื่อแยกว่าตลาดกำลัง trend หรือ sideway"
  },
  {
    q: "4 metrics ที่ต้องดูในการ backtest ระบบ trading?",
    a: "1) Win Rate: ชนะกี่% ของ trades ทั้งหมด (50%+ ถือว่าดี) 2) Profit Factor: กำไรรวม ÷ ขาดทุนรวม (ต้อง > 1.5) 3) Max Drawdown: ขาดทุนสูงสุดจาก peak (ยิ่งต่ำยิ่งดี) 4) Consistency: ทำงานดีใน bull, bear, sideways หรือเฉพาะ condition บางอย่าง"
  },
  {
    q: "Stock Screener แก้ปัญหาอะไรให้นักลงทุนในตลาด US?",
    a: "ตลาด US มีหุ้น 6,000+ ตัว — screener กรองด้วย criteria ที่เรากำหนด (EMA alignment, volume, sector momentum, profitability) ให้เหลือแค่ watchlist 20-50 ตัวที่ actionable โดยใช้ TradingView Pro+ เป็นเครื่องมือหลัก"
  },
  // Options
  {
    q: "Options ต่างจากหุ้นปกติอย่างไรในเชิงโครงสร้าง?",
    a: "หุ้นคือ ownership ในบริษัท Options คือสัญญาสิทธิ์ (derivative) ที่กำหนด: สินค้าอ้างอิง, strike price, จำนวน, และวันหมดอายุ ผู้ซื้อ options มีสิทธิ์แต่ไม่มีภาระ ผู้ขายมีภาระและรับ premium — options จึงเป็น leverage ที่รู้ max loss ล่วงหน้า (สำหรับผู้ซื้อ)"
  },
  {
    q: "4 มิติของ Options คืออะไร และแต่ละมิติใช้ในสภาวะตลาดใด?",
    a: "Long Call: คาดขึ้น (bullish) | Long Put: คาดลง (bearish) / hedge พอร์ต | Short Call: คาดไม่ขึ้น หรือสร้าง income จากหุ้นที่ถือ (Covered Call) | Short Put: คาดไม่ลง รับ premium เป็น income หรือต้องการซื้อหุ้นถูกลง — ครอบคลุมทุกสภาวะตลาด"
  },
  {
    q: "Long Call มี Max Loss และ Max Gain เท่าไร?",
    a: "Max Loss = premium ที่จ่ายไป (รู้ล่วงหน้าตั้งแต่เปิด position) Max Gain = ไม่จำกัด (ยิ่งหุ้นขึ้นมากยิ่งกำไรมาก) — นี่คือข้อได้เปรียบของ Long Call เทียบกับ Short ทั่วไปที่ max loss ไม่จำกัด"
  },
  {
    q: "Covered Call คืออะไร และสร้างรายได้อย่างไร?",
    a: "Covered Call = ถือหุ้นอยู่แล้ว + Sell Call ต่อ เพื่อเก็บ premium เป็น income ตัวอย่าง: ถือ AAPL + Sell Call strike 200 เดือนนี้ = เก็บ premium $200 ทันที ถ้าหุ้นไม่ขึ้นถึง 200 ได้เงิน premium ฟรี ถ้าขึ้นเกิน 200 ต้องขายหุ้นที่ราคา 200 (จำกัด upside)"
  },
  {
    q: "IV (Implied Volatility) สูง vs ต่ำ ควรใช้ options strategy อะไร?",
    a: "IV สูง (เช่นช่วง earnings, วิกฤต): premium แพง → ควร Sell Options เพื่อ collect premium (Covered Call, Cash-secured Put) IV ต่ำ (ตลาดสงบ): premium ถูก → ควร Buy Options เพื่อ leverage ถูก (Long Call/Put) — อย่าสลับ เพราะซื้อตอน IV สูง = แพงมาก"
  },
  {
    q: "Protective Put คืออะไร และช่วยอย่างไรเมื่อตลาดลง?",
    a: "ซื้อ Long Put ขณะที่ถือหุ้น เหมือนซื้อ insurance สำหรับพอร์ต ตัวอย่าง: ถือ AAPL ที่ $150 ซื้อ Put strike $140 จ่าย $3/หุ้น ถ้าหุ้นลงต่ำกว่า $140 put จะกำไรชดเชย max loss ทั้งพอร์ตจำกัดที่ $13/หุ้น ไม่ว่าหุ้นจะลงไปเท่าไร"
  },
  {
    q: "ทบต้น 10%/เดือน ลงทุน 100,000 บาท จะมีเท่าไรใน 5 ปี?",
    a: "12 เดือน = 313,843 บาท | 24 เดือน = 984,973 บาท (~1 ล้าน) | 36 เดือน = 3 ล้านบาท | 48 เดือน = 9.7 ล้านบาท | 60 เดือน = 30 ล้านบาท — นี่คือพลังของ compound interest ที่ options สามารถทำให้ 10%/เดือนเป็นไปได้ (แต่ต้องมีระบบที่ดีและ discipline)"
  },
  {
    q: "Greeks ใน Options มีอะไรบ้าง และแต่ละตัวบอกอะไร?",
    a: "Delta: options เคลื่อนที่กี่บาทเมื่อหุ้น +$1 (Call = 0 ถึง +1, Put = -1 ถึง 0) | Theta: time decay — options สูญเสียมูลค่าเท่าไรต่อวัน (ผู้ขายได้เปรียบ) | Vega: options เปลี่ยนมูลค่าเท่าไรเมื่อ IV เปลี่ยน 1% | Gamma: Delta เปลี่ยนเร็วแค่ไหนเมื่อราคาหุ้นเปลี่ยน"
  },
  {
    q: "อ.นัทเปรียบ Options เหมือนอะไร และทำไมถึงเปรียบแบบนั้น?",
    a: "อ.นัทเปรียบการซื้อหุ้น = ซื้อรถ, Options = Package/Config เสริมที่เลือกตามต้องการ (safety package, performance package) เช่นเดียวกัน: ถือหุ้นแล้วต้องการ protection → ซื้อ Put, ต้องการ income → Sell Covered Call ไม่ใช่เลือกระหว่างหุ้น vs options — มันทำงานร่วมกัน"
  },
  {
    q: "Call Spread คืออะไร และต่างจาก Long Call ตรงๆ อย่างไร?",
    a: "Call Spread = Buy Call strike ต่ำ + Sell Call strike สูง ตัวอย่าง: Buy Call 110 + Sell Call 115 ต้นทุน $50 max gain $500 (R:R = 1:10) Long Call ตรงๆ: ต้นทุนสูงกว่า แต่ไม่จำกัด upside Call Spread: ถูกกว่า แต่จำกัด upside เหมาะเมื่อ IV สูงและต้องการลด cost"
  }
];

// ─── QUIZ ─────────────────────────────────────────────────────────────────────

const quiz = [
  {
    q: "ทำไม อ.นัท ณัฐกฤษ จึงย้ายเงิน 80% ออกจากตลาดไทยมา US?",
    options: ["ค่าคอมในตลาดไทยแพงกว่า", "ตลาด US มี options รายตัว ทำกำไรได้ทุกสภาวะ", "หุ้นไทยไม่ขึ้นแล้ว", "broker ไทยไม่น่าเชื่อถือ"],
    answer: 1,
    explain: "เพราะ options ใน US ทำกำไรได้ทั้งขาขึ้น ขาลง ไซด์เวย์ — ตลาดไทยมีแค่ SET50 options"
  },
  {
    q: "ตลาดหุ้นไทยมี options ในรูปแบบใด?",
    options: ["มีในหุ้นรายตัวทุกตัวใน SET", "มีเฉพาะ SET50 index ตัวเดียว", "ไม่มีเลย", "มีใน TFEX ครบทุก commodity"],
    answer: 1,
    explain: "ไทยมี options เฉพาะ SET50 index ตัวเดียว มีมาแล้ว 10+ ปีแต่ยังไม่ค่อยได้รับความนิยม"
  },
  {
    q: "4 มิติของ Options ได้แก่อะไรบ้าง?",
    options: [
      "Buy, Sell, Hold, Wait",
      "Long Call, Long Put, Short Call, Short Put",
      "ITM, ATM, OTM, DITM",
      "Call, Put, Spread, Straddle"
    ],
    answer: 1,
    explain: "4 มิติครอบคลุมทุกสภาวะ: Long Call (bullish), Long Put (bearish), Short Call (neutral/income), Short Put (neutral/income)"
  },
  {
    q: "ใน Economic cycle ช่วง Contraction (Recession) สินทรัพย์ใด outperform?",
    options: ["หุ้น growth", "Bonds และ defensive stocks", "Commodities", "Small cap stocks"],
    answer: 1,
    explain: "ช่วง recession เฟดมักลดดอกเบี้ย bond ราคาขึ้น defensive stocks (utilities, healthcare) ทำงานได้ดีกว่า"
  },
  {
    q: "MTF (Multi Time Frame) — TF ไหนมีหน้าที่กำหนด Direction หลัก?",
    options: ["TF เล็ก (5min/15min)", "TF กลาง (4H)", "TF ใหญ่ (Weekly/Daily)", "ทุก TF เท่ากัน"],
    answer: 2,
    explain: "TF ใหญ่กำหนด direction ห้ามเทรดทวน TF กลางรอ alignment TF เล็กใช้ entry เท่านั้น"
  },
  {
    q: "EV Disruption ส่งผลให้กลุ่มธุรกิจใดได้ประโยชน์มากที่สุด?",
    options: ["น้ำมันและปิโตรเคมี", "ร้านซ่อม ICE engine", "แบตเตอรี่, ชิป, charging infrastructure", "ดีลเลอร์รถยนต์แบบดั้งเดิม"],
    answer: 2,
    explain: "EV เปลี่ยน ecosystem ทั้งหมด: battery supply chain, power semiconductor, charging infra, utility grid ล้วนได้ประโยชน์"
  },
  {
    q: "Stock Screener ใช้แก้ปัญหาอะไรในตลาด US?",
    options: ["ช่วยซื้อหุ้นถูกกว่าราคาตลาด", "กรองหุ้นจาก 6,000+ ตัวให้เหลือ watchlist ที่ actionable", "หลีกเลี่ยงภาษีจากกำไร", "ทำนายราคาหุ้นได้แม่นยำ"],
    answer: 1,
    explain: "US มีหุ้น 6,000+ ตัว screener ใช้ EMA, volume, sector criteria กรองให้เหลือ 20-50 ตัวที่ดูแลได้"
  },
  {
    q: "Max Loss ของ Long Call Option คืออะไร?",
    options: ["ไม่จำกัด", "เท่ากับมูลค่าหุ้นทั้งหมด", "เท่ากับ premium ที่จ่ายไป", "50% ของ premium"],
    answer: 2,
    explain: "Long Call max loss = premium ที่จ่าย เป็น risk ที่รู้ล่วงหน้าตั้งแต่เปิด position คือข้อดีหลักของ Long options"
  },
  {
    q: "ใน Backtest ที่ดี Profit Factor ควรอยู่ที่เท่าไรขึ้นไป?",
    options: ["มากกว่า 1.0", "มากกว่า 1.5", "มากกว่า 2.0", "มากกว่า 3.0"],
    answer: 1,
    explain: "Profit Factor = กำไรรวม ÷ ขาดทุนรวม ต้อง > 1.5 เป็นขั้นต่ำ หมายความว่าทุก $1 ที่เสีย ได้คืน $1.50+"
  },
  {
    q: "ใน Asset Allocation ควรพิจารณาอะไรก่อนเป็นอันดับแรก?",
    options: ["เลือก broker ที่ถูกที่สุด", "ดูว่า influencer แนะนำหุ้นอะไร", "กำหนด macro phase ของเศรษฐกิจก่อน allocate", "เลือกหุ้นที่ราคาต่ำสุด"],
    answer: 2,
    explain: "อ.T (CFA L2) สอน top-down: macro phase → asset class → sector → stock → entry อย่าข้ามขั้นตอน"
  },
  {
    q: "IV สูง ควรใช้ options strategy แบบใด?",
    options: ["Buy Call และ Buy Put", "Sell Call หรือ Sell Put (collect premium)", "ซื้อ Straddle", "รอให้ IV ลดก่อนค่อยทำอะไร"],
    answer: 1,
    explain: "IV สูง = premium แพง → ควร Sell เพื่อ collect premium เป็น income ซื้อตอน IV สูง = แพงมาก เสียเปรียบ"
  },
  {
    q: "Covered Call คือการทำอะไร?",
    options: ["ซื้อ Call option เพื่อ leverage", "ถือหุ้น + Sell Call ต่อเพื่อสร้าง income", "Short selling หุ้นพร้อมกับซื้อ Call", "ซื้อ Put เพื่อป้องกันขาลง"],
    answer: 1,
    explain: "Covered Call = ถือหุ้อยู่แล้ว + Sell Call ต่อ เพื่อเก็บ premium เป็น income เพิ่มจาก position หุ้นที่มีอยู่"
  },
  {
    q: "Amazon ใช้กลยุทธ์ S-Curve อย่างไรที่ทำให้เป็น tech winner?",
    options: ["ลดราคาสินค้าต่ำที่สุด", "เปิด S-Curve ใหม่ซ้อนบน S-Curve เดิม (Retail → AWS → AI)", "ซื้อกิจการคู่แข่งทั้งหมด", "เน้นขายในตลาด US เท่านั้น"],
    answer: 1,
    explain: "Amazon สร้าง S-Curve ใหม่ตลอด: Online Retail → AWS → AI/ML ทำให้ revenue diversify และไม่ถูก disrupt"
  },
  {
    q: "ทำไมการกำหนด exit rule ก่อน entry จึงสำคัญมาก?",
    options: ["เพื่อให้ broker รู้ราคาเป้าหมาย", "เพราะถ้าไม่มี exit rule พอตลาดพัง = หนีตายทุกราคา และกำไรที่สะสมมาหายหมด", "เพื่อประหยัดเวลาในการตัดสินใจ", "ตลาด US บังคับให้มี stop loss"],
    answer: 1,
    explain: "ผู้สอนเคยถือหุ้น 10 ตัว กำไร 100%+ แต่ไม่มี exit plan พอตลาดพัง กำไรหายหมด — exit rule ต้องวางก่อน entry"
  },
  {
    q: "EMA ใช้ดีช่วงไหน และไม่ดีช่วงไหน?",
    options: ["ดีตลอด ไม่ว่าตลาดจะเป็นอย่างไร", "ดีช่วง trend ชัด ไม่ดีช่วง sideway", "ดีช่วง sideway ไม่ดีช่วง trend", "ดีเฉพาะตลาด US เท่านั้น"],
    answer: 1,
    explain: "EMA ดีมากช่วงมี trend แต่ส่ง false signal ตลอดช่วง sideway ต้องมี filter เพิ่ม เช่น ADX หรือ volume"
  },
  {
    q: "ทบต้น 10%/เดือน ลงทุน 100,000 บาท ครบ 2 ปี (24 เดือน) มีเท่าไร?",
    options: ["240,000 บาท", "984,973 บาท (~1 ล้าน)", "313,843 บาท", "2,400,000 บาท"],
    answer: 1,
    explain: "24 เดือนที่ 10%/เดือน ทบต้น: 100k × (1.1)^24 ≈ 984,973 บาท นี่คือพลังของ compound interest"
  },
  {
    q: "อ.นัทเปรียบ Options กับการซื้อรถอย่างไร?",
    options: ["ซื้อรถ = เล่น options, ถือหุ้น = ผลาญน้ำมัน", "ซื้อรถ = ถือหุ้น, Options = Config/Package เสริมที่เลือกตามต้องการ", "Options คือเปลี่ยนยี่ห้อรถ, หุ้นคือใช้รถประจำ", "ซื้อรถ = Short options, ถือหุ้น = Long options"],
    answer: 1,
    explain: "อ.นัทอธิบาย: หุ้น = รถพื้นฐาน, options = config เสริม เช่น safety package หรือ performance package ที่เลือกตามความต้องการ"
  },
  {
    q: "Call Spread (Buy Call 110 / Sell Call 115) ต้นทุน $50 มี Max Gain เท่าไร?",
    options: ["ไม่จำกัด", "$100", "$500", "$50"],
    answer: 2,
    explain: "Max gain = (115 - 110) × 100 shares - $50 premium = $500 - $50 = $450 หรือเรียกง่ายๆว่า spread width × 100 - premium"
  }
];

// ─── STATE ───────────────────────────────────────────────────────────────────

const state = {
  done: new Set(JSON.parse(localStorage.getItem("il.done") || "[]")),
  note: localStorage.getItem("il.note") || "",
  cardIndex: 0,
  quizIndex: 0,
  selectedTopic: topics[0].name,
  expandedLesson: null
};

// ─── HELPERS ─────────────────────────────────────────────────────────────────

function saveDone() {
  localStorage.setItem("il.done", JSON.stringify([...state.done]));
}

function lessonById(id) {
  return lessons.find(l => l.id === id);
}

function formatTime(min) {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return h ? `${h} ชม. ${m} นาที` : `${m} นาที`;
}

function tagHtml(cat) {
  return `<span class="tag tag-${cat}">${cat}</span>`;
}

// ─── PROGRESS ────────────────────────────────────────────────────────────────

function updateProgress() {
  const count = state.done.size;
  const pct = Math.round((count / lessons.length) * 100);
  document.querySelector("#overallPct").textContent = `${pct}%`;
  document.querySelector("#progressBar").style.width = `${pct}%`;
  document.querySelector("#doneLessons").textContent = count;
  const next = lessons.find(l => !state.done.has(l.id));
  document.querySelector("#progressHint").textContent = next
    ? `ถัดไป: บท ${next.index} ${next.title}`
    : "ครบทุกบทแล้ว! ทบทวนด้วย quiz";
  renderNextLesson();
}

// ─── DASHBOARD ───────────────────────────────────────────────────────────────

function renderLearningPath() {
  const path = [
    { label: "Foundation", desc: "เปิดโลก + โอกาสตลาด US" },
    { label: "Macro", desc: "ระบบการเงินโลก + Asset Allocation" },
    { label: "Sector", desc: "Tech Stocks + EV Disruption" },
    { label: "Technical", desc: "Momentum MTF + Screener + Backtest" },
    { label: "Options", desc: "4 มิติ → Intermediate → Advanced" }
  ];
  document.querySelector("#learningPath").innerHTML = path
    .map(p => `<li><strong>${p.label}</strong>${p.desc}</li>`)
    .join("");
}

function lessonCardInner(lesson, compact = false) {
  const done = state.done.has(lesson.id);
  return `
    <div class="lesson-topline">
      ${tagHtml(lesson.category)}
      <span class="lesson-meta">บท ${lesson.index} · ${formatTime(lesson.minutes)}</span>
    </div>
    <h3>${lesson.title}</h3>
    <p class="instructor">${lesson.instructor}</p>
    <p>${lesson.focus}</p>
    ${compact ? `<p style="margin-top:8px;"><strong>จำให้ได้:</strong> ${lesson.takeaway}</p>` : ""}
    <div class="lesson-actions">
      <button class="status-btn ${done ? "done" : ""}" data-toggle="${lesson.id}">
        ${done ? "✓ จบแล้ว" : "ติ๊กว่าจบ"}
      </button>
      ${lesson.videoUrl ? `<a class="video-link" href="${lesson.videoUrl}" target="_blank" rel="noopener">▶ ดูวีดีโอ</a>` : ""}
    </div>
  `;
}

function renderNextLesson() {
  const next = lessons.find(l => !state.done.has(l.id)) || lessons[0];
  document.querySelector("#nextLesson").innerHTML = lessonCardInner(next, true);
}

function renderLessons(filter = "") {
  const q = filter.trim().toLowerCase();
  const visible = q
    ? lessons.filter(l => `${l.title} ${l.category} ${l.focus} ${l.takeaway} ${l.instructor}`.toLowerCase().includes(q))
    : lessons;
  document.querySelector("#lessonGrid").innerHTML = visible
    .map(l => `<article class="lesson-card">${lessonCardInner(l)}</article>`)
    .join("");
}

// ─── LESSON DETAIL BUILDER ────────────────────────────────────────────────────

function buildLessonDetail(id) {
  const content = lessonContent[id];
  if (!content) return "";
  const conceptsHtml = content.concepts.map(c => `
    <div class="concept-item">
      <h4>${c.title}</h4>
      <p>${c.body}</p>
    </div>
  `).join("");
  const rulesHtml = content.rules.map(r => `<li>${r}</li>`).join("");
  const numbersHtml = content.numbers.map(n => `<span class="number-chip">${n}</span>`).join("");
  return `
    <div class="lesson-detail" id="detail-${id}">
      <div class="for-you-box">
        <strong>ทำไมบทนี้ถึงสำคัญสำหรับคุณ</strong>
        ${content.forYou}
      </div>
      <div class="detail-section">
        <p class="detail-section-title">แนวคิดหลักที่ต้องเข้าใจ</p>
        <div class="concept-list">${conceptsHtml}</div>
      </div>
      <div class="detail-section">
        <p class="detail-section-title">กฎที่ต้องจำ</p>
        <ul class="rule-list">${rulesHtml}</ul>
      </div>
      <div class="detail-section">
        <p class="detail-section-title">ตัวเลขสำคัญ</p>
        <div class="number-chips">${numbersHtml}</div>
      </div>
    </div>
  `;
}

// ─── ROADMAP ─────────────────────────────────────────────────────────────────

function renderRoadmap() {
  document.querySelector("#roadmapList").innerHTML = lessons.map(l => {
    const done = state.done.has(l.id);
    const isExpanded = state.expandedLesson === l.id;
    return `
      <div class="roadmap-item">
        <div class="roadmap-num ${done ? "done" : ""}">${l.index}</div>
        <div class="roadmap-body">
          <div class="roadmap-header">
            ${tagHtml(l.category)}
            <span style="font-size:12px;color:#64748B;">ep.${l.ep} · ${formatTime(l.minutes)}</span>
          </div>
          <h3>${l.title}</h3>
          <p class="instructor" style="font-size:12px;color:#94A3B8;margin-bottom:6px;">${l.instructor}</p>
          <p class="focus">${l.focus}</p>
          <p class="takeaway"><strong>จำให้ได้:</strong> ${l.takeaway}</p>
          <div class="actions">
            <button class="expand-btn ${isExpanded ? "open" : ""}" data-expand="${l.id}">
              ${isExpanded ? "ซ่อนบทเรียน ↑" : "อ่านบทเรียน ↓"}
            </button>
            <button class="status-btn ${done ? "done" : ""}" data-toggle="${l.id}" style="margin-left:8px;">
              ${done ? "✓ จบแล้ว" : "ติ๊กว่าจบ"}
            </button>
            ${l.videoUrl ? `<a class="video-link" href="${l.videoUrl}" target="_blank" rel="noopener" style="margin-left:8px;">▶ ดูวีดีโอเต็ม</a>` : ""}
          </div>
          ${buildLessonDetail(l.id)}
        </div>
      </div>
    `;
  }).join("");

  // Re-open expanded if any
  if (state.expandedLesson) {
    const detail = document.getElementById(`detail-${state.expandedLesson}`);
    if (detail) detail.classList.add("open");
  }
}

// ─── MIND MAP ─────────────────────────────────────────────────────────────────

function renderMindmap() {
  const canvas = document.querySelector("#mindmapCanvas");
  const w = canvas.offsetWidth || 600;
  const h = canvas.offsetHeight || 500;
  const cx = w / 2;
  const cy = h / 2;
  const radius = Math.min(w, h) * 0.35;

  const svg = document.querySelector("#mapSvg");
  svg.innerHTML = topics.map(t => {
    const rad = (t.angle * Math.PI) / 180;
    const nx = cx + Math.cos(rad) * radius;
    const ny = cy + Math.sin(rad) * radius;
    return `<line x1="${cx}" y1="${cy}" x2="${nx}" y2="${ny}" stroke="${t.color}" stroke-width="2" stroke-dasharray="6 4" opacity="0.4"/>`;
  }).join("");

  document.querySelector("#mapNodes").innerHTML = topics.map(t => {
    const rad = (t.angle * Math.PI) / 180;
    const nx = cx + Math.cos(rad) * radius;
    const ny = cy + Math.sin(rad) * radius;
    const count = t.lessons.length;
    return `
      <button class="map-node"
        style="left:${nx}px;top:${ny}px;border-color:${t.color};"
        data-topic="${t.name}">
        <strong style="color:${t.color};">${t.label}</strong>
        <span>${count} บทเรียน</span>
      </button>
    `;
  }).join("");

  renderTopicPanel(state.selectedTopic);

  document.querySelectorAll(".map-node").forEach(node => {
    node.classList.toggle("active", node.dataset.topic === state.selectedTopic);
  });
}

function renderTopicPanel(topicName) {
  const topic = topics.find(t => t.name === topicName);
  if (!topic) return;
  const topicLessons = topic.lessons.map(lessonById);
  document.querySelector("#topicPanel").innerHTML = `
    <div class="topic-panel-heading">
      <h3 style="color:${topic.color};">${topic.label}</h3>
      <span class="cat-badge tag tag-${topic.name}">${topic.name}</span>
    </div>
    <p class="topic-prompt">${topic.prompt}</p>
    <div class="topic-lesson-list">
      ${topicLessons.map(l => {
        const c = lessonContent[l.id];
        return `
          <div class="topic-lesson-item">
            <h4>บท ${l.index}: ${l.title}</h4>
            <p>${l.takeaway}</p>
            ${c ? `<p style="margin-top:6px;font-size:12px;color:#F97316;">${c.forYou.substring(0, 80)}…</p>` : ""}
          </div>
        `;
      }).join("")}
    </div>
  `;
}

// ─── FLASHCARDS ───────────────────────────────────────────────────────────────

function renderCard(showAnswer = false) {
  const card = cards[state.cardIndex];
  document.querySelector("#cardCounter").textContent =
    `ข้อ ${state.cardIndex + 1} / ${cards.length}`;
  document.querySelector("#fcQuestion").textContent = card.q;
  const ans = document.querySelector("#fcAnswer");
  ans.textContent = card.a;
  ans.classList.toggle("hidden", !showAnswer);
}

// ─── QUIZ ─────────────────────────────────────────────────────────────────────

function renderQuiz() {
  const item = quiz[state.quizIndex];
  document.querySelector("#quizCounter").textContent =
    `ข้อ ${state.quizIndex + 1} / ${quiz.length}`;
  document.querySelector("#quizQuestion").textContent = item.q;
  document.querySelector("#quizFeedback").textContent = "";
  document.querySelector("#quizFeedback").className = "quiz-feedback";
  document.querySelector("#quizOptions").innerHTML = item.options
    .map((opt, i) => `<button class="quiz-opt" data-answer="${i}">${opt}</button>`)
    .join("");
}

// ─── VIEWS ────────────────────────────────────────────────────────────────────

const viewTitles = {
  dashboard: "ภาพรวมการเรียน",
  roadmap: "Roadmap ทั้ง 11 บท",
  mindmap: "Mind Map แกนความรู้",
  review: "ทบทวนให้เข้าหัว",
  quiz: "Quiz ตรวจความเข้าใจ"
};

function switchView(name) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelector(`#${name}View`).classList.add("active");
  document.querySelectorAll(".tab").forEach(t => {
    t.classList.toggle("active", t.dataset.view === name);
  });
  document.querySelector("#viewTitle").textContent = viewTitles[name];
  if (name === "roadmap") renderRoadmap();
  if (name === "mindmap") renderMindmap();
}

// ─── EVENTS ───────────────────────────────────────────────────────────────────

document.addEventListener("click", e => {
  // Nav tab
  const tab = e.target.closest("[data-view]");
  if (tab) { switchView(tab.dataset.view); return; }

  // Toggle lesson done
  const toggle = e.target.closest("[data-toggle]");
  if (toggle) {
    const id = toggle.dataset.toggle;
    state.done.has(id) ? state.done.delete(id) : state.done.add(id);
    saveDone();
    renderLessons(document.querySelector("#searchInput").value);
    renderRoadmap();
    updateProgress();
    return;
  }

  // Expand/collapse lesson detail
  const expandBtn = e.target.closest("[data-expand]");
  if (expandBtn) {
    const id = expandBtn.dataset.expand;
    if (state.expandedLesson === id) {
      state.expandedLesson = null;
    } else {
      state.expandedLesson = id;
    }
    renderRoadmap();
    if (state.expandedLesson) {
      const detail = document.getElementById(`detail-${state.expandedLesson}`);
      if (detail) {
        detail.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }
    return;
  }

  // Mind map node
  const node = e.target.closest("[data-topic]");
  if (node) {
    state.selectedTopic = node.dataset.topic;
    document.querySelectorAll(".map-node").forEach(n => {
      n.classList.toggle("active", n.dataset.topic === state.selectedTopic);
    });
    renderTopicPanel(state.selectedTopic);
    return;
  }

  // Quiz option
  const opt = e.target.closest(".quiz-opt");
  if (opt) {
    const selected = Number(opt.dataset.answer);
    const item = quiz[state.quizIndex];
    document.querySelectorAll(".quiz-opt").forEach(btn => {
      btn.disabled = true;
      const idx = Number(btn.dataset.answer);
      if (idx === item.answer) btn.classList.add("correct");
      if (idx === selected && idx !== item.answer) btn.classList.add("wrong");
    });
    const fb = document.querySelector("#quizFeedback");
    const explain = item.explain || "";
    if (selected === item.answer) {
      fb.textContent = `ถูกต้อง! ${explain}`;
      fb.className = "quiz-feedback correct";
    } else {
      fb.textContent = `ยังไม่ใช่ — ${explain}`;
      fb.className = "quiz-feedback wrong";
    }
    return;
  }
});

document.querySelector("#searchInput").addEventListener("input", e => {
  renderLessons(e.target.value);
});

document.querySelector("#showAnswerBtn").addEventListener("click", () => renderCard(true));

document.querySelector("#nextCardBtn").addEventListener("click", () => {
  state.cardIndex = (state.cardIndex + 1) % cards.length;
  renderCard(false);
});

document.querySelector("#saveNoteBtn").addEventListener("click", () => {
  const note = document.querySelector("#studyNote").value;
  localStorage.setItem("il.note", note);
  const btn = document.querySelector("#saveNoteBtn");
  btn.textContent = "บันทึกแล้ว ✓";
  setTimeout(() => { btn.textContent = "บันทึกโน้ต"; }, 1500);
});

document.querySelector("#nextQuizBtn").addEventListener("click", () => {
  state.quizIndex = (state.quizIndex + 1) % quiz.length;
  renderQuiz();
});

// Restore note
document.querySelector("#studyNote").value = state.note;

// ─── INIT ─────────────────────────────────────────────────────────────────────

document.querySelector("#totalLessons").textContent = lessons.length;
renderLearningPath();
renderLessons();
renderCard(false);
renderQuiz();
updateProgress();
