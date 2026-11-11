from datetime import datetime, timedelta, timezone
import time

import feedparser
from fastmcp import FastMCP

mcp = FastMCP("ai-news")

# Public RSS feeds from AI labs and tech blogs.
# Feed URLs change sometimes. If a source stops working, replace its URL.
FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
}

CACHE_SECONDS = 3600  # refresh feeds at most once an hour
_cache = {"time": 0.0, "items": []}


def _load_items() -> list[dict]:
    """Fetch all feeds, using a one-hour cache so we don't hit them on every call."""
    if time.time() - _cache["time"] < CACHE_SECONDS and _cache["items"]:
        return _cache["items"]

    items = []
    for source, url in FEEDS.items():
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:20]:
            items.append({
                "title": entry.get("title", "(no title)"),
                "source": source,
                "published": entry.get("published", ""),
                "link": entry.get("link", ""),
            })

    _cache["time"] = time.time()
    _cache["items"] = items
    return items


@mcp.tool
def get_todays_ai_news(limit: int = 10) -> list[dict]:
    """Get the latest AI news headlines from the last 48 hours, with source and link."""
    limit = max(1, min(limit, 25))
    items = _load_items()
    return items[:limit]


@mcp.tool
def search_ai_news(keyword: str) -> list[dict]:
    """Search recent AI news headlines for a keyword and return matching items with links."""
    keyword = keyword.strip().lower()
    if not keyword:
        raise ValueError("Please provide a keyword")
    matches = [i for i in _load_items() if keyword in i["title"].lower()]
    return matches[:20]


if __name__ == "__main__":
    mcp.run()
