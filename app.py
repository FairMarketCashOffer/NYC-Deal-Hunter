import feedparser
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# NYC REAL ESTATE ONLY (ALL BOROUGHS INCLUDED AUTOMATICALLY)
RSS_FEEDS = [
    "https://newyork.craigslist.org/search/rea?format=rss"
]

try:
    with open("seen_links.txt", "r") as f:
        seen = set(f.read().splitlines())
except:
    seen = set()

def send_message(text):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": text}
    )

for url in RSS_FEEDS:
    feed = feedparser.parse(url)

    for entry in feed.entries:

        title = entry.title.lower()

        # 🚫 EXCLUDE STATEN ISLAND ONLY
        if "staten island" in title:
            continue

        # Always avoid duplicates
        if entry.link in seen:
            continue

        message = f"""🚨 NYC REAL ESTATE ALERT

{entry.title}

{entry.link}
"""

        send_message(message)

        seen.add(entry.link)

with open("seen_links.txt", "w") as f:
    for link in seen:
        f.write(link + "\n")
