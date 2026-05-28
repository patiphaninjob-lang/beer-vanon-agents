// ==UserScript==
// @name         Beer Vanon Notes on TradingView
// @namespace    https://patiphaninjob-lang.github.io/beer-vanon-agents/
// @version      3.2.1
// @description  Put Beer Top 100 notes, Beer analysis, and news context onto TradingView as small candle-anchored markers.
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
  const RAW = `https://raw.githubusercontent.com/${REPO}/main/docs`;
  const NOTES_TTL = 60_000;
  const POLL_MS = 1500;
  const MAX_TOOLTIP_CHARS = 3600;
  const MAX_NOTE_CHARS = 520;

  let notesCache = null;
  let dailyCache = {};
  let currentTicker = null;
  let panelOpen = false;
  let lastNotesLoadAt = 0;
  let lastPanelTicker = null;

  const log = (...args) => console.log('[BeerNotes]', ...args);
  const esc = value => String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  function gmGet(url) {
    return new Promise((resolve, reject) => {
      const gm = typeof GM_xmlhttpRequest !== 'undefined'
        ? GM_xmlhttpRequest
        : typeof GM !== 'undefined' && GM.xmlHttpRequest
          ? GM.xmlHttpRequest
          : null;

      if (!gm) {
        return fetch(url)
          .then(r => (r.ok ? r.text() : Promise.reject(new Error('HTTP ' + r.status))))
          .then(resolve, reject);
      }

      gm({
        method: 'GET',
        url,
        timeout: 15000,
        onload: r => {
          if (r.status >= 200 && r.status < 400) resolve(r.responseText);
          else reject(new Error('HTTP ' + r.status));
        },
        onerror: e => reject(new Error('Network error: ' + (e.error || 'unknown'))),
        ontimeout: () => reject(new Error('Timeout'))
      });
    });
  }

  async function copyText(text) {
    if (typeof GM_setClipboard !== 'undefined') {
      GM_setClipboard(text, 'text');
      return true;
    }
    await navigator.clipboard.writeText(text);
    return true;
  }

  function getCurrentTicker() {
    const sym = new URLSearchParams(location.search).get('symbol');
    if (sym) {
      const parts = decodeURIComponent(sym).split(':');
      return (parts[1] || parts[0]).trim().toUpperCase();
    }

    const pathMatch = location.pathname.match(/\/symbols\/([^/]+)/);
    if (pathMatch) {
      const parts = pathMatch[1].split('-');
      return (parts[parts.length - 1] || parts[0]).trim().toUpperCase();
    }

    const titleMatch = document.title.match(/^([A-Z][A-Z0-9.]{0,9})\b/);
    return titleMatch ? titleMatch[1].toUpperCase() : null;
  }

  async function loadNotes(force = false) {
    if (!force && notesCache && Date.now() - lastNotesLoadAt < NOTES_TTL) return notesCache;
    try {
      const txt = await gmGet(`${RAW}/notes/notes.json?_=${Date.now()}`);
      notesCache = JSON.parse(txt);
      log('loaded notes for', Object.keys(notesCache).length, 'keys');
    } catch (err) {
      log('notes load failed:', err.message);
      notesCache = notesCache || {};
    }
    lastNotesLoadAt = Date.now();
    return notesCache;
  }

  async function loadDailyFile(date) {
    if (!date) return null;
    if (dailyCache[date] !== undefined) return dailyCache[date];
    try {
      const txt = await gmGet(`${RAW}/data/${date}.json?_=${Date.now()}`);
      dailyCache[date] = JSON.parse(txt);
    } catch (err) {
      log('daily load failed:', date, err.message);
      dailyCache[date] = null;
    }
    return dailyCache[date];
  }

  function tickerNotes(ticker) {
    if (!ticker) return [];
    // Normalize ticker: TradingView BRK.B -> Yahoo BRK-B
    const normalized = ticker.replace('.', '-');
    const notes = notesCache?.[normalized] || notesCache?.[ticker] || [];
    return notes
      .filter(n => n && (n.archive_date || n.date))
      .slice()
      .sort((a, b) => String(b.id || '').localeCompare(String(a.id || '')));
  }

  function groupNotesByArchiveDate(notes) {
    const groups = {};
    for (const n of notes) {
      const key = n.date || n.archive_date || 'unknown';
      (groups[key] ||= []).push(n);
    }
    return Object.keys(groups)
      .sort((a, b) => b.localeCompare(a))
      .map(date => ({ date, notes: groups[date] }));
  }

  function previousWeekday(dateStr) {
    const d = new Date(`${dateStr}T00:00:00Z`);
    if (Number.isNaN(d.getTime())) return { markerDate: dateStr, shifted: false };
    const dow = d.getUTCDay();
    if (dow === 0) d.setUTCDate(d.getUTCDate() - 2);
    if (dow === 6) d.setUTCDate(d.getUTCDate() - 1);
    return { markerDate: d.toISOString().slice(0, 10), shifted: dow === 0 || dow === 6 };
  }

  function clipText(value, max = MAX_NOTE_CHARS, preserveLines = false) {
    const raw = String(value || '');
    const text = preserveLines
      ? raw.replace(/[^\S\r\n]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim()
      : raw.replace(/\s+/g, ' ').trim();
    const chars = Array.from(text);
    return chars.length > max ? chars.slice(0, max - 1).join('') + '…' : text;
  }

  function plainText(value) {
    return String(value || '')
      .replace(/\*\*/g, '')
      .replace(/^\s*[-*]\s+/gm, '- ')
      .replace(/\r/g, '')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  }

  function fmtNumber(value) {
    const num = Number(value || 0);
    if (!Number.isFinite(num)) return '';
    if (Math.abs(num) >= 1_000_000_000_000) return (num / 1_000_000_000_000).toFixed(2) + 'T';
    if (Math.abs(num) >= 1_000_000_000) return (num / 1_000_000_000).toFixed(2) + 'B';
    if (Math.abs(num) >= 1_000_000) return (num / 1_000_000).toFixed(2) + 'M';
    if (Math.abs(num) >= 1_000) return (num / 1_000).toFixed(2) + 'K';
    return num.toFixed(0);
  }

  function pineString(value, max = MAX_TOOLTIP_CHARS) {
    const clipped = clipText(value, max, true);
    return clipped
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/\r/g, '')
      .replace(/\n/g, '\\n');
  }

  function pineHeader(ticker) {
    return [
      '//@version=6',
      `indicator("Beer Notes · ${ticker}", overlay=true, max_labels_count=500)`,
      `isMyTicker = syminfo.ticker == "${ticker}"`,
      'showMarkers = input.bool(true, "Show Beer note markers")',
      'markerSize = input.string("tiny", "Marker size", options=["tiny", "small", "normal"])',
      'mkSize = markerSize == "normal" ? size.normal : markerSize == "small" ? size.small : size.tiny',
      'isFirstBarOfDay = timeframe.isintraday ? ta.change(time("D")) != 0 : true'
    ].join('\n');
  }

  function buildTooltip(ticker, rawDate, markerDate, shifted, groupNotes, stock) {
    const lines = [
      `Beer Notes · ${ticker}`,
      shifted ? `Written: ${rawDate} | Marker: ${markerDate}` : `Date: ${markerDate}`
    ];

    if (stock) {
      const pct = Number(stock.pct_change || 0);
      lines.push([
        `Rank #${stock.rank || '-'}`,
        stock.sector || '',
        stock.price != null ? `$${Number(stock.price).toFixed(2)} (${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%)` : '',
        stock.volume ? `Vol ${fmtNumber(stock.volume)}` : ''
      ].filter(Boolean).join(' | '));
    }

    lines.push('', 'My thoughts:');
    groupNotes.forEach((n, i) => {
      const prefix = n.time ? `[${n.time}] ` : `${i + 1}. `;
      lines.push(prefix + clipText(n.note, 520));
    });

    if (stock?.analysis) {
      lines.push('', 'Beer analysis / opinion:');
      lines.push(clipText(plainText(stock.analysis), 1200));
    }

    if (stock?.homework_checklist?.length) {
      lines.push('', 'Chapter 34 homework to finish:');
      stock.homework_checklist.slice(0, 6).forEach((item, i) => {
        const homeworkText = item.insight || item.prompt || '';
        lines.push(clipText(`${i + 1}. ${item.topic || ''}: ${homeworkText}`, 300));
      });
    }

    if (stock?.news?.length) {
      lines.push('', 'News Beer used:');
      stock.news.slice(0, 4).forEach((news, i) => {
        const meta = [news.provider, news.date].filter(Boolean).join(' · ');
        const item = `${i + 1}. ${news.title || 'Untitled'}${news.summary ? ' — ' + news.summary : ''}${meta ? ' (' + meta + ')' : ''}`;
        lines.push(clipText(item, 360));
      });
    }

    return lines.join('\n');
  }

  async function generatePineScript(ticker, notes) {
    const groups = groupNotesByArchiveDate(notes);
    if (!groups.length) return '';

    const dailyByDate = {};
    await Promise.all(groups.map(async g => {
      dailyByDate[g.date] = await loadDailyFile(g.date);
    }));

    let script = pineHeader(ticker);

    for (const group of groups) {
      const { markerDate, shifted } = previousWeekday(group.date);
      const [y, m, d] = markerDate.split('-').map(Number);
      if (!y || !m || !d) continue;

      const daily = dailyByDate[group.date];
      const stock = daily?.stocks?.find(s => s.ticker === ticker || s.ticker === ticker.replace('.', '-'));
      const tooltip = pineString(buildTooltip(ticker, group.date, markerDate, shifted, group.notes, stock));
      const color = shifted ? 'color.orange' : 'color.yellow';
      const cond = `isMyTicker and showMarkers and isFirstBarOfDay and year == ${y} and month == ${m} and dayofmonth == ${d}`;

      script += `\n\nif ${cond}\n`;
      script += `    label.new(bar_index, high, "💡", yloc=yloc.abovebar, style=label.style_label_down, color=color.new(${color}, 0), textcolor=color.black, size=mkSize, tooltip="${tooltip}")`;
    }

    return script;
  }

  function ensureButton() {
    let btn = document.getElementById('bv-note-button');
    if (btn) return btn;
    btn = document.createElement('button');
    btn.id = 'bv-note-button';
    btn.type = 'button';
    btn.addEventListener('click', () => {
      panelOpen = !panelOpen;
      renderPanel();
    });
    document.body.appendChild(btn);
    return btn;
  }

  function ensurePanel() {
    let panel = document.getElementById('bv-note-panel');
    if (panel) return panel;
    panel = document.createElement('aside');
    panel.id = 'bv-note-panel';
    document.body.appendChild(panel);
    return panel;
  }

  function setStatus(message, tone = 'muted') {
    const el = document.getElementById('bv-status');
    if (!el) return;
    el.className = `bv-status ${tone}`;
    el.textContent = message;
  }

  async function renderPanel() {
    const panel = ensurePanel();
    panel.classList.toggle('open', panelOpen);
    if (!panelOpen) return;

    const ticker = currentTicker;
    const notes = tickerNotes(ticker);
    lastPanelTicker = ticker;

    const groups = groupNotesByArchiveDate(notes);
    panel.innerHTML = `
      <div class="bv-panel-head">
        <div>
          <div class="bv-title">${esc(ticker || 'Ticker')}</div>
          <div class="bv-subtitle">Beer Top 100 note markers</div>
        </div>
        <button type="button" class="bv-icon-btn" id="bv-close">×</button>
      </div>
      <div class="bv-actions">
        <button type="button" class="bv-primary" id="bv-copy-pine">Copy Pine markers</button>
        <button type="button" class="bv-secondary" id="bv-try-install">Try place on chart</button>
      </div>
      <div id="bv-status" class="bv-status muted">Marker = small 💡 on the candle date. Full text stays here and in Pine tooltip.</div>
      <div class="bv-panel-body">
        ${groups.length ? '<div class="bv-loading">Loading Beer archive context...</div>' : '<div class="bv-empty">No Beer Top 100 notes for this ticker yet.</div>'}
      </div>
    `;

    panel.querySelector('#bv-close').addEventListener('click', () => {
      panelOpen = false;
      renderPanel();
    });

    panel.querySelector('#bv-copy-pine').addEventListener('click', async () => {
      await handleCopyPine();
    });

    panel.querySelector('#bv-try-install').addEventListener('click', async () => {
      await handleInstallPine();
    });

    if (groups.length) {
      const stockByDate = {};
      await Promise.all(groups.map(async group => {
        const daily = await loadDailyFile(group.date);
        stockByDate[group.date] = daily?.stocks?.find(s => s.ticker === ticker || s.ticker === ticker.replace('.', '-')) || null;
      }));

      if (!panelOpen || lastPanelTicker !== ticker) return;
      const body = panel.querySelector('.bv-panel-body');
      if (body) body.innerHTML = groups.map(group => groupHTML(group, stockByDate[group.date])).join('');
    }
  }

  function groupHTML(group, stock) {
    const { markerDate, shifted } = previousWeekday(group.date);
    return `
      <section class="bv-day">
        <div class="bv-day-head">
          <span>${esc(group.date)}</span>
          <span>${shifted ? `marker ${esc(markerDate)}` : 'same candle'}</span>
        </div>
        ${stock ? stockContextHTML(stock) : '<div class="bv-missing">Beer archive context was not found for this date.</div>'}
        ${group.notes.map(noteHTML).join('')}
      </section>
    `;
  }

  function stockContextHTML(stock) {
    const pct = Number(stock.pct_change || 0);
    const price = stock.price != null ? `$${Number(stock.price).toFixed(2)} (${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%)` : '';
    const pills = [
      stock.rank ? `Rank #${stock.rank}` : '',
      stock.sector || '',
      price,
      stock.volume ? `Vol ${fmtNumber(stock.volume)}` : '',
      stock.market_cap ? `MCap ${fmtNumber(stock.market_cap)}` : '',
      stock.pe_ratio ? `P/E ${Number(stock.pe_ratio).toFixed(1)}` : ''
    ].filter(Boolean).map(v => `<span>${esc(v)}</span>`).join('');

    const news = (stock.news || []).slice(0, 5).map(n => `
      <div class="bv-news-item">
        <div class="bv-news-title">${esc(n.title || 'Untitled')}</div>
        ${n.summary ? `<div class="bv-news-summary">${esc(n.summary)}</div>` : ''}
        <div class="bv-news-meta">${esc([n.provider, n.date].filter(Boolean).join(' · '))}</div>
      </div>
    `).join('');
    const homework = (stock.homework_checklist || []).slice(0, 6).map(item => `
      <div class="bv-homework-item">
        <div class="bv-homework-topic">${esc(item.topic || '')}</div>
        <div class="bv-homework-prompt">${esc(item.insight || item.prompt || '')}</div>
      </div>
    `).join('');

    return `
      <div class="bv-stock">
        <div class="bv-stock-name">${esc(stock.name || stock.ticker || '')}</div>
        <div class="bv-pills">${pills}</div>
      </div>
      ${homework ? `
        <div class="bv-homework">
          <div class="bv-section-label">🧭 Chapter 34 homework to finish</div>
          ${homework}
        </div>
      ` : ''}
      ${stock.analysis ? `
        <div class="bv-analysis">
          <div class="bv-section-label">🍺 Beer analysis / opinion</div>
          <div class="bv-analysis-text">${esc(stock.analysis)}</div>
        </div>
      ` : ''}
      ${news ? `
        <div class="bv-news">
          <div class="bv-section-label">📰 News Beer used</div>
          ${news}
        </div>
      ` : ''}
      <div class="bv-section-label bv-my-label">My thoughts</div>
    `;
  }

  function noteHTML(n) {
    const pct = Number(n.pct_change || 0);
    const price = n.price ? `$${Number(n.price).toFixed(2)} (${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%)` : '';
    return `
      <div class="bv-note">
        <div class="bv-note-meta">${esc([n.time, price].filter(Boolean).join(' · '))}</div>
        <div class="bv-note-text">${esc(n.note)}</div>
      </div>
    `;
  }

  async function handleCopyPine() {
    const ticker = currentTicker;
    const notes = tickerNotes(ticker);
    if (!ticker || !notes.length) return setStatus('No notes to convert.', 'warn');
    setStatus('Building Pine marker script...', 'muted');
    const script = await generatePineScript(ticker, notes);
    await copyText(script);
    setStatus('Copied. Paste into Pine Editor, then Add/Update on chart.', 'ok');
  }

  async function handleInstallPine() {
    const ticker = currentTicker;
    const notes = tickerNotes(ticker);
    if (!ticker || !notes.length) return setStatus('No notes to place on this chart.', 'warn');

    setStatus('Building Pine and copying it first...', 'muted');
    const script = await generatePineScript(ticker, notes);
    await copyText(script);

    const opened = await openPineEditor();
    if (!opened) {
      return setStatus('Copied Pine. Open Pine Editor and paste it manually.', 'warn');
    }

    const injected = await injectIntoEditor(script);
    if (!injected) {
      return setStatus('Copied Pine. TradingView blocked auto paste; press Ctrl+V in Pine Editor.', 'warn');
    }

    const applied = await clickAddOrUpdate();
    setStatus(applied
      ? 'Placed marker script on chart. Look for small 💡 candles.'
      : 'Pasted Pine. Click Add to chart / Update on chart if TradingView asks.',
      applied ? 'ok' : 'warn');
  }

  async function openPineEditor() {
    const candidates = [
      '[aria-label="Pine"]',
      '[aria-label*="Pine"]',
      '[title*="Pine"]',
      '[data-name*="pine"]'
    ];
    const btn = findFirst(candidates) || findButtonByText(['Pine', 'Pine Editor']);
    if (!btn) return false;
    btn.click();
    await sleep(1200);
    return true;
  }

  async function injectIntoEditor(script) {
    const editor = findEditorSurface();
    if (!editor) return false;

    editor.focus();
    await sleep(100);

    try {
      const ok = document.execCommand('selectAll') && document.execCommand('insertText', false, script);
      if (ok) return true;
    } catch {}

    const cm = findCM6View(editor);
    if (cm) {
      cm.dispatch({ changes: { from: 0, to: cm.state.doc.length, insert: script } });
      return true;
    }

    try {
      const dt = new DataTransfer();
      dt.setData('text/plain', script);
      editor.dispatchEvent(new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData: dt }));
      return true;
    } catch {}

    return false;
  }

  function findEditorSurface() {
    return document.querySelector('.monaco-editor textarea.inputarea')
      || document.querySelector('textarea[aria-label*="Editor content"]')
      || document.querySelector('.cm-content')
      || document.querySelector('[contenteditable="true"]');
  }

  function findCM6View(surface) {
    const cmEditor = surface?.closest('.cm-editor') || document.querySelector('.cm-editor');
    if (!cmEditor) return null;
    for (const key of Object.getOwnPropertyNames(cmEditor)) {
      try {
        const value = cmEditor[key];
        if (value?.state?.doc != null && typeof value.dispatch === 'function') return value;
      } catch {}
    }
    return null;
  }

  async function clickAddOrUpdate() {
    await sleep(700);
    const btn = findButtonByText(['Add to chart', 'Update on chart']);
    if (!btn) return false;
    if (btn.disabled || btn.getAttribute('aria-disabled') === 'true') return false;
    btn.click();
    return true;
  }

  function findFirst(selectors) {
    for (const selector of selectors) {
      try {
        const el = document.querySelector(selector);
        if (el) return el;
      } catch {}
    }
    return null;
  }

  function findButtonByText(needles) {
    const lower = needles.map(n => n.toLowerCase());
    for (const el of document.querySelectorAll('button,[role="button"],[role="tab"]')) {
      const label = [
        el.textContent,
        el.getAttribute('aria-label'),
        el.getAttribute('title')
      ].filter(Boolean).join(' ').trim().toLowerCase();
      if (lower.some(n => label.includes(n))) return el;
    }
    return null;
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function tick() {
    const ticker = getCurrentTicker();
    const tickerChanged = ticker !== currentTicker;
    currentTicker = ticker;
    await loadNotes();

    const notes = ticker ? tickerNotes(ticker) : [];
    const btn = ensureButton();
    if (!ticker || !notes.length) {
      btn.style.display = 'none';
      panelOpen = false;
      renderPanel();
      return;
    }

    const uniqueDates = groupNotesByArchiveDate(notes).length;
    btn.style.display = 'flex';
    btn.innerHTML = `<span class="bv-dot">💡</span><span>${esc(ticker)}</span><strong>${notes.length}</strong>`;
    btn.title = `${notes.length} Beer notes across ${uniqueDates} candle date(s)`;

    if (panelOpen || tickerChanged || lastPanelTicker === ticker) renderPanel();
  }

  function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      #bv-note-button {
        position: fixed; top: 78px; right: 18px; z-index: 2147483646;
        display: none; align-items: center; gap: 7px;
        border: 1px solid #f0b90b; background: #10151f; color: #f7d774;
        border-radius: 999px; padding: 7px 12px; font: 600 12px/1.2 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
        cursor: pointer; box-shadow: 0 8px 26px rgba(0,0,0,.45);
      }
      #bv-note-button:hover { background: #171e2b; transform: translateY(-1px); }
      #bv-note-button strong {
        min-width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center;
        border-radius: 999px; background: #f0b90b; color: #111827; font-size: 11px;
      }
      #bv-note-panel {
        position: fixed; top: 0; right: 0; z-index: 2147483647;
        width: 430px; max-width: min(430px, 92vw); height: 100vh;
        transform: translateX(104%); transition: transform .22s ease;
        background: #0d1117; color: #e6edf3; border-left: 1px solid #30363d;
        box-shadow: -16px 0 42px rgba(0,0,0,.55);
        font: 13px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
        display: flex; flex-direction: column;
      }
      #bv-note-panel.open { transform: translateX(0); }
      .bv-panel-head {
        padding: 14px 16px; display: flex; align-items: center; justify-content: space-between;
        background: #161b22; border-bottom: 1px solid #21262d;
      }
      .bv-title { font-size: 17px; font-weight: 750; color: #fff; }
      .bv-subtitle { color: #8b949e; font-size: 12px; margin-top: 1px; }
      .bv-icon-btn {
        border: 0; background: transparent; color: #8b949e; font-size: 24px; line-height: 1;
        cursor: pointer; width: 32px; height: 32px; border-radius: 6px;
      }
      .bv-icon-btn:hover { background: #21262d; color: #fff; }
      .bv-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 12px 16px 8px; }
      .bv-primary, .bv-secondary {
        border-radius: 7px; padding: 9px 10px; cursor: pointer; font: 700 12px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      }
      .bv-primary { border: 1px solid #f0b90b; background: #f0b90b; color: #111827; }
      .bv-secondary { border: 1px solid #30363d; background: #161b22; color: #e6edf3; }
      .bv-primary:hover { background: #ffd15c; }
      .bv-secondary:hover { background: #21262d; }
      .bv-status { margin: 0 16px 10px; padding: 8px 10px; border-radius: 7px; font-size: 12px; }
      .bv-status.muted { background: #111827; color: #9ca3af; }
      .bv-status.ok { background: rgba(22,199,132,.12); color: #55e6aa; }
      .bv-status.warn { background: rgba(240,185,11,.13); color: #f7d774; }
      .bv-panel-body { overflow: auto; padding: 0 16px 16px; }
      .bv-day { border-left: 3px solid #f0b90b; background: #161b22; border-radius: 0 7px 7px 0; padding: 10px 12px; margin: 0 0 10px; }
      .bv-day-head { display: flex; justify-content: space-between; gap: 8px; color: #fff; font-weight: 700; font-size: 12px; margin-bottom: 8px; }
      .bv-day-head span:last-child { color: #8b949e; font-weight: 600; }
      .bv-loading, .bv-missing { color: #8b949e; text-align: center; padding: 18px 0; }
      .bv-stock { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 9px 10px; margin-bottom: 9px; }
      .bv-stock-name { color: #fff; font-weight: 750; margin-bottom: 7px; }
      .bv-pills { display: flex; flex-wrap: wrap; gap: 5px; }
      .bv-pills span { color: #d1d5db; background: #111827; border: 1px solid #21262d; border-radius: 999px; padding: 3px 7px; font-size: 11px; }
      .bv-section-label { color: #f0b90b; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .04em; margin: 10px 0 6px; }
      .bv-my-label { color: #e6edf3; }
      .bv-analysis, .bv-news, .bv-homework { background: #0d1117; border: 1px solid #21262d; border-radius: 6px; padding: 9px 10px; margin-bottom: 9px; }
      .bv-analysis-text { color: #d1d5db; white-space: pre-wrap; word-break: break-word; }
      .bv-homework-item { border-left: 2px solid #30363d; padding: 6px 8px; margin-top: 6px; background: #111827; border-radius: 0 5px 5px 0; }
      .bv-homework-topic { color: #f0b90b; font-weight: 700; font-size: 11px; }
      .bv-homework-prompt { color: #d1d5db; line-height: 1.45; margin-top: 2px; }
      .bv-news-item { border-top: 1px solid #21262d; padding-top: 8px; margin-top: 8px; }
      .bv-news-item:first-of-type { border-top: 0; padding-top: 0; margin-top: 0; }
      .bv-news-title { color: #93c5fd; font-weight: 700; line-height: 1.35; }
      .bv-news-summary { color: #c9d1d9; margin-top: 3px; }
      .bv-news-meta { color: #8b949e; font-size: 11px; margin-top: 4px; }
      .bv-note { background: #0d1117; border: 1px solid #21262d; border-radius: 6px; padding: 8px 9px; margin-top: 7px; }
      .bv-note-meta { color: #8b949e; font-size: 11px; margin-bottom: 4px; }
      .bv-note-text { color: #d1d5db; white-space: pre-wrap; word-break: break-word; }
      .bv-empty { color: #8b949e; text-align: center; padding: 40px 0; }
      @media (max-width: 560px) {
        #bv-note-button { top: auto; bottom: 86px; right: 14px; }
      }
    `;
    document.head.appendChild(style);
  }

  injectStyles();
  log('v3.1.0 marker-only integration loaded');
  tick();
  setInterval(tick, POLL_MS);
})();
