/**
 * Gmail Organizer — patiphan.injob@gmail.com
 *
 * วิธีรัน:
 * 1. ไป https://script.google.com → New Project
 * 2. วางโค้ดทั้งหมดนี้ลงไปแทนที่ code เดิม
 * 3. (ถ้าต้องการสี) คลิก Services (+) ซ้ายมือ → ค้นหา "Gmail API" → Add
 * 4. กดปุ่ม ▶ Run → เลือก organizeMail
 * 5. อนุญาต permission ครั้งแรก → รอ log ใน Execution Log
 */

// ─── Label definitions ──────────────────────────────────────────────
const LABELS = [
  { key: 'beerUS',   name: '🍺 Beer/📈 หุ้น US',      bg: '#16a766', fg: '#ffffff' },
  { key: 'beerTH',   name: '🍺 Beer/🇹🇭 หุ้นไทย',    bg: '#4986e7', fg: '#ffffff' },
  { key: 'beerTx',   name: '🍺 Beer/🎙️ Transcripts', bg: '#b99aff', fg: '#ffffff' },
  { key: 'beerHW',   name: '🍺 Beer/📚 การบ้าน',       bg: '#ffad47', fg: '#ffffff' },
  { key: 'scrapers', name: '🤖 Scrapers',              bg: '#2da2bb', fg: '#ffffff' },
  { key: 'github',   name: '🔔 GitHub',                bg: '#434343', fg: '#ffffff' },
  { key: 'security', name: '🔒 Security',              bg: '#cc3a21', fg: '#ffffff' },
];

// ─── Search rules (Gmail query syntax) ─────────────────────────────
const RULES = [
  {
    key:   'beerUS',
    query: 'subject:"Beer Daily Report"',
  },
  {
    key:   'beerTH',
    query: 'subject:"Beer หุ้นไทย"',
  },
  {
    key:   'beerTx',
    query: 'subject:"Beer Vanon Transcripts"',
  },
  {
    key:   'beerHW',
    query: 'subject:"Beer การบ้าน"',
  },
  {
    key:   'scrapers',
    // ครอบคลุม: progress reports + start emails ของทั้ง Krasuang และ Bert Manit
    query: 'from:me (subject:Krasuang OR subject:"Bert Manit")',
  },
  {
    key:   'github',
    query: 'from:(notifications@github.com OR noreply@github.com)',
  },
  {
    key:   'security',
    // Facebook security + Google security alerts
    query: 'from:(security@facebookmail.com OR no-reply@accounts.google.com)',
  },
];

// ─── Main ───────────────────────────────────────────────────────────
function organizeMail() {
  Logger.log('🚀 เริ่มจัดระเบียบ Gmail...\n');

  // 1. สร้าง labels (createLabel คืน label เดิมถ้ามีอยู่แล้ว — safe to re-run)
  const labelMap = {};
  for (const def of LABELS) {
    labelMap[def.key] = GmailApp.createLabel(def.name);
  }
  Logger.log('📁 สร้าง labels ครบ ' + LABELS.length + ' หมวด\n');

  // 2. ใส่สี — ต้องการ Gmail API (Services)
  //    ถ้าไม่ได้เปิด Services → ข้ามขั้นตอนนี้ไปโดยอัตโนมัติ
  try {
    for (const def of LABELS) {
      Gmail.Users.Labels.patch(
        { color: { backgroundColor: def.bg, textColor: def.fg } },
        'me',
        labelMap[def.key].getId()
      );
    }
    Logger.log('🎨 ใส่สีเรียบร้อย\n');
  } catch (_) {
    Logger.log('ℹ️  ข้ามการใส่สี (เปิด Services → Gmail API ก่อน ถ้าต้องการ)\n');
  }

  // 3. Label threads ที่มีอยู่ใน inbox ทั้งหมด
  Logger.log('📨 กำลัง label threads...');
  let total = 0;
  for (const rule of RULES) {
    const label = labelMap[rule.key];
    let start = 0, count = 0;
    while (true) {
      const threads = GmailApp.search(rule.query, start, 50);
      if (!threads.length) break;
      threads.forEach(t => t.addLabel(label));
      count  += threads.length;
      start  += threads.length;
      if (threads.length < 50) break;
    }
    Logger.log(`  ✅ ${rule.key.padEnd(10)} → ${count} threads`);
    total += count;
  }

  Logger.log('\n🎉 เสร็จ! จัดหมวดหมู่ ' + total + ' threads ทั้งหมด');
  Logger.log('💡 Tip: รัน script นี้ซ้ำได้ทุกสัปดาห์ จะ label เฉพาะอีเมลใหม่ที่ยังไม่มี label');
}
