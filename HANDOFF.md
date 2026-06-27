# Session Handoff - Fullscreen Charts & Precision Hit-Testing Deployed

## Latest Truth
- **v2.6.0 Deployed**: อัพเดตฟังก์ชันกราฟหน้าแรกครั้งใหญ่แบบครบวงจร
- **ระบบขยายกราฟ (Fullscreen Chart Modal)**: เพิ่มปุ่ม `⤢` ขยายกราฟที่มุมซ้ายบนของทุกหน้าต่างกราฟ (ดัชนีตลาดและหุ้นรายตัว) แสดงผลหน้าต่างป๊อปอัปใหญ่สไตล์ iOS (Backdrop-filter blur 16px, spring scale animation, click-outside-to-close)
- **ระบบตรวจจับพิกัดแท่งเทียนอัจฉริยะ (Precision Hit-Testing)**: เพิ่มแกน Y ในการหาพิกัด (`hitTestCandle()`) ทำให้การจ่อเมาส์ (Hover) หรือสัมผัส (Touch) ทริกเกอร์ Tooltip เฉพาะเมื่ออยู่บนพื้นที่แกนของแท่งเทียนจริงๆ ไม่เด้งรบกวนเมื่อชี้บริเวณพื้นที่ว่าง
- **ปรับปรุง Touch Screen**: รองรับการลากนิ้ว (TouchMove) บนมือถือเพื่อเลื่อนดูข้อมูลแท่งเทียนแบบเรียลไทม์
- **แก้ไขเลเยอร์การแสดงผล (Z-Index Fix)**: ปรับ `z-index` ของกล่อง Tooltip จาก `1500` เป็น `2500` เพื่อให้แสดงผลทับหน้าต่างกราฟ fullscreen เสมอ

## Files Changed
- `docs/index.html`:
  - เพิ่ม CSS ส่วนของ `.chart-expand-btn` และ `.chart-fullscreen-overlay`
  - เพิ่มปุ่มขยายกราฟลงใน HTML template ของดัชนีและหุ้นรายตัว
  - เพิ่ม JS ฟังก์ชัน `hitTestCandle()`, `openExpandedChart()`, `bindExpandedChartEvents()`, และ `closeExpandedChart()`
  - อัปเดตอีเวนต์ `mousemove`, `click`, `touchmove`, `touchend` ของกราฟทั้งตัวเล็กและตัวใหญ่ให้ใช้ `hitTestCandle()`
  - อัปเดตเวอร์ชันบนหน้าเว็บบนซ้ายเป็น `v2.6.0` พร้อม Changelog ใน Tooltip
- `docs/sw.js`:
  - อัปเดต `CACHE_NAME` แคชบราว์เซอร์เป็น `beer-top100-v20260627-candlestick-3d-glow-v17` เพื่ออัปเดตไฟล์ให้ผู้ใช้ทันที

## Verification
- ทดสอบตรวจสอบไวยากรณ์ด้วย Node.js และไม่พบข้อผิดพลาด (`SYNTAX OK`)
- ทดสอบ Git commit & push ขึ้นเซิร์ฟเวอร์เรียบร้อยดี

## Open Risks
- ไม่มี

## Next Step
- พัฒนาหรือปรับแต่งระบบ Trading Journal, Note, หรือ RAG-Knowledge Base เพิ่มเติมตามความต้องการถัดไป
