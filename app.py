import feedparser
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_URL = "https://newyork.craigslist.org/search/rea?query=multifamily&format=rss"

try:
    with open("seen_links.txt", "r") as f:
        seen_links = set(f.read().splitlines())
except:
    seen_links = set()

feed = feedparser.parse(RSS_URL)

for entry in feed.entries:
    if entry.link not in seen_links:

        message = f"""🚨 NEW PROPERTY ALERT

{entry.title}

{entry.link}
"""

        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": message
            }
        )

        seen_links.add(entry.link)

with open("seen_links.txt", "w") as f:
    for link in seen_links:
        f.write(link + "\n")
