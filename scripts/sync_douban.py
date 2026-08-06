#!/usr/bin/env python3
"""Sync Douban marks (books/movies) into _data/douban.json.

Uses the public Douban mobile API to fetch the complete lists of books
(read / reading / want-to-read) and recently watched movies, then writes a
full snapshot to the data file. On any fetch failure the existing data file
is left untouched.

Run from the repo root: python3 scripts/sync_douban.py
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

DOUBAN_USER_ID = "191702958"
API_BASE = f"https://m.douban.com/rexxar/api/v2/user/{DOUBAN_USER_ID}/interests"
DATA_FILE = Path(__file__).resolve().parent.parent / "_data" / "douban.json"

PAGE_SIZE = 50
MAX_MOVIES = 100  # keep the movie list bounded; books are always fetched in full

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Referer": "https://m.douban.com/mine/book",
}

# (type, douban status) -> status key used by the site templates
SOURCES = [
    ("book", "doing", "reading"),
    ("book", "done", "read"),
    ("book", "mark", "want_to_read"),
    ("movie", "done", "watched"),
]


def fetch_page(subject_type, status, start):
    params = urllib.parse.urlencode(
        {"type": subject_type, "status": status, "start": start, "count": PAGE_SIZE}
    )
    request = urllib.request.Request(f"{API_BASE}?{params}", headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_all(subject_type, status, cap=None):
    interests, start, total = [], 0, None
    while total is None or start < total:
        if cap is not None and start >= cap:
            break
        page = fetch_page(subject_type, status, start)
        total = page["total"]
        interests.extend(page["interests"])
        start += PAGE_SIZE
        time.sleep(1)  # be polite to the API
    return interests


def to_entry(interest, category, status_key):
    subject = interest["subject"]
    rating = interest.get("rating") or {}
    authors = subject.get("author") or []
    return {
        "guid": str(interest["id"]),
        "name": subject.get("title", ""),
        "author": ", ".join(authors),
        "link": subject.get("url", ""),
        "category": category,
        "status": status_key,
        "stars": rating.get("star_count") or None,
        "comment": (interest.get("comment") or "").strip(),
        "cover": (subject.get("pic") or {}).get("normal", ""),
        "date": (interest.get("create_time") or "")[:10],
    }


def main():
    entries = []
    try:
        for subject_type, douban_status, status_key in SOURCES:
            cap = MAX_MOVIES if subject_type == "movie" else None
            for interest in fetch_all(subject_type, douban_status, cap=cap):
                entries.append(to_entry(interest, subject_type, status_key))
    except Exception as error:  # noqa: BLE001 - keep old data on any fetch failure
        print(f"Fetch failed, keeping existing data: {error}")
        return 0

    entries.sort(key=lambda e: e["date"], reverse=True)
    DATA_FILE.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Saved {len(entries)} items to {DATA_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
