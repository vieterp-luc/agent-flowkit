/**
 * Gemini Bridge — Content Script
 * Intercepts fetch/XHR on gemini.google.com to capture music download URLs.
 * Sends captured URLs to background service worker for forwarding to local agent.
 */

(function () {
  if (window.__geminiBridgeInjected) return;
  window.__geminiBridgeInjected = true;

  // Intercept fetch to capture music download requests
  const _origFetch = window.fetch;
  window.fetch = async function (...args) {
    const req = args[0];
    const url = typeof req === 'string' ? req : req?.url || '';

    // Gemini music downloads: /data/download?c=...&opi=...
    if (url.includes('/data/download') || (url.includes('opi=') && (url.includes('.mp4') || url.includes('.m4a')))) {
      chrome.runtime.sendMessage({
        type: 'MUSIC_URL_FROM_PAGE',
        url,
        time: new Date().toISOString(),
      }).catch(() => {});
    }

    return _origFetch.apply(this, args);
  };

  // Also intercept XMLHttpRequest
  const _origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    if (typeof url === 'string' && (url.includes('/data/download') || url.includes('.mp4'))) {
      chrome.runtime.sendMessage({
        type: 'MUSIC_URL_FROM_PAGE',
        url,
        time: new Date().toISOString(),
      }).catch(() => {});
    }
    return _origOpen.apply(this, [method, url, ...rest]);
  };

  console.log('[GeminiBridge] Content script active');
})();
