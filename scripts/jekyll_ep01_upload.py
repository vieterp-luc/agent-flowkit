"""Upload Jekyll & Hyde ep1 long-form + 3 Shorts to Lamplit Library.

Sequencing (Shorts-FIRST per pilot strategy):
- Short 1: Mon 2026-06-08 19:00 ICT — sets feed signal
- Short 2: Wed 2026-06-10 19:00 ICT
- Short 3: Fri 2026-06-12 19:00 ICT
- Long-form Sun 2026-06-14 19:00 ICT — rewards subscribed viewers
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/Users/vieterp/code/Research/agent-flowkit")
sys.path.insert(0, str(ROOT))

from youtube.upload import upload_video, authorize, load_rules
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ICT = timezone(timedelta(hours=7))
CHANNEL = "lamplit-library"
PLAYLIST_URL = ("https://www.youtube.com/playlist?"
                "list=PLTF91ZI8UKnwvRCxoc2LObRIY4bVukCsL")

EP_DIR = ROOT / "output/jekyll_hyde_classics_en/ep01_story_of_the_door"
LONG_FORM = EP_DIR / "ep01_final_branded.mp4"
THUMB = EP_DIR / "thumbnails/thumbnail_ep01_yt.png"
SHORTS_DIR = ROOT / "output/jekyll_hyde_classics_en/shorts"


SHORTS = [
    {"file": SHORTS_DIR / "short_ep01_a.mp4",
     "title": "WHO IS THE MAN ATTACKING LONDON? — Jekyll & Hyde Ep 1 #Shorts",
     "hook_blurb": ("A respected London doctor. A stranger no one can describe. "
                    "Tonight on Lamplit Library — the door no one should open."),
     "section": "the door no one should open",
     "publish_at": datetime(2026, 6, 8, 19, 0, 0, tzinfo=ICT)},
    {"file": SHORTS_DIR / "short_ep01_b.mp4",
     "title": "A WILL THAT MAKES NO SENSE — Jekyll & Hyde Ep 1 #Shorts",
     "hook_blurb": ("Why would Dr Jekyll leave everything to a stranger? "
                    "The lawyer Utterson begins to unravel a hidden truth."),
     "section": "the will that should not exist",
     "publish_at": datetime(2026, 6, 10, 19, 0, 0, tzinfo=ICT)},
    {"file": SHORTS_DIR / "short_ep01_c.mp4",
     "title": "I HAVE SEEN HIS FACE — Jekyll & Hyde Ep 1 #Shorts",
     "hook_blurb": ("In the foggy London street, Utterson finally meets "
                    "Edward Hyde. And the meeting only makes it worse."),
     "section": "Utterson meets Edward Hyde",
     "publish_at": datetime(2026, 6, 12, 19, 0, 0, tzinfo=ICT)},
]

LONG_FORM_TITLE = ("Why Dr Jekyll Hides a Stranger in His House | "
                   "Jekyll & Hyde Ep 1")
LONG_FORM_PUBLISH = datetime(2026, 6, 14, 19, 0, 0, tzinfo=ICT)
LONG_FORM_DESC = (
    "We open Robert Louis Stevenson's The Strange Case of Dr Jekyll and Mr Hyde "
    "with the first three chapters — a door, a will, and a stranger named Edward "
    "Hyde. Mr Utterson the lawyer begins to suspect that his old friend Dr Jekyll "
    "is being blackmailed by a creature no one can describe.\n\n"
    "Chapters:\n"
    "00:00 Hook\n"
    "01:00 The door, the trampled girl, the cheque\n"
    "03:30 The will that makes no sense\n"
    "05:30 Dr Lanyon and a broken friendship\n"
    "07:00 Utterson meets Hyde in the fog\n"
    "08:30 Inside Jekyll's house — the same building\n"
    "10:00 Jekyll's promise — and his fear\n\n"
    f"📚 Full Jekyll & Hyde series playlist:\n{PLAYLIST_URL}\n\n"
    "💬 Tell me below: at what moment did you first feel something was truly "
    "wrong with Mr Hyde?\n"
    "🕯️ A new chapter every Sunday — subscribe to not miss the next page.\n\n"
    "📚 Source text: Project Gutenberg (public domain)\n"
    "🎙️ Narrated by AI for educational discussion\n\n"
    "Lamplit Library — Classics, one chapter at a time.\n\n"
    "#JekyllAndHyde #RobertLouisStevenson #GothicLiterature #ClassicLiterature "
    "#BookPodcast #LamplitLibrary #VictorianHorror")

LONG_FORM_TAGS = [
    "jekyll and hyde", "robert louis stevenson", "gothic literature",
    "classic literature", "victorian horror", "book summary",
    "chapter analysis", "literary podcast", "audiobook",
    "lamplit library", "literature explained",
]


def upload_short(s, yt):
    desc = (f"{s['hook_blurb']}\n\n"
            f"▶ Full chapter (10 min deep-dive) — dropping Sunday 14 June:\n"
            "https://www.youtube.com/@lamplitlibrary\n\n"
            f"📚 Lamplit Library series playlist:\n{PLAYLIST_URL}\n\n"
            "#Shorts #JekyllAndHyde #ClassicLiterature #GothicLiterature "
            "#BookPodcast #LamplitLibrary")
    tags = ["shorts", "jekyll and hyde", "robert louis stevenson",
            "gothic literature", "classic literature", "book podcast",
            "lamplit library", "literature explained"]
    print(f"\n=== Uploading Short: {s['title'][:50]}... ===")
    vid = upload_video(
        channel_name=CHANNEL, video_path=str(s["file"]),
        title=s["title"][:100], description=desc, tags=tags,
        category_id="27",
        publish_at=s["publish_at"].isoformat(),
    )
    print(f"  ✓ {vid}  publish={s['publish_at'].isoformat()}")
    return vid


def main():
    if not LONG_FORM.exists():
        print(f"⚠ long-form not found: {LONG_FORM}")
        sys.exit(1)
    if not THUMB.exists():
        print(f"⚠ thumbnail not found: {THUMB}")
        sys.exit(1)
    for s in SHORTS:
        if not s["file"].exists():
            print(f"⚠ short not found: {s['file']}")
            sys.exit(1)

    creds = authorize(CHANNEL)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

    # 1. Upload 3 Shorts (scheduled)
    short_ids = []
    for s in SHORTS:
        vid = upload_short(s, yt)
        short_ids.append(vid)

    # 2. Upload long-form (scheduled Sunday)
    print(f"\n=== Uploading long-form ep1 ===")
    long_vid = upload_video(
        channel_name=CHANNEL, video_path=str(LONG_FORM),
        title=LONG_FORM_TITLE[:100],
        description=LONG_FORM_DESC, tags=LONG_FORM_TAGS,
        category_id="27",
        publish_at=LONG_FORM_PUBLISH.isoformat(),
    )
    print(f"  ✓ {long_vid}  publish={LONG_FORM_PUBLISH.isoformat()}")

    # 3. Set thumbnail
    media = MediaFileUpload(str(THUMB), mimetype="image/png")
    yt.thumbnails().set(videoId=long_vid, media_body=media).execute()
    print("  ✓ thumbnail set")

    # 4. Save mapping
    out = EP_DIR / "upload_ids.json"
    out.write_text(json.dumps({
        "long_form": long_vid,
        "shorts": short_ids,
    }, indent=2))
    print(f"\nSaved IDs: {out}")


if __name__ == "__main__":
    main()
