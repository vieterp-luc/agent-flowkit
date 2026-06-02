"""Meta AI (meta.ai/create) UI selectors — centralized so UI drift is patched here.

Verified via scripts/meta_vibes_inspect.py against the /create composer. Re-run that
script and patch below if Meta changes the DOM.
"""

# Create page — composer with image upload + "Create" generate button.
APP_URL = "https://www.meta.ai/create"

# Login redirect detection — URL contains one of these when the session expired.
LOGIN_URL_FRAGMENTS = (
    "facebook.com/login",
    "instagram.com/accounts/login",
    "accountscenter.meta.com",
    "/login",
)

# Prompt composer — stable data-testid shared by a hidden <textarea> backing store
# and the VISIBLE contenteditable editor. Match both; code picks the visible one
# (`:visible`) and types via real key events (Lexical editor ignores value-set).
COMPOSER = '[data-testid="composer-input"]:visible'

# Hidden <input type=file> behind the "+" attachment button. Playwright can set files
# on it directly (no native dialog). accept = images + mp4/mov.
FILE_INPUT = 'input[type="file"]'
ADD_ATTACHMENT_BUTTON = 'button[data-testid="composer-add-attachment-button"]'

# Generate button (composer). Verified label text "Create" (no aria/testid).
CREATE_BUTTON = 'button:has-text("Create")'

# Fallback submit — the blue send-arrow at the composer's bottom-right.
SEND_BUTTON = (
    'button[aria-label*="Send" i], '
    'div[role="button"][aria-label*="Send" i], '
    'button[aria-label*="Generate" i], '
    'button[type="submit"]'
)

# Result-video controls (hover toolbar) — download is the cleanest capture path.
DOWNLOAD_BUTTON = (
    'button[aria-label*="Download" i], '
    'a[aria-label*="Download" i], '
    'button[aria-label*="Tải" i]'
)

# Best-effort dismiss buttons for consent/welcome overlays on a fresh load.
OVERLAY_DISMISS = (
    'button:has-text("Allow all"), '
    'button:has-text("Accept all"), '
    'button:has-text("Got it"), '
    'button:has-text("Continue"), '
    'button[aria-label*="Close" i]'
)

# Quota / safety messages (substring match against page text, lowercase)
BLOCK_MESSAGES = (
    "you've reached your limit",
    "limit reached",
    "try again later",
    "can't help with that",
    "unable to generate",
    "violates our",
    "đã đạt giới hạn",
)
