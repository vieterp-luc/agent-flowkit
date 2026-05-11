/**
 * Gemini Bridge — Chrome Extension Background Service Worker
 *
 * Two modes:
 * 1. Passive capture: intercepts music download URLs when user generates in Gemini UI
 * 2. Active generation: sends StreamGenerate request programmatically with captured session params
 *
 * Session params (f.sid, bl, at) are auto-captured from ongoing Gemini requests.
 */

const AGENT_WS_URL = 'ws://127.0.0.1:9223';
const AGENT_HTTP_URL = 'http://127.0.0.1:8100';

let ws = null;
let state = 'off';
let manualDisconnect = false;
let capturedMusic = [];

// Session params captured from ongoing Gemini requests
const sessionParams = { fsid: '', bl: '', at: '', userPrefix: '/u/0', sourcePath: '' };

// ─── Session Param Capture ──────────────────────────────────
// Intercept all Gemini requests to extract f.sid, bl, and at (XSRF) token

chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    const url = details.url;

    // Extract f.sid, bl, and user prefix from batchexecute / StreamGenerate URLs
    if (url.includes('BardChatUi/data/') || url.includes('StreamGenerate')) {
      try {
        const u = new URL(url);
        const fsid = u.searchParams.get('f.sid');
        const bl = u.searchParams.get('bl');
        const sp = u.searchParams.get('source-path');
        if (fsid) sessionParams.fsid = fsid;
        if (bl) sessionParams.bl = bl;
        if (sp) sessionParams.sourcePath = sp;
        // Capture /u/N/ prefix from path (e.g. /u/2/_/BardChatUi/...)
        const prefixMatch = u.pathname.match(/^(\/u\/\d+)/);
        if (prefixMatch) sessionParams.userPrefix = prefixMatch[1];
      } catch {}
    }

    // Extract 'at' XSRF token from POST body of form-encoded requests
    if (details.method === 'POST' && details.requestBody?.formData?.at) {
      const at = details.requestBody.formData.at[0];
      if (at && at.length > 10) sessionParams.at = at;
    }

    // ── Music URL Capture ──
    const isDownload = url.includes('/data/download') || url.includes('BardChatUi/data/download');
    const isMedia = url.includes('.mp4') || url.includes('.m4a') || url.includes('.opus') || url.includes('.webm');
    const hasOpi = url.includes('opi=');

    if (url.includes('gemini.google.com') && (isDownload || (isMedia && hasOpi) || details.type === 'media')) {
      const isDupe = capturedMusic.some(
        (m) => m.url === url && Date.now() - new Date(m.capturedAt).getTime() < 10000
      );
      if (!isDupe) {
        const entry = { id: `music_${Date.now()}`, url, capturedAt: new Date().toISOString(), filename: _extractFilename(url) };
        capturedMusic.unshift(entry);
        if (capturedMusic.length > 50) capturedMusic.pop();
        console.log('[GeminiBridge] Music captured:', entry.filename);
        notifyAgent({ type: 'music_captured', entry });
        _fetchAndUploadMusic(entry);
      }
    }
  },
  { urls: ['https://gemini.google.com/*', 'https://*.googleapis.com/*'] },
  ['requestBody'],
);

function _extractFilename(url) {
  const paramMatch = url.match(/[?&]filename=([^&]+\.mp4)/i);
  if (paramMatch) return decodeURIComponent(paramMatch[1]);
  const pathMatch = url.match(/([^/&?=]+\.mp4)/i);
  return pathMatch ? decodeURIComponent(pathMatch[1]) : `gemini_music_${Date.now()}.mp4`;
}

// ─── Music Generation ───────────────────────────────────────

// f.req template for StreamGenerate music request
// Structure reverse-engineered from live Gemini traffic
function _buildFReq(prompt, atToken) {
  const uuid = crypto.randomUUID().toUpperCase();
  const inner = [
    [prompt, 0, null, null, null, null, 0],
    ['vi'],
    ['', '', '', null, null, null, null, null, null, ''],
    atToken,
    '',         // conversation ID — empty = new conversation
    null,
    [1],        // music mode flag
    1, null, null, 1, 0,
    null, null, null, null, null,
    [[0]],
    0, null, null, null, null, null, null, null, null,
    1, null, null,
    [4],        // lyria/music tool
    null, null, null, null, null, null, null, null, null, null,
    [1],
    null, null, null, null, null, null, null,
    21,
    null, null, null, 0, null, null, null, null, null,
    uuid,
    null, [], null, null, null, null, null,
    0, 2, null, null, null, null, null, null, null, null, null, null,
    3,
  ];
  return JSON.stringify([null, JSON.stringify([inner])]);
}

async function handleGenerateMusic(msg) {
  const { id, params } = msg;
  const { prompt, lang = 'vi' } = params;

  if (!sessionParams.fsid || !sessionParams.bl || !sessionParams.at) {
    sendToAgent({ id, error: 'SESSION_PARAMS_MISSING — open gemini.google.com and interact first' });
    return;
  }

  setState('running');

  const reqid = Math.floor(Math.random() * 9000000) + 1000000;
  const prefix = sessionParams.userPrefix || '/u/0';
  let url = `https://gemini.google.com${prefix}/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate`
    + `?bl=${encodeURIComponent(sessionParams.bl)}`
    + `&f.sid=${sessionParams.fsid}`
    + `&hl=${lang}`
    + `&_reqid=${reqid}`
    + `&rt=c`;
  if (sessionParams.sourcePath) {
    url += `&source-path=${encodeURIComponent(sessionParams.sourcePath)}`;
  }

  const body = new URLSearchParams({
    'f.req': _buildFReq(prompt, sessionParams.at),
    'at': sessionParams.at,
  });

  // Record how many music entries exist before the request
  const prevCount = capturedMusic.length;

  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
      credentials: 'include',
      body: body.toString(),
    });

    if (!resp.ok) {
      sendToAgent({ id, error: `STREAM_GENERATE_HTTP_${resp.status}` });
      setState('idle');
      return;
    }

    console.log('[GeminiBridge] StreamGenerate sent, waiting for music URL...');

    // Wait up to 3 minutes for music download URL to be captured
    const entry = await _waitForNewMusic(prevCount, 180000);
    if (entry) {
      sendToAgent({ id, result: { ok: true, entry } });
    } else {
      sendToAgent({ id, error: 'MUSIC_TIMEOUT — no download URL captured within 3 minutes' });
    }
  } catch (e) {
    sendToAgent({ id, error: e.message || 'GENERATE_FAILED' });
  }

  setState('idle');
}

function _waitForNewMusic(prevCount, timeoutMs) {
  return new Promise((resolve) => {
    const deadline = Date.now() + timeoutMs;
    const check = setInterval(() => {
      if (capturedMusic.length > prevCount) {
        clearInterval(check);
        resolve(capturedMusic[0]);
      } else if (Date.now() > deadline) {
        clearInterval(check);
        resolve(null);
      }
    }, 1000);
  });
}

// ─── Music Download via Extension ───────────────────────────

async function _fetchAndUploadMusic(entry) {
  try {
    const resp = await fetch(entry.url, { credentials: 'include' });
    if (!resp.ok) { console.error('[GeminiBridge] Music fetch failed:', resp.status); return; }
    const blob = await resp.blob();
    const form = new FormData();
    form.append('file', blob, entry.filename);
    form.append('id', entry.id);
    form.append('filename', entry.filename);
    const up = await fetch(`${AGENT_HTTP_URL}/api/gemini/music-upload`, { method: 'POST', body: form });
    const result = await up.json();
    console.log('[GeminiBridge] Music uploaded:', result.path, `${result.size_kb}KB`);
  } catch (e) {
    console.error('[GeminiBridge] Music upload error:', e);
  }
}

// ─── Startup ────────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(init);
chrome.runtime.onStartup.addListener(init);

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'reconnect') connectToAgent();
  if (alarm.name === 'keepAlive') keepAlive();
});

async function init() {
  const data = await chrome.storage.local.get(['capturedMusic', 'sessionParams']);
  if (data.capturedMusic) capturedMusic = data.capturedMusic;
  if (data.sessionParams) Object.assign(sessionParams, data.sessionParams);
  connectToAgent();
  chrome.alarms.create('keepAlive', { periodInMinutes: 0.4 });
}

// ─── WebSocket to Agent ─────────────────────────────────────

function connectToAgent() {
  if (manualDisconnect) return;
  if (ws?.readyState === WebSocket.CONNECTING) return;
  if (ws?.readyState === WebSocket.OPEN) return;
  try { ws = new WebSocket(AGENT_WS_URL); } catch (e) { scheduleReconnect(); return; }

  ws.onopen = () => {
    chrome.alarms.clear('reconnect');
    setState('idle');
    ws.send(JSON.stringify({
      type: 'extension_ready',
      client: 'gemini-bridge',
      capturedCount: capturedMusic.length,
      sessionReady: !!(sessionParams.fsid && sessionParams.at),
    }));
  };

  ws.onmessage = async ({ data }) => {
    try {
      const msg = JSON.parse(data);
      if (msg.method === 'generate_music') await handleGenerateMusic(msg);
      else if (msg.method === 'get_captured') sendToAgent({ id: msg.id, result: { music: capturedMusic } });
      else if (msg.method === 'get_session_status') {
        sendToAgent({ id: msg.id, result: {
          sessionReady: !!(sessionParams.fsid && sessionParams.at),
          hasFsid: !!sessionParams.fsid,
          hasBl: !!sessionParams.bl,
          hasAt: !!sessionParams.at,
          userPrefix: sessionParams.userPrefix,
          sourcePath: sessionParams.sourcePath,
        }});
      }
    } catch (e) { console.error('[GeminiBridge] Message error:', e); }
  };

  ws.onclose = () => { setState('off'); if (!manualDisconnect) scheduleReconnect(); };
  ws.onerror = (e) => console.error('[GeminiBridge] WS error:', e);
}

function scheduleReconnect() { chrome.alarms.create('reconnect', { delayInMinutes: 0.083 }); }
function keepAlive() {
  if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'ping' }));
  else connectToAgent();
}
function notifyAgent(msg) { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg)); }
function sendToAgent(msg) {
  if (msg.id) {
    fetch(`${AGENT_HTTP_URL}/api/gemini/callback`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(msg),
    }).catch(() => { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg)); });
    return;
  }
  if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg));
}

// ─── State & Badge ──────────────────────────────────────────

function setState(newState) {
  state = newState;
  chrome.action.setBadgeText({ text: { idle: '●', running: '▶', off: '○' }[state] || '' });
  chrome.action.setBadgeBackgroundColor({ color: { idle: '#8b5cf6', running: '#f59e0b', off: '#6b7280' }[state] || '#000' });
}

// ─── Popup Messages ─────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, _, reply) => {
  if (msg.type === 'STATUS') {
    reply({ connected: ws?.readyState === WebSocket.OPEN, state, capturedCount: capturedMusic.length,
            sessionReady: !!(sessionParams.fsid && sessionParams.at) });
    return true;
  }
  if (msg.type === 'GET_CAPTURED') { reply({ music: capturedMusic.slice(0, 20) }); return true; }
  if (msg.type === 'MUSIC_URL_FROM_PAGE') {
    const url = msg.url;
    const isDupe = capturedMusic.some((m) => m.url === url && Date.now() - new Date(m.capturedAt).getTime() < 10000);
    if (!isDupe) {
      const entry = { id: `music_${Date.now()}`, url, capturedAt: msg.time, filename: _extractFilename(url) };
      capturedMusic.unshift(entry);
      if (capturedMusic.length > 50) capturedMusic.pop();
      notifyAgent({ type: 'music_captured', entry });
      _fetchAndUploadMusic(entry);
    }
    reply({ ok: true }); return true;
  }
  if (msg.type === 'CLEAR_CAPTURED') { capturedMusic = []; chrome.storage.local.set({ capturedMusic: [] }); reply({ ok: true }); return true; }
  if (msg.type === 'DISCONNECT') { manualDisconnect = true; if (ws) ws.close(); reply({ ok: true }); return true; }
  if (msg.type === 'RECONNECT') { manualDisconnect = false; connectToAgent(); reply({ ok: true }); return true; }
  return true;
});

console.log('[GeminiBridge] Extension loaded');
