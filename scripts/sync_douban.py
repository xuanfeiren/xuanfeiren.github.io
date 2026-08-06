#!/usr/bin/env python3
"""Sync Douban marks (books/movies/music) into _data/douban.json.

Fetches the public RSS feed of Douban user interests and merges new items
into the existing data file, so history accumulates over time even though
the feed only exposes the ~10 most recent marks.

Run from the repo root: python3 scripts/sync_douban.py
"""

import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

DOUBAN_USER_ID = "191702958"
FEED_URL = f"https://www.douban.com/feed/people/{DOUBAN_USER_ID}/interests"
DATA_FILE = Path(__file__).resolve().parent.parent / "_data" / "douban.json"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# Order matters: longer prefixes must be tried first.
STATUS_PREFIXES = [
    ("最近在读", "reading"),
    ("在读", "reading"),
    ("读过", "read"),
    ("想读", "want_to_read"),
    ("最近在看", "watching"),
    ("在看", "watching"),
    ("看过", "watched"),
    ("想看", "want_to_watch"),
    ("最近在听", "listening"),
    ("在听", "listening"),
    ("听过", "listened"),
    ("想听", "want_to_listen"),
]

RATING_STARS = {"力荐": 5, "推荐": 4, "还行": 3, "较差": 2, "很差": 1}


def category_of(link):
    if "book.douban.com" in link:
        return "book"
    if "movie.douban.com" in link:
        return "movie"
    if "music.douban.com" in link:
        return "music"
    return "other"


def parse_item(item):
    title = item.findtext("title", "").strip()
    link = item.findtext("link", "").strip()
    guid = item.findtext("guid", "").strip()
    description = item.findtext("description", "") or ""
    pub_date = item.findtext("pubDate", "").strip()

    status, name = "", title
    for prefix, key in STATUS_PREFIXES:
        if title.startswith(prefix):
            status, name = key, title[len(prefix):].strip()
            break
    if not status:
        return None  # not an interest mark (e.g. a status update)

    rating_match = re.search(r"推荐:\s*([^<\s]+)", description)
    comment_match = re.search(r"备注:\s*(.+?)</p>", description, re.S)
    cover_match = re.search(r'<img src="([^"]+)"', description)

    try:
        date = parsedate_to_datetime(pub_date).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        date = ""

    return {
        "guid": guid,
        "name": name,
        "link": link,
        "category": category_of(link),
        "status": status,
        "stars": RATING_STARS.get(rating_match.group(1)) if rating_match else None,
        "comment": comment_match.group(1).strip() if comment_match else "",
        "cover": cover_match.group(1) if cover_match else "",
        "date": date,
    }


def main():
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            feed = response.read()
    except Exception as error:  # noqa: BLE001 - keep old data on any fetch failure
        print(f"Fetch failed, keeping existing data: {error}")
        return 0

    items = [parse_item(i) for i in ET.fromstring(feed).iter("item")]
    items = [i for i in items if i]

    existing = []
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    # Merge: newest mark per subject wins (e.g. "reading" later becomes "read").
    by_link = {entry["link"]: entry for entry in sorted(existing, key=lambda e: e["date"])}
    for entry in sorted(items, key=lambda e: e["date"]):
        by_link[entry["link"]] = entry

    merged = sorted(by_link.values(), key=lambda e: e["date"], reverse=True)
    DATA_FILE.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Saved {len(merged)} items ({len(items)} in feed) to {DATA_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
