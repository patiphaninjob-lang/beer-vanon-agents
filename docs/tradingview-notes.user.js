// ==UserScript==
// @name         🍺 Beer Vanon Notes on TradingView
// @namespace    https://patiphaninjob-lang.github.io/beer-vanon-agents/
// @version      1.9.4
// @description  แสดงโน้ต/วิเคราะห์/ข่าว Beer Vanon ของหุ้นที่คุณเคยใส่มุมมองไว้ บนกราฟ TradingView
// @author       Patiphan
// @match        https://*.tradingview.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM.xmlHttpRequest
// @grant        GM_setClipboard
// @connect      raw.githubusercontent.com
// @connect      githubusercontent.com
// @run-at       document-end
// @updateURL    https://patiphaninjob-lang.github.io/beer-vanon-agents/tradingview-notes.user.js
// @downloadURL  https://patiphaninjob-lang.github.io/beer-vanon-agents/tradingview-notes.user.js
// ==/UserScript==

(function () {
  'use strict';

  const REPO = 'patiphaninjob-lang/beer-vanon-agents';
  const RAW  = `https://raw.githubusercontent.com/${REPO}/main/docs`;

  let notesCache  = null;
  let dailyCache  = {};
  let currentTicker = null;
  let panelOpen   = false;
  let lastNotesLoadAt = 0;
  const NOTES_TTL = 60_000; // refresh notes ทุก 1 นาที
  let markersTicker = null; // ticker ที่ inject markers ไปแล้ว

  // ── Helpers ─────────────────────────────────────────────────
  const esc = s => (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const log = (...a) => console.log('[BeerNotes]', ...a);

  // Cross-origin GET that bypasses TradingView's CSP via Tampermonkey
  function gmGet(url) {
    return new Promise((resolve, reject) => {
      const gm = (typeof GM_xmlhttpRequest !== 'undefined') ? GM_xmlhttpRequest
               : (typeof GM !== 'undefined' && GM.xmlHttpRequest) ? GM.xmlHttpRequest
               : null;
      if (!gm) {
        // Fallback to plain fetch (won't work if blocked by CSP)
        return fetch(url).then(r => r.ok ? r.text() : Promise.reject(new Error('HTTP ' + r.status)))
                         .then(resolve, reject);
      }
      gm({
        method: 'GET', url, timeout: 15000,
        onload: r => (r.status >= 200 && r.status < 400) ? resolve(r.responseText) : reject(new Error('HTTP ' + r.status)),
        onerror: e => reject(new Error('Network error: ' + (e.error || 'unknown'))),
        ontimeout: () => reject(new Error('Timeout'))
      });
    });
  }

  function getCurrentTicker() {
    // ?symbol=NASDAQ:NVDA หรือ NASDAQ%3ANVDA
    const sym = new URLSearchParams(location.search).get('symbol');
    if (sym) {
      const parts = decodeURIComponent(sym).split(':');
      return (parts[1] || parts[0]).trim().toUpperCase();
    }
    // /symbols/NASDAQ-NVDA/ หรือ /symbols/NVDA/
    const m = location.pathname.match(/\/symbols\/([^\/]+)/);
    if (m) {
      const parts = m[1].split('-');
      return (parts[parts.length - 1] || parts[0]).trim().toUpperCase();
    }
    // Title fallback: "NVDA stock price ..." / "NVDA - NVIDIA ..."
    const t = document.title.match(/^([A-Z][A-Z0-9.]{0,9})\b/);
    if (t) return t[1].toUpperCase();
    return null;
  }

  // ── Data ────────────────────────────────────────────────────
  async function loadNotes(force = false) {
    if (!force && notesCache && Date.now() - lastNotesLoadAt < NOTES_TTL) return notesCache;
    try {
      const txt = await gmGet(`${RAW}/notes/notes.json?_=${Date.now()}`);
      notesCache = JSON.parse(txt);
      log('notes loaded:', Object.keys(notesCache).length, 'tickers');
    } catch (e) {
      log('notes load failed:', e.message);
      notesCache = notesCache || {};
    }
    lastNotesLoadAt = Date.now();
    return notesCache;
  }

  async function loadDailyFile(date) {
    if (dailyCache[date] !== undefined) return dailyCache[date];
    try {
      const txt = await gmGet(`${RAW}/data/${date}.json`);
      dailyCache[date] = JSON.parse(txt);
    } catch (e) {
      log('daily load failed for', date, ':', e.message);
      dailyCache[date] = null;
    }
    return dailyCache[date];
  }

  // ── Floating button ────────────────────────────────────────
  function ensureButton() {
    let btn = document.getElementById('bv-float-btn');
    if (btn) return btn;
    btn = document.createElement('button');
    btn.id = 'bv-float-btn';
    btn.onclick = togglePanel;
    btn.title = 'ดูมุมมอง Beer Vanon ของหุ้นนี้';
    document.body.appendChild(btn);
    return btn;
  }
  function setButton(count) {
    const btn = ensureButton();
    btn.innerHTML = `💡 <span style="color:#fff">${count}</span> มุมมอง`;
    btn.style.display = 'flex';
  }
  function hideButton() {
    const btn = document.getElementById('bv-float-btn');
    if (btn) btn.style.display = 'none';
  }

  // ── Side panel ─────────────────────────────────────────────
  function ensurePanel() {
    let p = document.getElementById('bv-panel');
    if (p) return p;
    p = document.createElement('div');
    p.id = 'bv-panel';
    document.body.appendChild(p);
    return p;
  }
  function togglePanel() {
    panelOpen = !panelOpen;
    const p = ensurePanel();
    p.style.transform = panelOpen ? 'translateX(0)' : 'translateX(100%)';
    if (panelOpen) renderPanel();
  }
  function closePanel() {
    panelOpen = false;
    const p = ensurePanel();
    p.style.transform = 'translateX(100%)';
  }

  async function renderPanel() {
    const p = ensurePanel();
    const pineScript = notesCache?.[currentTicker]?.length
      ? generatePineScript(currentTicker, notesCache[currentTicker]) : null;
    p.innerHTML = `
      <div class="bv-head">
        <div>
          <div class="bv-head-ticker">📊 ${esc(currentTicker)}</div>
          <div class="bv-head-sub">มุมมองของฉัน · Beer Vanon</div>
        </div>
        <div style="display:flex;gap:6px;align-items:center">
          ${pineScript ? `<button class="bv-copy-btn" id="bv-copy-pine" title="คัดลอก Pine Script แล้ววางในตัวแก้ไข Pine Editor">📋 Pine Script</button>` : ''}
          <button class="bv-close-btn" title="ปิด">✕</button>
        </div>
      </div>
      <div class="bv-body" id="bv-body"><div class="bv-loading">กำลังโหลด...</div></div>
      <div class="bv-foot">
        <a href="https://patiphaninjob-lang.github.io/beer-vanon-agents/?date=" id="bv-foot-link" target="_blank">เปิด Beer Top 100 →</a>
      </div>`;
    p.querySelector('.bv-close-btn').onclick = closePanel;
    const copyBtn = document.getElementById('bv-copy-pine');
    if (copyBtn && pineScript) {
      copyBtn.onclick = async () => {
        try {
          if (typeof GM_setClipboard !== 'undefined') {
            GM_setClipboard(pineScript, 'text');
          } else {
            await navigator.clipboard.writeText(pineScript);
          }
          copyBtn.textContent = '✅ คัดลอกแล้ว!';
          setTimeout(() => { copyBtn.textContent = '📋 Pine Script'; }, 2500);
        } catch { copyBtn.textContent = '❌ ล้มเหลว'; }
      };
    }

    const allNotes = (notesCache?.[currentTicker] || []).slice().sort((a, b) => Number(b.id) - Number(a.id));
    const body = document.getElementById('bv-body');
    if (!allNotes.length) {
      body.innerHTML = '<div class="bv-loading">ยังไม่มีโน้ตของ ' + esc(currentTicker) + '</div>';
      return;
    }

    // Group by archive_date (or fallback to note's own date)
    const groups = {};
    for (const n of allNotes) {
      const key = n.archive_date || n.date || 'misc';
      (groups[key] ||= []).push(n);
    }
    const dates = Object.keys(groups).sort((a, b) => b.localeCompare(a));

    // Show notes immediately, then fill in daily data
    body.innerHTML = dates.map(d => `
      <div class="bv-day" data-date="${esc(d)}">
        <div class="bv-day-head">
          <span>📅 ${esc(d)}</span>
          <span class="bv-day-price" id="bv-price-${esc(d)}">—</span>
        </div>
        <div class="bv-section">
          <div class="bv-label">📝 มุมมองของฉัน (${groups[d].length})</div>
          ${groups[d].map(n => `
            <div class="bv-note">
              <div class="bv-note-meta">${esc(n.date || '')}${n.time ? ' · ' + esc(n.time) : ''}${n.price ? ` · $${n.price} (${n.pct_change >= 0 ? '+' : ''}${n.pct_change}%)` : ''}</div>
              <div class="bv-note-text">${esc(n.note)}</div>
            </div>`).join('')}
        </div>
        <div id="bv-analysis-${esc(d)}"></div>
        <div id="bv-news-${esc(d)}"></div>
      </div>
    `).join('');

    // Lazy-load daily data per date
    dates.forEach(async d => {
      const daily = await loadDailyFile(d);
      const stock = daily?.stocks?.find(s => s.ticker === currentTicker);
      if (!stock) return;

      const priceEl = document.getElementById(`bv-price-${d}`);
      if (priceEl) {
        const color = stock.pct_change >= 0 ? '#16c784' : '#ea3943';
        const arrow = stock.pct_change >= 0 ? '▲' : '▼';
        priceEl.innerHTML = `$${stock.price.toFixed(2)} <span style="color:${color}">${arrow} ${Math.abs(stock.pct_change).toFixed(2)}%</span>`;
      }

      if (stock.analysis) {
        const aEl = document.getElementById(`bv-analysis-${d}`);
        if (aEl) aEl.innerHTML = `
          <div class="bv-section">
            <div class="bv-label">🍺 Beer วิเคราะห์</div>
            <div class="bv-analysis">${esc(stock.analysis)}</div>
          </div>`;
      }

      if (stock.news?.length) {
        const nEl = document.getElementById(`bv-news-${d}`);
        if (nEl) nEl.innerHTML = `
          <div class="bv-section">
            <div class="bv-label">📰 ข่าววันนั้น</div>
            ${stock.news.slice(0, 5).map(n => `
              <div class="bv-news">
                ${n.url ? `<a href="${esc(n.url)}" target="_blank" rel="noopener">${esc(n.title)}</a>` : `<span>${esc(n.title)}</span>`}
                ${n.summary ? `<div class="bv-news-sum">${esc(n.summary)}</div>` : ''}
                ${n.provider || n.date ? `<div class="bv-news-meta">${esc([n.provider, n.date].filter(Boolean).join(' · '))}</div>` : ''}
              </div>`).join('')}
          </div>`;
      }
    });

    // Update footer link with first date
    const footLink = document.getElementById('bv-foot-link');
    if (footLink && dates.length) footLink.href = `https://patiphaninjob-lang.github.io/beer-vanon-agents/?date=${dates[0]}`;
  }

  // ── Pine Script Chart Markers ─────────────────────────────
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  // ถ้า archive_date ตรงกับวันหยุด (เสาร์/อาทิตย์) ให้เลื่อนมาวันศุกร์ก่อนหน้า
  function nearestTradingDay(dateStr) {
    const d = new Date(dateStr + 'T00:00:00Z');
    const dow = d.getUTCDay(); // 0=Sun, 6=Sat
    if (dow === 0) d.setUTCDate(d.getUTCDate() - 2); // Sun → Fri
    if (dow === 6) d.setUTCDate(d.getUTCDate() - 1); // Sat → Fri
    const isWeekend = (dow === 0 || dow === 6);
    return { dateStr: d.toISOString().slice(0, 10), isWeekend };
  }

  // Escape string for Pine Script double-quoted string
  function escapePine(s) {
    return (s || '').replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\r/g, '').replace(/\n/g, '\\n').slice(0, 2000);
  }

  function generatePineScript(ticker, notes, dateFiles = {}) {
    const rawDates = [...new Set(notes.map(n => n.archive_date).filter(Boolean))];
    if (!rawDates.length) return null;

    let script = `//@version=6\nindicator("💡 Beer Notes · ${ticker}", overlay=true, max_labels_count=500)\nisMyTicker = syminfo.ticker == "${ticker}"\nshowFull = input.bool(true, "แสดงข้อมูลเต็ม")\n`;

    rawDates.forEach((rawDate, i) => {
      const { dateStr, isWeekend } = nearestTradingDay(rawDate);
      const [y, m, day] = dateStr.split('-').map(Number);
      const color = isWeekend ? 'color.orange' : 'color.yellow';

      // Build visible text box content
      const dayNotes = notes.filter(n => n.archive_date === rawDate);
      const daily = dateFiles[rawDate];
      const stock = daily?.stocks?.find(s => s.ticker === ticker);
      const priceStr = stock?.price != null ? ` | ${stock.price} (${stock.pct_change >= 0 ? '+' : ''}${stock.pct_change}%)` : '';
      const header = isWeekend ? `💡 วันหยุด ${rawDate}${priceStr}` : `💡 ${dateStr}${priceStr}`;
      const lines = [header, '─'.repeat(22)];
      dayNotes.forEach(n => lines.push(`${n.time ? '[' + n.time + '] ' : ''}${n.note}`, ''));
      if (stock?.analysis) lines.push('🍺 ' + stock.analysis);

      const txt = escapePine(lines.join('\n').trimEnd());
      const cond = `isMyTicker and (year==${y} and month==${m} and dayofmonth==${day})`;

      script += `\nif (${cond}) and close >= open\n    label.new(bar_index, close, showFull ? "${txt}" : "💡", style=label.style_label_down, yloc=yloc.price, color=color.new(${color},0), textcolor=color.black, size=showFull ? size.normal : size.small, textalign=text.align_left)\n`;
      script += `if (${cond}) and close < open\n    label.new(bar_index, close, showFull ? "${txt}" : "💡", style=label.style_label_up, yloc=yloc.price, color=color.new(${color},0), textcolor=color.black, size=showFull ? size.normal : size.small, textalign=text.align_left)\n`;
    });

    return script.trim();
  }

  // Find the Pine Editor's .cm-content (not other CM6 instances on page)
  function findPineCmContent() {
    const containers = [
      '.tv-script-editor-container',
      '.script-editor-wrapper',
      '[data-name="pine-editor"]',
      '.pine-editor-toolbar',
    ];
    for (const sel of containers) {
      const el = document.querySelector(sel);
      if (el) {
        const c = el.querySelector('.cm-content') || el.closest('.cm-editor')?.querySelector('.cm-content');
        if (c) return c;
      }
    }
    // Fallback: last .cm-content on page (Pine Editor opens last)
    const all = document.querySelectorAll('.cm-content');
    return all.length ? all[all.length - 1] : null;
  }

  // Find CM6 EditorView by scanning the .cm-editor element's own properties
  function findCM6View(cmContent) {
    const cmEditor = cmContent?.closest('.cm-editor') || document.querySelector('.cm-editor');
    if (!cmEditor) return null;
    // CM6 attaches EditorView to the DOM element under various property names
    for (const key of Object.getOwnPropertyNames(cmEditor)) {
      try {
        const v = cmEditor[key];
        if (v && typeof v === 'object' && v.state?.doc != null && typeof v.dispatch === 'function') {
          log('CM6 view found at .cm-editor.' + key);
          return v;
        }
      } catch {}
    }
    return null;
  }

  // Inject script text into CM6 Pine Editor — 3 strategies
  async function tryInjectScript(script) {
    const cmContent = findPineCmContent();
    if (!cmContent) { log('cm-content not found'); return false; }

    // Strategy 1: CM6 EditorView.dispatch via property scan
    const view = findCM6View(cmContent);
    if (view) {
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: script } });
      log('injected via CM6 dispatch');
      return true;
    }

    // Strategy 2: ClipboardEvent paste — CM6 listens to paste events on .cm-content
    cmContent.focus();
    cmContent.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'a', code: 'KeyA', ctrlKey: true, bubbles: true, cancelable: true
    }));
    await sleep(120);
    try {
      const dt = new DataTransfer();
      dt.setData('text/plain', script);
      const pasteEvt = new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData: dt });
      cmContent.dispatchEvent(pasteEvt);
      log('injected via ClipboardEvent paste');
      return true;
    } catch (e) { log('ClipboardEvent failed:', e.message); }

    // Strategy 3: execCommand insertText
    document.execCommand('selectAll', false, null);
    await sleep(100);
    const ok = document.execCommand('insertText', false, script);
    if (ok) { log('injected via execCommand'); return true; }

    log('all strategies failed');
    return false;
  }

  async function injectChartMarkers(ticker, notes) {
    if (markersTicker === ticker) return;
    markersTicker = ticker;

    // Load daily data for tooltip content (Beer analysis, price)
    const dateFiles = {};
    const archiveDates = [...new Set(notes.map(n => n.archive_date).filter(Boolean))];
    await Promise.all(archiveDates.map(async d => { dateFiles[d] = await loadDailyFile(d); }));

    const script = generatePineScript(ticker, notes, dateFiles);
    if (!script) { log('no archive_dates to plot'); return; }

    log('v1.9: Pine Script injection for', ticker);

    // Step 1: Find Pine Editor button
    await sleep(2000);
    const pineBtn = findByAttr([
      '[data-name="pine-script"]', '[data-name="script"]',
      '[data-name="pine-editor"]', '[data-tooltip*="Pine"]',
      '[title*="Pine Editor"]', '[aria-label*="Pine Editor"]',
    ]) || findBtnByText(['Pine Editor', 'Pine Script']);

    if (!pineBtn) {
      const names = [...document.querySelectorAll('[data-name]')].map(e => e.getAttribute('data-name'));
      log('Pine btn NOT found. data-names:', [...new Set(names)].join(', '));
      return;
    }
    log('Pine btn found:', pineBtn.getAttribute('data-name') || pineBtn.textContent?.trim());
    pineBtn.click();
    await sleep(2000); // wait for CM6 to initialize

    // Step 2: Inject Pine Script into CM6 editor
    const injected = await tryInjectScript(script);
    if (!injected) { log('script injection failed'); return; }
    await sleep(600);

    // Step 3: Click "Add to chart"
    const addBtn = findByAttr([
      '[data-name="add-to-chart"]', '[data-tooltip*="Add to chart"]',
      '[title*="Add to chart"]', '[aria-label*="Add to chart"]',
    ]) || findBtnByText(['Add to chart', 'Add to Chart']);

    if (!addBtn) { log('"Add to chart" btn not found'); return; }
    addBtn.click();
    log('💡 Pine Script added to chart for', ticker);
    await sleep(800);

    // Step 4: Close Pine Editor so it doesn't cover the chart
    const closeBtn = findByAttr([
      '[data-name="close"]', '[aria-label="Close"]', '[title="Close"]',
    ]) || findBtnByText(['Close', 'ปิด']);
    if (closeBtn) { closeBtn.click(); log('editor closed'); }
  }

  function findByAttr(selectors) {
    for (const s of selectors) {
      try { const el = document.querySelector(s); if (el) return el; } catch {}
    }
    return null;
  }
  function findBtnByText(texts) {
    for (const el of document.querySelectorAll('button,[role="button"],[role="tab"]')) {
      const t = (el.textContent || el.getAttribute('aria-label') || el.getAttribute('title') || '').trim();
      if (texts.some(x => t.toLowerCase().includes(x.toLowerCase()))) return el;
    }
    return null;
  }

  // ── Polling: detect ticker change ──────────────────────────
  async function tick() {
    const t = getCurrentTicker();
    if (t === currentTicker) return;
    log('ticker change:', currentTicker, '→', t);
    currentTicker = t;
    if (!t) { hideButton(); if (panelOpen) closePanel(); return; }

    await loadNotes();
    const count = (notesCache?.[t] || []).length;
    log('ticker', t, 'has', count, 'notes');
    if (count === 0) {
      hideButton();
      if (panelOpen) closePanel();
    } else {
      setButton(count);
      if (panelOpen) renderPanel();
      injectChartMarkers(t, notesCache[t]).catch(e => log('injectChartMarkers error:', e.message));
    }
  }

  // ── Styles ─────────────────────────────────────────────────
  function injectStyles() {
    const s = document.createElement('style');
    s.textContent = `
      #bv-float-btn {
        position: fixed; top: 80px; right: 20px; z-index: 2147483646;
        background: #1a1f2e; border: 1px solid #f0b90b; color: #f0b90b;
        border-radius: 20px; padding: 7px 14px; font-size: 13px;
        cursor: pointer; box-shadow: 0 4px 16px rgba(0,0,0,0.5);
        display: flex; align-items: center; gap: 6px; font-weight: 600;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        transition: transform 0.15s ease;
      }
      #bv-float-btn:hover { transform: scale(1.05); background: #21262d; }
      #bv-panel {
        position: fixed; top: 0; right: 0; width: 440px; max-width: 90vw; height: 100vh;
        background: #0d1117; border-left: 1px solid #30363d;
        z-index: 2147483647; transform: translateX(100%);
        transition: transform 0.25s ease;
        display: flex; flex-direction: column; overflow: hidden;
        box-shadow: -8px 0 32px rgba(0,0,0,0.6);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #e6edf3; font-size: 13px;
      }
      .bv-head {
        padding: 14px 18px; border-bottom: 1px solid #21262d;
        background: #161b22; display: flex; justify-content: space-between;
        align-items: center; flex-shrink: 0;
      }
      .bv-head-ticker { font-size: 1.15em; font-weight: 700; color: #fff; }
      .bv-head-sub { font-size: 0.78em; color: #6b7280; margin-top: 2px; }
      .bv-close-btn {
        background: none; border: none; color: #8b949e; font-size: 1.3em;
        cursor: pointer; padding: 4px 8px; border-radius: 4px;
      }
      .bv-close-btn:hover { color: #fff; background: #21262d; }
      .bv-copy-btn {
        background: #1c2233; border: 1px solid #f0b90b; color: #f0b90b;
        border-radius: 6px; padding: 4px 10px; font-size: 0.78em;
        cursor: pointer; font-family: inherit; white-space: nowrap;
      }
      .bv-copy-btn:hover { background: #252d40; }
      .bv-body { padding: 14px 18px; overflow-y: auto; flex: 1; }
      .bv-foot {
        padding: 10px 18px; border-top: 1px solid #21262d; background: #161b22;
        text-align: center; flex-shrink: 0;
      }
      .bv-foot a { color: #6366f1; text-decoration: none; font-size: 0.85em; }
      .bv-foot a:hover { text-decoration: underline; }
      .bv-loading { text-align: center; color: #6b7280; padding: 40px 0; }
      .bv-day {
        background: #161b22; border-radius: 8px; padding: 14px;
        margin-bottom: 12px; border-left: 3px solid #f0b90b;
      }
      .bv-day-head {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 12px; color: #fff; font-weight: 600; font-size: 0.95em;
      }
      .bv-day-price { font-weight: normal; color: #e6edf3; font-size: 0.88em; }
      .bv-section { margin-bottom: 12px; }
      .bv-section:last-child { margin-bottom: 0; }
      .bv-label {
        color: #6b7280; font-size: 0.72em; text-transform: uppercase;
        letter-spacing: 0.06em; margin-bottom: 6px; font-weight: 600;
      }
      .bv-note {
        background: #0d1117; border-left: 2px solid #6366f1;
        border-radius: 0 6px 6px 0; padding: 8px 10px; margin-bottom: 6px;
      }
      .bv-note-meta { color: #6b7280; font-size: 0.75em; margin-bottom: 4px; }
      .bv-note-text {
        color: #d1d5db; line-height: 1.6; white-space: pre-wrap;
        word-break: break-word; font-size: 0.87em;
      }
      .bv-analysis {
        background: #0d1117; border-radius: 6px; padding: 10px;
        color: #d1d5db; line-height: 1.6; white-space: pre-wrap;
        font-size: 0.85em;
      }
      .bv-news { margin-bottom: 8px; padding-left: 8px; border-left: 2px solid #1e2532; }
      .bv-news a { color: #93c5fd; text-decoration: none; font-size: 0.85em; font-weight: 500; line-height: 1.4; }
      .bv-news a:hover { text-decoration: underline; }
      .bv-news span { color: #d1d5db; font-size: 0.85em; font-weight: 500; }
      .bv-news-sum { color: #6b7280; font-size: 0.78em; margin-top: 3px; line-height: 1.5; }
      .bv-news-meta { color: #4b5563; font-size: 0.72em; margin-top: 2px; }
      @media (max-width: 560px) {
        #bv-float-btn { top: auto; bottom: 80px; right: 12px; }
        #bv-panel { width: 100vw; }
      }
    `;
    document.head.appendChild(s);
  }

  // ── Init ───────────────────────────────────────────────────
  log('userscript v1.9.0 booting on', location.href);
  injectStyles();
  tick();
  setInterval(tick, 1500);
})();
