"""Gemini UI selectors — centralized so UI drift can be patched in one place."""

# Composer (input box)
COMPOSER = '[contenteditable="true"][role="textbox"]'

# Model selector — pillbox button at composer row; opens model menu
MODEL_TRIGGER = '[data-test-id="bard-mode-menu-button"]'
# Model menu items use this class; filter by accessible name to pick Pro/Tư duy/Nhanh
MODEL_MENU_ITEM = 'button.bard-mode-list-button'

# Lyria renders music as <video> with src on contribution.usercontent.google.com/download
MUSIC_VIDEO = 'video[src*="contribution.usercontent.google.com/download"]'

# Download button appears beside the music player when render finishes — exact aria labels
DOWNLOAD_BUTTON = (
    'button[aria-label="Tải bản nhạc xuống"], '
    'button[aria-label*="Download music" i], '
    'button[aria-label*="Download song" i], '
    'button[aria-label*="Download track" i]'
)

# Quota / rate-limit messages (substring match against page text)
QUOTA_MESSAGES = (
    "you've reached your limit",
    "limit reached",
    "đã đạt giới hạn",
    "vượt quá hạn mức",
)

# Login redirect detection — URL contains this when session expired
LOGIN_URL_FRAGMENT = "accounts.google.com"

# Default landing path
APP_URL = "https://gemini.google.com/app"

# "New chat" button — try multiple selectors (UI varies by locale/build)
NEW_CHAT_BUTTON = (
    '[data-test-id="new-chat-button"], '
    'button[aria-label="New chat"], '
    'button[aria-label="Trò chuyện mới"], '
    'button[aria-label="Cuộc trò chuyện mới"], '
    'button[aria-label*="new chat" i], '
    'a[aria-label*="new chat" i]'
)
