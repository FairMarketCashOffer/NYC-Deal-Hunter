import os
import time
import logging

import feedparser
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("nyc-craigslist-bot")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "120"))
SEEN_LINKS_FILE = os.getenv("SEEN_LINKS_FILE", "seen_links.txt")

RSS_FEEDS = [
    "https://newyork.craigslist.org/search/rea?format=rss",
]

EXCLUDE_KEYWORDS = ["staten island"]

CONFIG_OK = bool(BOT_TOKEN) and bool(CHAT_ID)
if not CONFIG_OK:
    log.warning(
        "BOT_TOKEN and/or CHAT_ID are not set. The bot will run but will NOT "
        "send Telegram messages until both env vars are configured on Render."
    )

# ---------------------------------------------------------------------------
# State (seen links)
# ---------------------------------------------------------------------------

def load_seen_links():
    try:
        with open(SEEN_LINKS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()
    except Exception as e:
        log.error(f"Failed to load seen links file, starting empty: {e}")
        return set()


def save_seen_links(seen):
    try:
        with open(SEEN_LINKS_FILE, "w") as f:
            for link in seen:
                f.write(link + "\n")
    except Exception as e:
        log.error(f"Failed to save seen links file: {e}")


seen_links = load_seen_links()

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_message(text):
    if not CONFIG_OK:
        log.info(f"[DRY RUN - no BOT_TOKEN/CHAT_ID] Would have sent:\n{text}")
        return False

    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": text},
            timeout=10,
        )
        if resp.status_code != 200:
            log.error(f"Telegram API returned {resp.status_code}: {resp.text}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        log.error(f"Telegram request failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Core polling logic
# ---------------------------------------------------------------------------

def check_feeds_once():
    global seen_links

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            log.error(f"Failed to parse feed {url}: {e}")
            continue

        if getattr(feed, "bozo", 0) and not getattr(feed, "entries", []):
            log.warning(f"Feed {url} appears malformed, skipping this cycle.")
            continue

        entries = getattr(feed, "entries", [])
        new_count = 0

        for entry in entries:
            title = getattr(entry, "title", "") or ""
            link = getattr(entry, "link", "") or ""

            if not link:
                continue

            title_lower = title.lower()
            if any(keyword in title_lower for keyword in EXCLUDE_KEYWORDS):
                continue

            if link in seen_links:
                continue
            seen_links.add(link)

            message = f"NYC LISTING:\n\n{title}\n\n{link}"
            send_message(message)
            new_count += 1

        if new_count:
            log.info(f"Sent {new_count} new listing(s) from {url}.")
        else:
            log.info(f"No new listings from {url} this cycle.")

    save_seen_links(seen_links)


def main():
    log.info(
        f"NYC-Deal-Hunter starting. Interval={POLL_INTERVAL_SECONDS}s, "
        f"Telegram configured={CONFIG_OK}"
    )
    while True:
        try:
            check_feeds_once()
        except Exception as e:
            # A single bad cycle must never kill the process.
            log.error(f"Unexpected error during feed check cycle: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
