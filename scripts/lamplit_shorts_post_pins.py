"""Post pinned-style top-level comments on Lamplit Frankenstein Shorts.

YouTube blocks commentThreads.insert on scheduled/private videos — this
script checks privacy status first and skips any Short that hasn't gone
public yet. Re-run after each scheduled publish time:

  - 25/05 19:00 ICT → post for Short ep9
  - 26/05 19:00 ICT → post for Short ep11
  - 27/05 19:00 ICT → post for Short ep12

YouTube Data API has NO 'pin' endpoint — pinning still requires 1 manual
click in Studio per comment. This script just pre-fills the text.

Idempotent: skips Shorts that already have a comment from the channel
owner with the long-form URL, so re-runs are safe.
"""
import sys
from pathlib import Path

ROOT = Path("/Users/vieterp/code/Research/agent-flowkit")
sys.path.insert(0, str(ROOT))

from youtube.upload import authorize, load_rules
from googleapiclient.discovery import build

CHANNEL = "lamplit-library"
PLAYLIST_URL = ("https://www.youtube.com/playlist?"
                "list=PLTF91ZI8UKnwvRCxoc2LObRIY4bVukCsL")

SHORTS = [
    {"short_id": "foL7pqwSXtE", "ep": 9, "long_form_id": "L_0hMuQvHAE",
     "section": "Justine's trial & confession"},
    {"short_id": "YK0PgyIcXyw", "ep": 11, "long_form_id": "gjsYag6I09Q",
     "section": "Sea of Ice confrontation"},
    {"short_id": "OKtqDN6okOs", "ep": 12, "long_form_id": "l3FJmZqLoiI",
     "section": "the Creature's awakening"},
]


def build_comment(ep: int, long_form_id: str, section: str) -> str:
    return (
        f"Full chapter (10 min deep-dive on Episode {ep} — {section}):\n"
        f"https://youtu.be/{long_form_id}\n\n"
        f"Full Frankenstein series:\n{PLAYLIST_URL}"
    )


def main():
    creds = authorize(CHANNEL)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    rules = load_rules(CHANNEL)
    channel_id = rules["youtube_channel_id"]

    short_ids = [s["short_id"] for s in SHORTS]
    statuses = yt.videos().list(
        part="status,snippet", id=",".join(short_ids),
    ).execute()
    privacy = {v["id"]: v["status"]["privacyStatus"] for v in statuses["items"]}

    for s in SHORTS:
        priv = privacy.get(s["short_id"], "unknown")
        print(f"\n=== Short ep{s['ep']} ({s['short_id']}) — privacy={priv} ===")
        if priv != "public":
            print(f"  → skipped (not public yet; re-run after publish time)")
            continue

        # Idempotency check: any existing comment by owner with our domain?
        try:
            existing = yt.commentThreads().list(
                part="snippet", videoId=s["short_id"], maxResults=20,
                searchTerms="youtu.be",
            ).execute()
            mine = [
                t for t in existing.get("items", [])
                if t["snippet"]["topLevelComment"]["snippet"]
                .get("authorChannelId", {}).get("value") == channel_id
            ]
            if mine:
                cid = mine[0]["id"]
                print(f"  → already commented (id={cid[:12]}...) — skipping")
                continue
        except Exception as e:
            print(f"  (idempotency check skipped: {e})")

        text = build_comment(s["ep"], s["long_form_id"], s["section"])
        try:
            resp = yt.commentThreads().insert(
                part="snippet",
                body={"snippet": {
                    "videoId": s["short_id"],
                    "topLevelComment": {"snippet": {"textOriginal": text}},
                }},
            ).execute()
            print(f"  ✓ posted: {resp['id']}")
            print(f"  → manual pin: Studio → "
                  f"https://studio.youtube.com/video/{s['short_id']}/comments"
                  " → 3-dot on your comment → Pin")
        except Exception as e:
            print(f"  ⚠ failed: {e}")


if __name__ == "__main__":
    main()
