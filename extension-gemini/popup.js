function fmt(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function render(status, music) {
  const badge = document.getElementById('badge');
  const wsStatus = document.getElementById('ws-status');
  const capturedCount = document.getElementById('captured-count');
  const musicList = document.getElementById('music-list');

  badge.className = `badge ${status.state || 'off'}`;
  badge.textContent = (status.state || 'off').toUpperCase();

  wsStatus.textContent = status.connected ? 'connected' : 'disconnected';
  wsStatus.className = `value ${status.connected ? 'ok' : 'err'}`;

  capturedCount.textContent = status.capturedCount || 0;

  if (!music || !music.length) {
    musicList.innerHTML = '<div class="empty">No music captured yet.<br>Generate music in Gemini chat.</div>';
    return;
  }

  musicList.innerHTML = music.map((m) => `
    <div class="music-entry">
      <span class="time">${fmt(m.capturedAt)}</span>
      <span class="name">${m.filename}</span>
    </div>
  `).join('');
}

async function refresh() {
  const [status, captured] = await Promise.all([
    chrome.runtime.sendMessage({ type: 'STATUS' }),
    chrome.runtime.sendMessage({ type: 'GET_CAPTURED' }),
  ]);
  render(status || {}, captured?.music || []);
}

document.getElementById('btn-reconnect').addEventListener('click', async () => {
  await chrome.runtime.sendMessage({ type: 'RECONNECT' });
  setTimeout(refresh, 300);
});

document.getElementById('btn-clear').addEventListener('click', async () => {
  await chrome.runtime.sendMessage({ type: 'CLEAR_CAPTURED' });
  refresh();
});

refresh();
setInterval(refresh, 2000);
