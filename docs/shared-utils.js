/**
 * Shared Utilities for Beer Top 100 System (Loaded globally)
 */

// HTML Escaping
function esc(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Thai Date Formatting
function fmtDate(d) {
  if (!d) return '';
  const parts = d.split('-');
  if (parts.length === 3) {
    const months = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
    const year = parseInt(parts[0]) + 543;
    return `${parseInt(parts[2])} ${months[parseInt(parts[1]) - 1]} ${year}`;
  }
  return d;
}

// Money Formatting
function fmtMoney(value) {
  if (value === null || value === undefined || isNaN(value)) return '-';
  return '$' + Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Emotion detection and coloring
const DEFAULT_EMOTIONS = [
  'กลัว', 'กังวล', 'ระแวง', 'ท้อแท้', 'เหนื่อยล้า',
  'โลภ', 'FOMO', 'หัวร้อน/อยากเอาคืน', 'มั่นใจเกินไป',
  'มั่นใจแต่ระวัง', 'มีวินัย', 'สบายใจ/ใจเย็น',
  'ลังเล', 'สับสน', 'ใจเย็นรอ', 'ไม่เชื่อข่าว', 'เสียดาย'
];

const DEFAULT_EMOTION_COLORS = {
  'กลัว': '#b71c1c',
  'กังวล': '#f06292',
  'ระแวง': '#9e9d24',
  'ท้อแท้': '#5c4033',
  'เหนื่อยล้า': '#78909c',
  'หัวร้อน/อยากเอาคืน': '#ff1744',
  'โลภ': '#ffd700',
  'FOMO': '#00e5ff',
  'มั่นใจเกินไป': '#d500f9',
  'เสียดาย': '#311b92',
  'มั่นใจแต่ระวัง': '#00897b',
  'มีวินัย': '#00e676',
  'สบายใจ/ใจเย็น': '#0288d1',
  'ลังเล': '#ffea00',
  'สับสน': '#e65100',
  'ใจเย็นรอ': '#ff9100',
  'ไม่เชื่อข่าว': '#7986cb'
};

function getCustomEmotionsList() {
  try {
    const raw = localStorage.getItem('BEER_CUSTOM_EMOTIONS');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        const combined = [...DEFAULT_EMOTIONS];
        parsed.forEach(item => {
          if (item && !combined.includes(item)) {
            combined.push(item);
          }
        });
        return combined;
      }
    }
  } catch (e) {}
  return DEFAULT_EMOTIONS;
}

function getCustomEmotionColorsMap() {
  try {
    const raw = localStorage.getItem('BEER_CUSTOM_EMOTION_COLORS');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object') {
        return Object.assign({}, DEFAULT_EMOTION_COLORS, parsed);
      }
    }
  } catch (e) {}
  return DEFAULT_EMOTION_COLORS;
}

function syncCustomEmotionsFromNotes(notes) {
  if (!notes) return false;
  let updated = false;
  if (Array.isArray(notes._custom_emotions) && notes._custom_emotions.length > 0) {
    localStorage.setItem('BEER_CUSTOM_EMOTIONS', JSON.stringify(notes._custom_emotions));
    updated = true;
  }
  if (notes._custom_emotion_colors && typeof notes._custom_emotion_colors === 'object' && Object.keys(notes._custom_emotion_colors).length > 0) {
    localStorage.setItem('BEER_CUSTOM_EMOTION_COLORS', JSON.stringify(notes._custom_emotion_colors));
    updated = true;
  }
  return updated;
}

function getNextDateString(dateStr) {
  const d = new Date(dateStr + 'T12:00:00');
  d.setDate(d.getDate() + 1);
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

function getTradingDaysList(rawDates) {
  const dates = [];
  rawDates.forEach(dStr => {
    const d = new Date(dStr + 'T12:00:00');
    const dow = d.getDay(); // 6 = Saturday, 0 = Sunday
    let targetDate = dStr;
    if (dow === 6) {
      const prev = new Date(d);
      prev.setDate(d.getDate() - 1);
      targetDate = prev.getFullYear() + '-' + String(prev.getMonth() + 1).padStart(2, '0') + '-' + String(prev.getDate()).padStart(2, '0');
    } else if (dow === 0) {
      const prev = new Date(d);
      prev.setDate(d.getDate() - 2);
      targetDate = prev.getFullYear() + '-' + String(prev.getMonth() + 1).padStart(2, '0') + '-' + String(prev.getDate()).padStart(2, '0');
    }
    if (!dates.includes(targetDate)) dates.push(targetDate);
  });
  return dates;
}

function detectEmotion(note, mode = 'personal') {
  if (!note) return null;
  if (note.journal) {
    if (mode === 'market' && note.journal.market_emotion) {
      return note.journal.market_emotion;
    }
    if (note.journal.emotion) {
      return note.journal.emotion;
    }
  }
  if (note.note) {
    const emotionsList = getCustomEmotionsList();
    for (const em of emotionsList) {
      if (note.note.includes(em)) return em;
    }
  }
  return null;
}

async function forceUpdateApp() {
  try {
    if ('serviceWorker' in navigator) {
      const registrations = await navigator.serviceWorker.getRegistrations();
      for (const reg of registrations) {
        await reg.unregister();
      }
    }
    if ('caches' in window) {
      const keys = await caches.keys();
      for (const key of keys) {
        await caches.delete(key);
      }
    }
  } catch (e) {
    console.warn('Clear cache error:', e);
  }
  window.location.href = window.location.origin + window.location.pathname + '?nocache=' + Date.now();
}

function getEmotionCategory(emotion) {
  if (!emotion) return 'default';
  const fear = ['กลัว', 'กังวล', 'ระแวง', 'ท้อแท้', 'เหนื่อยล้า'];
  const confident = ['มั่นใจแต่ระวัง', 'มีวินัย', 'สบายใจ/ใจเย็น'];
  const hesitant = ['ลังเล', 'สับสน', 'ใจเย็นรอ', 'ไม่เชื่อข่าว', 'เสียดาย'];
  const greed = ['โลภ', 'FOMO', 'หัวร้อน/อยากเอาคืน', 'มั่นใจเกินไป'];
  
  if (fear.includes(emotion)) return 'fear';
  if (confident.includes(emotion)) return 'confident';
  if (hesitant.includes(emotion)) return 'hesitant';
  if (greed.includes(emotion)) return 'greed';
  return 'default';
}

function getEmotionColor(emotion) {
  if (!emotion) return '#8b949e';
  const colorsMap = getCustomEmotionColorsMap();
  if (colorsMap[emotion]) return colorsMap[emotion];
  
  // fuzzy matches if needed
  const fear = ['กลัว', 'กังวล', 'ระแวง', 'ท้อแท้', 'เหนื่อยล้า'];
  const confident = ['มั่นใจแต่ระวัง', 'มีวินัย', 'สบายใจ/ใจเย็น'];
  const hesitant = ['ลังเล', 'สับสน', 'ใจเย็นรอ', 'ไม่เชื่อข่าว', 'เสียดาย'];
  const greed = ['โลภ', 'FOMO', 'หัวร้อน/อยากเอาคืน', 'มั่นใจเกินไป'];
  
  if (fear.includes(emotion)) return '#b71c1c';
  if (confident.includes(emotion)) return '#00e676';
  if (hesitant.includes(emotion)) return '#ffea00';
  if (greed.includes(emotion)) return '#ffd700';
  return '#8b949e';
}


function renderEmotionBadge(label, emotion) {
  if (!emotion) return '';
  const color = getEmotionColor(emotion);
  const bg = color + '26'; // 15% opacity hex
  const border = color + '40'; // 25% opacity hex
  return `<span class="journal-badge" style="background:${bg}; color:${color}; border:1px solid ${border}; font-weight:bold;">${esc(label)}: ${esc(emotion)}</span>`;
}

// Note Parser
function parseNoteText(noteText) {
  if (!noteText) return { text: '' };
  
  const thesisMatch = noteText.match(/Thesis:\s*([\s\S]*?)(?=(?:If wrong:|Risk:|Review:|$))/i);
  const wrongMatch = noteText.match(/If wrong:\s*([\s\S]*?)(?=(?:Thesis:|Risk:|Review:|$))/i);
  const riskMatch = noteText.match(/Risk:\s*([\s\S]*?)(?=(?:Thesis:|If wrong:|Review:|$))/i);
  const reviewMatch = noteText.match(/Review:\s*([\s\S]*?)(?=(?:Thesis:|If wrong:|Risk:|$))/i);

  if (!thesisMatch && !wrongMatch && !riskMatch && !reviewMatch) {
    let cleanText = noteText;
    if (cleanText.trim().startsWith('[')) {
      const closingBracket = cleanText.indexOf(']');
      if (closingBracket !== -1) {
        cleanText = cleanText.substring(closingBracket + 1).trim();
      }
    }
    cleanText = cleanText.replace(/RRR:\s*1:[\d.]+\s*\(Entry:[\s\S]*?\)/gi, '').trim();
    return { text: cleanText };
  }

  return {
    thesis: thesisMatch ? thesisMatch[1].trim() : null,
    wrong: wrongMatch ? wrongMatch[1].trim() : null,
    risk: riskMatch ? riskMatch[1].trim() : null,
    review: reviewMatch ? reviewMatch[1].trim() : null
  };
}

// Note body layout (with label wrapper)
function renderJournalNoteBody(n) {
  let journalBadges = '';
  let planCard = '';
  let thoughtsHtml = '';
  
  if (n.journal) {
    const intentLabels = { 'ซื้อ': 'ซื้อ', 'ขาย': 'ขาย', 'ถือ': 'ถือ', 'รอจังหวะ': 'รอจังหวะ' };
    const intentText = intentLabels[n.journal.intent] || n.journal.intent || '';
    
    const setupText = n.journal.setup || '';
    const outcomeVal = n.journal.outcome || 'None';
    let outcomeBadgeHtml = '';
    if (outcomeVal !== 'None' && outcomeVal !== null) {
      const outcomeLabels = {
        'Open': '⏳ ยังถือ (Open)',
        'Big Win': '🏆 Big Win',
        'Small Win': '🟢 Small Win',
        'Breakeven': '🟡 เท่าทุน',
        'Small Loss': '🟠 คัทในแผน',
        'Big Loss': '🔴 ขาดทุนเกินแผน'
      };
      const outcomeText = outcomeLabels[outcomeVal] || outcomeVal;
      
      let outcomeClass = 'outcome-open';
      if (outcomeVal.includes('Win')) outcomeClass = 'outcome-win';
      else if (outcomeVal.includes('Loss')) outcomeClass = 'outcome-loss';
      else if (outcomeVal.includes('Breakeven') || outcomeVal.includes('เท่าทุน')) outcomeClass = 'outcome-draw';
      outcomeBadgeHtml = `<span class="journal-badge ${outcomeClass}">${esc(outcomeText)}</span>`;
    }

    journalBadges = `
      <div class="journal-badge-section" style="display:flex; gap:6px; margin:4px 0 8px 0; flex-wrap:wrap;">
        ${renderEmotionBadge('😊 ส่วนตัว', n.journal.emotion)}
        ${renderEmotionBadge('👥 ตลาด', n.journal.market_emotion)}
        ${intentText ? `<span class="journal-badge action">${esc(intentText)}</span>` : ''}
        ${n.journal.confidence ? `<span class="journal-badge confidence">ความมั่นใจ ${esc(n.journal.confidence)}/10</span>` : ''}
        ${setupText ? `<span class="journal-badge setup-badge">${esc(setupText)}</span>` : ''}
        ${n.journal.rrr ? `<span class="journal-badge setup-badge">RRR: 1:${esc(n.journal.rrr)}</span>` : ''}
        ${outcomeBadgeHtml}
      </div>
    `;

    const entryText = n.journal.entryPrice ? `Entry: ${esc(n.journal.entryPrice)}` : '';
    const targetText = n.journal.targetPrice ? `Target: ${esc(n.journal.targetPrice)}` : '';
    const stopText = n.journal.stopLoss ? `SL: ${esc(n.journal.stopLoss)}` : '';
    const gridItems = [entryText, targetText, stopText].filter(Boolean);

    if (gridItems.length > 0) {
      planCard = `
        <div class="tt-plan-card" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255, 255, 255, 0.08); border-radius:8px; padding:10px; margin-top:8px; margin-bottom:8px;">
          <div class="tt-plan-grid" style="display:grid; grid-template-columns:repeat(3, 1fr); gap:8px; text-align:center; border-bottom:1px dashed rgba(255,255,255,0.08); padding-bottom:8px; margin-bottom:8px;">
            <div class="tt-plan-col" style="display:flex; flex-direction:column; gap:2px;"><span style="font-size:9px; color:#8b949e;">ENTRY</span><span style="font-size:12px; font-weight:bold; color:#e6edf3;">${n.journal.entryPrice || '-'}</span></div>
            <div class="tt-plan-col" style="display:flex; flex-direction:column; gap:2px;"><span style="font-size:9px; color:#8b949e;">TARGET</span><span style="font-size:12px; font-weight:bold; color:#26a69a;">${n.journal.targetPrice || '-'}</span></div>
            <div class="tt-plan-col" style="display:flex; flex-direction:column; gap:2px;"><span style="font-size:9px; color:#8b949e;">STOP LOSS</span><span style="font-size:12px; font-weight:bold; color:#ef5350;">${n.journal.stopLoss || '-'}</span></div>
          </div>
          ${n.journal.rrr ? `<div style="text-align:center; font-size:10px; color:#f0b90b; font-weight:bold;">Reward to Risk Ratio (RRR) &nbsp; 1 : ${esc(n.journal.rrr)}</div>` : ''}
        </div>
      `;
    }
  }

  const parsed = parseNoteText(n.note || '');
  if (parsed.thesis || parsed.wrong || parsed.risk || parsed.review) {
    thoughtsHtml = `
      ${parsed.thesis ? `
      <div class="tt-thought-box thesis" style="border-left: 3px solid #58a6ff; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
        <div class="tt-thought-title" style="font-size: 10px; color: #58a6ff; font-weight: bold; margin-bottom: 2px;">🎯 แนวคิดเชิงกลยุทธ์ (Thesis)</div>
        <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.thesis)}</div>
      </div>` : ''}
      ${parsed.wrong ? `
      <div class="tt-thought-box wrong" style="border-left: 3px solid #ef5350; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
        <div class="tt-thought-title" style="font-size: 10px; color: #ef5350; font-weight: bold; margin-bottom: 2px;">⚠️ จุดยอมรับความพ่ายแพ้ (If Wrong)</div>
        <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.wrong)}</div>
      </div>` : ''}
      ${parsed.risk ? `
      <div class="tt-thought-box risk" style="border-left: 3px solid #fabb2e; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
        <div class="tt-thought-title" style="font-size: 10px; color: #fabb2e; font-weight: bold; margin-bottom: 2px;">⚡ ความเสี่ยงที่เฝ้าระวัง (Risk Factors)</div>
        <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.risk)}</div>
      </div>` : ''}
      ${parsed.review ? `
      <div class="tt-thought-box review" style="border-left: 3px solid #8b949e; background: rgba(255,255,255,0.01); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
        <div class="tt-thought-title" style="font-size: 10px; color: #8b949e; font-weight: bold; margin-bottom: 2px;">⏱️ กลับมาทบทวน (Review)</div>
        <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.review)}</div>
      </div>` : ''}
    `;
  } else {
    thoughtsHtml = `<div class="tt-text" style="white-space: pre-wrap; word-break: break-word; margin-top: 4px; font-size: 12px; line-height: 1.45;">${esc(parsed.text || n.note || '')}</div>`;
  }

  const phaseLabels = {
    'premarket': 'ก่อนตลาดเปิด',
    'midday': 'ระหว่างวัน',
    'postmarket': 'หลังตลาดปิด',
    'legacy': 'ทั่วไป'
  };
  const noteDateStr = n.date ? fmtDate(n.date) : '';
  const phaseText = n.archive_phase ? (phaseLabels[n.archive_phase] || n.archive_phase) : '';
  const timeText = n.time ? `เวลา ${esc(n.time)} น.` : '';
  const metaParts = [noteDateStr, phaseText, timeText].filter(Boolean);
  const metaStr = metaParts.length > 0 ? ` - ${metaParts.join(' · ')}` : '';

  return `
    <div class="tt-section">
      <div class="tt-label">📝 บันทึกเทรดส่วนตัว${metaStr}</div>
      ${journalBadges}
      ${planCard}
      ${thoughtsHtml}
    </div>
  `;
}

// Note body layout (without wrapper)
function renderJournalNoteCard(n) {
  let journalBadges = '';
  let planCard = '';
  let thoughtsHtml = '';
  
  if (n.journal) {
    const intentLabels = { 'ซื้อ': 'ซื้อ', 'ขาย': 'ขาย', 'ถือ': 'ถือ', 'รอจังหวะ': 'รอจังหวะ' };
    const intentText = intentLabels[n.journal.intent] || n.journal.intent || '';
    
    const setupText = n.journal.setup || '';
    const outcomeVal = n.journal.outcome || 'None';
    let outcomeBadgeHtml = '';
    if (outcomeVal !== 'None' && outcomeVal !== null) {
      const outcomeLabels = {
        'Open': '⏳ ยังถือ (Open)',
        'Big Win': '🏆 Big Win',
        'Small Win': '🟢 Small Win',
        'Breakeven': '🟡 เท่าทุน',
        'Small Loss': '🟠 คัทในแผน',
        'Big Loss': '🔴 ขาดทุนเกินแผน'
      };
      const outcomeText = outcomeLabels[outcomeVal] || outcomeVal;
      
      let outcomeClass = 'outcome-open';
      if (outcomeVal.includes('Win')) outcomeClass = 'outcome-win';
      else if (outcomeVal.includes('Loss')) outcomeClass = 'outcome-loss';
      else if (outcomeVal.includes('Breakeven') || outcomeVal.includes('เท่าทุน')) outcomeClass = 'outcome-draw';
      outcomeBadgeHtml = `<span class="journal-badge ${outcomeClass}">${esc(outcomeText)}</span>`;
    }

    const phaseLabels = {
      'premarket': 'ก่อนตลาดเปิด',
      'midday': 'ระหว่างวัน',
      'postmarket': 'หลังตลาดปิด',
      'legacy': 'ทั่วไป'
    };
    const phaseText = n.archive_phase ? (phaseLabels[n.archive_phase] || n.archive_phase) : '';

    journalBadges = `
      <div class="journal-badge-section" style="display:flex; gap:6px; margin:4px 0 8px 0; flex-wrap:wrap;">
        ${phaseText ? `<span class="journal-badge phase-badge" style="background:rgba(88, 166, 255, 0.15); color:#58a6ff; border:1px solid rgba(88, 166, 255, 0.25); font-weight:bold;">${esc(phaseText)}</span>` : ''}
        ${renderEmotionBadge('😊 ส่วนตัว', n.journal.emotion)}
        ${renderEmotionBadge('👥 ตลาด', n.journal.market_emotion)}
        ${intentText ? `<span class="journal-badge action">${esc(intentText)}</span>` : ''}
        ${n.journal.confidence ? `<span class="journal-badge confidence">ความมั่นใจ ${esc(n.journal.confidence)}/10</span>` : ''}
        ${setupText ? `<span class="journal-badge setup-badge">${esc(setupText)}</span>` : ''}
        ${n.journal.rrr ? `<span class="journal-badge setup-badge">RRR: 1:${esc(n.journal.rrr)}</span>` : ''}
        ${outcomeBadgeHtml}
      </div>
    `;

    const entryText = n.journal.entryPrice ? `Entry: ${esc(n.journal.entryPrice)}` : '';
    const targetText = n.journal.targetPrice ? `Target: ${esc(n.journal.targetPrice)}` : '';
    const stopText = n.journal.stopLoss ? `SL: ${esc(n.journal.stopLoss)}` : '';
    const gridItems = [entryText, targetText, stopText].filter(Boolean);

    if (gridItems.length > 0) {
      planCard = `
        <div class="tt-plan-card" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255, 255, 255, 0.08); border-radius:8px; padding:10px; margin-top:8px; margin-bottom:8px;">
          <div class="tt-plan-grid" style="display:grid; grid-template-columns:repeat(3, 1fr); gap:8px; text-align:center; border-bottom:1px dashed rgba(255,255,255,0.08); padding-bottom:8px; margin-bottom:8px;">
            <div class="tt-plan-col" style="display:flex; flex-direction:column; gap:2px;"><span style="font-size:9px; color:#8b949e;">ENTRY</span><span style="font-size:12px; font-weight:bold; color:#e6edf3;">${n.journal.entryPrice || '-'}</span></div>
            <div class="tt-plan-col" style="display:flex; flex-direction:column; gap:2px;"><span style="font-size:9px; color:#8b949e;">TARGET</span><span style="font-size:12px; font-weight:bold; color:#26a69a;">${n.journal.targetPrice || '-'}</span></div>
            <div class="tt-plan-col" style="display:flex; flex-direction:column; gap:2px;"><span style="font-size:9px; color:#8b949e;">STOP LOSS</span><span style="font-size:12px; font-weight:bold; color:#ef5350;">${n.journal.stopLoss || '-'}</span></div>
          </div>
          ${n.journal.rrr ? `<div style="text-align:center; font-size:10px; color:#f0b90b; font-weight:bold;">Reward to Risk Ratio (RRR) &nbsp; 1 : ${esc(n.journal.rrr)}</div>` : ''}
        </div>
      `;
    }
  }

  const parsed = parseNoteText(n.note || '');
  if (parsed.thesis || parsed.wrong || parsed.risk || parsed.review) {
    thoughtsHtml = `
      ${parsed.thesis ? `
      <div class="tt-thought-box thesis" style="border-left: 3px solid #58a6ff; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
        <div class="tt-thought-title" style="font-size: 10px; color: #58a6ff; font-weight: bold; margin-bottom: 2px;">🎯 แนวคิดเชิงกลยุทธ์ (Thesis)</div>
        <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.thesis)}</div>
      </div>` : ''}
      ${parsed.wrong ? `
      <div class="tt-thought-box wrong" style="border-left: 3px solid #ef5350; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
        <div class="tt-thought-title" style="font-size: 10px; color: #ef5350; font-weight: bold; margin-bottom: 2px;">⚠️ จุดยอมรับความพ่ายแพ้ (If Wrong)</div>
        <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.wrong)}</div>
      </div>` : ''}
      ${parsed.risk ? `
      <div class="tt-thought-box risk" style="border-left: 3px solid #fabb2e; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
        <div class="tt-thought-title" style="font-size: 10px; color: #fabb2e; font-weight: bold; margin-bottom: 2px;">⚡ ความเสี่ยงที่เฝ้าระวัง (Risk Factors)</div>
        <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.risk)}</div>
      </div>` : ''}
      ${parsed.review ? `
      <div class="tt-thought-box review" style="border-left: 3px solid #8b949e; background: rgba(255,255,255,0.01); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
        <div class="tt-thought-title" style="font-size: 10px; color: #8b949e; font-weight: bold; margin-bottom: 2px;">⏱️ กลับมาทบทวน (Review)</div>
        <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.review)}</div>
      </div>` : ''}
    `;
  } else {
    thoughtsHtml = `<div class="tt-text" style="white-space: pre-wrap; word-break: break-word; margin-top: 4px; font-size: 12px; line-height: 1.45;">${esc(parsed.text || n.note || '')}</div>`;
  }

  return `
    <div class="journal-card-body" style="width: 100%;">
      ${journalBadges}
      ${planCard}
      ${thoughtsHtml}
    </div>
  `;
}

// Ch34 analysis parser
function parseBeerAnalysis(text) {
  if (!text) return null;
  const cleaned = text.replace(/Beer\s+มองว่า\s*:?\s*/gi, '').trim();
  
  const businessMatch = cleaned.match(/(?:•?\s*(?:ธุรกิจ|Business Angle|Business|1\.)\s*(?::|\s)\s*)([\s\S]*?)(?=(?:•?\s*(?:ตัวเลข|Valuation|Numbers|2\.)|•?\s*(?:การสื่อสาร|Communication|3\.)|•?\s*(?:คู่แข่ง|Competitors|4\.)|•?\s*(?:ผู้บริหาร|Management|5\.)|•?\s*(?:แผนของเรา|Our Strategy|Plan|6\.)|$))/i);
  const numbersMatch = cleaned.match(/(?:•?\s*(?:ตัวเลข|Valuation|Numbers|2\.)\s*(?::|\s)\s*)([\s\S]*?)(?=(?:•?\s*(?:ธุรกิจ|Business Angle|Business|1\.)|•?\s*(?:การสื่อสาร|Communication|3\.)|•?\s*(?:คู่แข่ง|Competitors|4\.)|•?\s*(?:ผู้บริหาร|Management|5\.)|•?\s*(?:แผนของเรา|Our Strategy|Plan|6\.)|$))/i);
  const commsMatch = cleaned.match(/(?:•?\s*(?:การสื่อสาร|Communication|3\.)\s*(?::|\s)\s*)([\s\S]*?)(?=(?:•?\s*(?:ธุรกิจ|Business Angle|Business|1\.)|•?\s*(?:ตัวเลข|Valuation|Numbers|2\.)|•?\s*(?:คู่แข่ง|Competitors|4\.)|•?\s*(?:ผู้บริหาร|Management|5\.)|•?\s*(?:แผนของเรา|Our Strategy|Plan|6\.)|$))/i);
  const competitorsMatch = cleaned.match(/(?:•?\s*(?:คู่แข่ง|Competitors|4\.)\s*(?::|\s)\s*)([\s\S]*?)(?=(?:•?\s*(?:ธุรกิจ|Business Angle|Business|1\.)|•?\s*(?:ตัวเลข|Valuation|Numbers|2\.)|•?\s*(?:การสื่อสาร|Communication|3\.)|•?\s*(?:ผู้บริหาร|Management|5\.)|•?\s*(?:แผนของเรา|Our Strategy|Plan|6\.)|$))/i);
  const managementMatch = cleaned.match(/(?:•?\s*(?:ผู้บริหาร|Management|5\.)\s*(?::|\s)\s*)([\s\S]*?)(?=(?:•?\s*(?:ธุรกิจ|Business Angle|Business|1\.)|•?\s*(?:ตัวเลข|Valuation|Numbers|2\.)|•?\s*(?:การสื่อสาร|Communication|3\.)|•?\s*(?:คู่แข่ง|Competitors|4\.)|•?\s*(?:แผนของเรา|Our Strategy|Plan|6\.)|$))/i);
  const planMatch = cleaned.match(/(?:•?\s*(?:แผนของเรา|Our Strategy|Plan|6\.)\s*(?::|\s)\s*)([\s\S]*?)(?=(?:•?\s*(?:ธุรกิจ|Business Angle|Business|1\.)|•?\s*(?:ตัวเลข|Valuation|Numbers|2\.)|•?\s*(?:การสื่อสาร|Communication|3\.)|•?\s*(?:คู่แข่ง|Competitors|4\.)|•?\s*(?:ผู้บริหาร|Management|5\.)|$))/i);

  if (!businessMatch && !numbersMatch && !commsMatch && !competitorsMatch && !managementMatch && !planMatch) {
    return null;
  }

  return {
    business: businessMatch ? businessMatch[1].trim() : null,
    numbers: numbersMatch ? numbersMatch[1].trim() : null,
    comms: commsMatch ? commsMatch[1].trim() : null,
    competitors: competitorsMatch ? competitorsMatch[1].trim() : null,
    management: managementMatch ? managementMatch[1].trim() : null,
    plan: planMatch ? planMatch[1].trim() : null
  };
}

// Ch34 Analysis renderer
function renderBeerAnalysis(analysisText, customLabel) {
  if (!analysisText) return '';
  const cleaned = analysisText.replace(/Beer\s+มองว่า\s*:?\s*/gi, '').trim();
  const parsed = parseBeerAnalysis(cleaned);
  
  const labelHtml = customLabel !== null ? `<div class="tt-label beer">${esc(customLabel || '🧭 Beer วิเคราะห์ Ch34 เจาะลึก:')}</div>` : '';
  
  if (parsed) {
    return `
      <div class="tt-section" style="margin-top: 10px; width: 100%;">
        ${labelHtml}
        ${parsed.business ? `
        <div class="tt-thought-box beer-business" style="border-left: 3px solid #58a6ff; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
          <div class="tt-thought-title" style="font-size: 10px; color: #58a6ff; font-weight: bold; margin-bottom: 2px;">🏢 ธุรกิจ (Business Angle)</div>
          <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.business)}</div>
        </div>` : ''}
        ${parsed.numbers ? `
        <div class="tt-thought-box beer-numbers" style="border-left: 3px solid #79c0ff; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
          <div class="tt-thought-title" style="font-size: 10px; color: #79c0ff; font-weight: bold; margin-bottom: 2px;">📊 ตัวเลข (Numbers / Valuation)</div>
          <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.numbers)}</div>
        </div>` : ''}
        ${parsed.comms ? `
        <div class="tt-thought-box beer-comms" style="border-left: 3px solid #ff7b72; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
          <div class="tt-thought-title" style="font-size: 10px; color: #ff7b72; font-weight: bold; margin-bottom: 2px;">📢 การสื่อสาร (Communication)</div>
          <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.comms)}</div>
        </div>` : ''}
        ${parsed.competitors ? `
        <div class="tt-thought-box beer-competitors" style="border-left: 3px solid #ea60ff; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
          <div class="tt-thought-title" style="font-size: 10px; color: #ea60ff; font-weight: bold; margin-bottom: 2px;">⚔️ คู่แข่ง (Competitors)</div>
          <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.competitors)}</div>
        </div>` : ''}
        ${parsed.management ? `
        <div class="tt-thought-box beer-management" style="border-left: 3px solid #d2a8ff; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
          <div class="tt-thought-title" style="font-size: 10px; color: #d2a8ff; font-weight: bold; margin-bottom: 2px;">👤 ผู้บริหาร (Management)</div>
          <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.management)}</div>
        </div>` : ''}
        ${parsed.plan ? `
        <div class="tt-thought-box beer-plan" style="border-left: 3px solid #ffca28; background: rgba(255,255,255,0.02); border-radius: 4px; padding: 6px 8px; margin-bottom: 6px;">
          <div class="tt-thought-title" style="font-size: 10px; color: #ffca28; font-weight: bold; margin-bottom: 2px;">💡 แผนของเรา (Our Strategy)</div>
          <div class="tt-thought-text" style="font-size: 11px; line-height: 1.4;">${esc(parsed.plan)}</div>
        </div>` : ''}
      </div>
    `;
  }
  
  return `
    <div class="tt-section">
      ${labelHtml}
      <div class="tt-text" style="word-break: break-word; white-space: pre-wrap;">${esc(cleaned)}</div>
    </div>
  `;
}
