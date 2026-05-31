# Ported from a Webwright Crafted CLI (techcrunch_ai_craft) — faithful 1:1 port.
# Dropped harness param: output_filename (local artifact I/O has no meaning in Intuned).
from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

from intuned_browser import go_to_url
from playwright.async_api import Page


class Params(TypedDict, total=False):
    days_back: int
    category_url: str


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


async def automation(page: Page, params: Params | None = None, **_kwargs) -> dict[str, Any]:
    params = params or {}
    days_back = int(params.get("days_back", 7))
    category_url = params.get("category_url", "https://techcrunch.com/category/startups/")
    if days_back <= 0:
        raise ValueError("days_back must be a positive integer")

    now = datetime.now(timezone.utc).astimezone()
    cutoff = now - timedelta(days=days_back)
    print(f"params: days_back={days_back} category_url={category_url}")

    # page is injected by Intuned — never launch a browser here.
    await go_to_url(page, url=category_url, timeout_s=90, retries=3)

    # Extraction logic preserved verbatim from the craft.
    js = """
    els => els.map((el, i) => {
      const headingLink = el.querySelector('h3 a, h2 a');
      const time = el.querySelector('time');
      const authorLinks = Array.from(el.querySelectorAll('a[href*="/author/"]')).map(x => (x.textContent || '').trim()).filter(Boolean);
      const categoryLinks = Array.from(el.querySelectorAll('a[href*="/category/"], a[href*="/tag/"]')).map(x => (x.textContent || '').trim()).filter(Boolean);
      return {
        i,
        text: (el.innerText || '').trim().slice(0, 300),
        title: headingLink ? (headingLink.textContent || '').trim() : null,
        href: headingLink ? headingLink.href : null,
        datetime: time ? time.getAttribute('datetime') : null,
        time_text: time ? (time.textContent || '').trim() : null,
        authors: authorLinks,
        categories: categoryLinks,
      };
    }).filter(x => x.title && x.href && x.datetime)
    """
    raw_items = await page.locator("main li").evaluate_all(js)
    print(f"extracted {len(raw_items)} raw dated listing items")

    filtered = []
    for item in raw_items:
        dt = _parse_dt(item.get("datetime"))
        if not dt:
            continue
        if dt >= cutoff:
            item["datetime_iso"] = dt.isoformat()
            filtered.append(item)
    filtered.sort(key=lambda x: x["datetime_iso"], reverse=True)
    print(f"{len(filtered)} items match the last-{days_back}-days window")

    return {
        "task": f"Scrape TechCrunch startup news from the last {days_back} days",
        "category_url": category_url,
        "days_back": days_back,
        "run_timestamp": now.isoformat(),
        "cutoff_timestamp": cutoff.isoformat(),
        "count": len(filtered),
        "items": filtered,
        "final_response": f"Scraped {len(filtered)} TechCrunch startup news items from the last {days_back} days.",
    }
