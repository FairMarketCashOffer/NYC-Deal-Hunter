import feedparser
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_FEEDS = [
    "https://newyork.craigslist.org/search/rea?query=house&format=rss",
    "https://newyork.craigslist.org/search/rea?query=single%20family&format=rss",
    "https://newyork.craigslist.org/search/rea?query=sfh&format=rss",
    "https://newyork.craigslist.org/search/rea?query=fixer&format=rss",
    "https://newyork.craigslist.org/search/rea?query=vacant&format=rss",
    "https://newyork.craigslist.org/search/rea?query=as-is&format=rss",
    "https://newyork.craigslist.org/search/rea?query=estate%20sale&format=rss",
    "https://newyork.craigslist.org/search/rea?query=owner&format=rss",
    "https://newyork.craigslist.org/search/rea?query=fsbo&format=rss",
    "https://newyork.craigslist.org/search/rea?query=brownstone&format=rss",
    "https://newyork.craigslist.org/search/rea?query=brooklyn&format=rss",
    "https://newyork.craigslist.org/search/rea?query=queens&format=rss",
    "https://newyork.craigslist.org/search/rea?query=east%20new%20york&format=rss"
]

try:
    with open("seen_links.txt", "r") as f:
        seen = set(f.read().splitlines())
except:
    seen = set()

def send(msg):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

for url in RSS_FEEDS:
    feed = feedparser.parse(url)

    for entry in feed.entries:
        if entry.link not in seen:

            title = entry.title.lower()

            keywords = [
                "fixer", "vacant", "as-is", "estate",
                "owner", "fsbo", "brownstone",
                "brooklyn", "queens", "east new york"
            ]

            score = sum(1 for k in keywords if k in title)

            if score >= 1:
                message = f"""🚨 NYC DEAL ALERT

{entry.title}

{entry.link}
"""
                send(message)

            seen.add(entry.link)

with open("seen_links.txt", "w") as f:
    for link in seen:
        f.write(link + "\n")
