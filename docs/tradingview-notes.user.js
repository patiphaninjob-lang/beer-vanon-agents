// ==UserScript==
// @name         🍺 Beer Vanon Notes on TradingView
// @namespace    https://patiphaninjob-lang.github.io/beer-vanon-agents/
// @version      1.4.0
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
    p.innerHTML = `
      <div class="bv-head">
        <div>
          <div class="bv-head-ticker">📊 ${esc(currentTicker)}</div>
          <div class="bv-head-sub">มุมมองของฉัน · Beer Vanon</div>
        </div>
        <button class="bv-close-btn" title="ปิด">✕</button>
      </div>
      <div class="bv-body" id="bv-body"><div class="bv-loading">กำลังโหลด...</div></div>
      <div class="bv-foot">
        <a href="https://patiphaninjob-lang.github.io/beer-vanon-agents/?date=" id="bv-foot-link" target="_blank">เปิด Beer Top 100 →</a>
      </div>`;
    p.querySelector('.bv-close-btn').onclick = closePanel;

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

  function generatePineScript(ticker, notes) {
    const dates = [...new Set(notes.map(n => n.archive_date).filter(Boolean))];
    if (!dates.length) return null;
    const conds = dates.map(d => {
      const [y, m, day] = d.split('-').map(Number);
      return `(year==${y} and month==${m} and dayofmonth==${day})`;
    }).join(' or ');
    return `//@version=5
indicator("💡 Beer Notes · ${ticker}", overlay=true, max_labels_count=50)
isMyTicker = syminfo.ticker == "${ticker}"
isNoteDay = ${conds}
plotshape(isMyTicker and isNoteDay, style=shape.labeldown, location=location.abovebar, color=color.new(color.yellow,0), textcolor=color.black, text="💡", size=size.small, title="Beer Note")`;
  }

  // Inject script text into CM6 Pine Editor — 3 strategies in order of preference
  async function tryInjectScript(script) {
    // Strategy 1: CM6 EditorView.dispatch (cleanest — if TV exposes .CodeMirror on .cm-editor)
    const cmEditor = document.querySelector('.cm-editor');
    if (cmEditor?.CodeMirror) {
      const view = cmEditor.CodeMirror;
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: script } });
      log('injected via CM6 dispatch');
      return true;
    }

    // Strategy 2: execCommand insertText on contenteditable .cm-content (works in Chrome CM6)
    const cmContent = document.querySelector('.cm-content');
    if (cmContent) {
      cmContent.focus();
      document.execCommand('selectAll', false, null);
      await sleep(120);
      const ok = document.execCommand('insertText', false, script);
      if (ok) { log('injected via execCommand insertText'); return true; }
    }

    // Strategy 3: GM_setClipboard + Ctrl+A / Ctrl+V key simulation
    if (typeof GM_setClipboard !== 'undefined' && cmContent) {
      GM_setClipboard(script, 'text');
      cmContent.focus();
      cmContent.dispatchEvent(new KeyboardEvent('keydown', { key: 'a', code: 'KeyA', ctrlKey: true, bubbles: true, cancelable: true }));
      await sleep(150);
      cmContent.dispatchEvent(new KeyboardEvent('keydown', { key: 'v', code: 'KeyV', ctrlKey: true, bubbles: true, cancelable: true }));
      await sleep(200);
      log('injected via GM_setClipboard + key simulation');
      return true;
    }

    log('all injection strategies failed — cmEditor:', !!cmEditor, 'cmContent:', !!cmContent);
    return false;
  }

  async function injectChartMarkers(ticker, notes) {
    if (markersTicker === ticker) return;
    markersTicker = ticker;

    const script = generatePineScript(ticker, notes);
    if (!script) { log('no archive_dates to plot'); return; }

    log('v1.4: Pine Script injection for', ticker);

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
  log('userscript v1.4.0 booting on', location.href);
  injectStyles();
  tick();
  setInterval(tick, 1500);
})();
