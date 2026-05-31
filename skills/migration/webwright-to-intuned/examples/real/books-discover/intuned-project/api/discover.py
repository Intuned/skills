# Ported from the books-discover Crafted CLI — faithful 1:1 port.
# Stripped: local Chromium bootstrap AND the craft's Browserbase CDP block
# (BROWSERBASE_API_KEY / connect_over_cdp / advancedStealth / httpx) — Intuned
# injects the page, so no browser-provider code belongs here.
from typing import Any, TypedDict
from urllib.parse import urljoin

from intuned_browser import go_to_url
from playwright.async_api import Page


class Params(TypedDict, total=False):
    start_url: str


async def automation(page: Page, params: Params | None = None, **_kwargs) -> dict[str, Any]:
    params = params or {}
    start_url = params.get("start_url", "https://books.toscrape.com/")

    visited_listing_pages: list[str] = []
    collected_urls: list[str] = []
    current_url = start_url

    while True:
        await go_to_url(page, url=current_url, retries=3)
        visited_listing_pages.append(page.url)

        article_links = await page.locator("article.product_pod h3 a").evaluate_all(
            "elements => elements.map(a => a.getAttribute('href'))"
        )
        collected_urls.extend(urljoin(page.url, href) for href in article_links if href)

        next_locator = page.locator("li.next a")
        if await next_locator.count() == 0:
            break
        next_href = await next_locator.first.get_attribute("href")
        current_url = urljoin(page.url, next_href)

    unique_urls = sorted(set(collected_urls))
    print(f"{len(unique_urls)} unique book URLs across {len(visited_listing_pages)} listing pages")
    return {
        "total_count": len(unique_urls),
        "book_urls": unique_urls,
        "listing_pages_visited": visited_listing_pages,
    }
