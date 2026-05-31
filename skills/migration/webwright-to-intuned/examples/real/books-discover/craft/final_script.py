import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urljoin

import httpx
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent


def next_run_dir() -> Path:
    final_runs = WORKSPACE_DIR / "final_runs"
    final_runs.mkdir(exist_ok=True)
    existing = []
    for child in final_runs.iterdir():
        if child.is_dir() and child.name.startswith("run_"):
            try:
                existing.append(int(child.name.split("_")[1]))
            except Exception:
                pass
    return final_runs / f"run_{(max(existing) + 1) if existing else 1}"


async def create_browserbase_session() -> Dict[str, str]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.browserbase.com/v1/sessions",
            headers={
                "x-bb-api-key": os.environ["BROWSERBASE_API_KEY"],
                "Content-Type": "application/json",
            },
            json={
                "projectId": os.environ["BROWSERBASE_PROJECT_ID"],
                "proxies": True,
                "browserSettings": {"advancedStealth": True},
                "timeout": 900,
            },
        )
        response.raise_for_status()
        return response.json()


async def open_browser(playwright) -> Tuple[Browser, BrowserContext, Page, str]:
    browser_mode = os.environ.get("BROWSER_MODE", "browserbase").lower()
    if browser_mode == "local":
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 2200})
        page = await context.new_page()
        return browser, context, page, browser_mode
    session = await create_browserbase_session()
    browser = await playwright.chromium.connect_over_cdp(session["connectUrl"])
    context = browser.contexts[0] if browser.contexts else await browser.new_context(viewport={"width": 1440, "height": 2200})
    page = context.pages[0] if context.pages else await context.new_page()
    await page.set_viewport_size({"width": 1440, "height": 2200})
    return browser, context, page, browser_mode


async def crawl_book_catalogue(start_url: str = "https://books.toscrape.com/", output_json_name: str = "book_urls.json") -> Dict[str, object]:
    """Crawl the Books to Scrape catalogue and collect all unique book detail URLs.

    Args:
        start_url (str): Starting catalogue URL to begin crawling from. Must be a fully
            qualified HTTP or HTTPS URL that points to the Books to Scrape homepage or
            another catalogue listing page. Default is "https://books.toscrape.com/".
        output_json_name (str): Filename for the JSON artifact containing the complete
            de-duplicated list of book detail page URLs and the total count. Provide a
            relative filename such as "book_urls.json". Default is "book_urls.json".

    Returns:
        Dict[str, object]: A dictionary containing "total_count" for the number of
        unique book detail URLs and "book_urls" for the ordered de-duplicated list.
    """
    run_dir = next_run_dir()
    screenshots_dir = run_dir / "screenshots"
    log_path = run_dir / "final_script_log.txt"
    output_path = run_dir / output_json_name
    run_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    log_path.write_text("", encoding="utf-8")

    def log(message: str) -> None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(message + "\n")
        print(message)

    log(f"step 0 params: start_url={start_url} output_json_name={output_json_name}")

    async def capture(page: Page, step_number: int, action: str) -> None:
        await page.screenshot(path=str(screenshots_dir / f"final_execution_{step_number}_{action}.png"), full_page=True)

    async with async_playwright() as playwright:
        browser, context, page, browser_mode = await open_browser(playwright)
        log(f"step 1 action: opened browser in mode={browser_mode}")

        current_url = start_url
        seen_book_urls = set()
        ordered_book_urls: List[str] = []
        page_index = 0

        while True:
            page_index += 1
            await page.goto(current_url, wait_until="domcontentloaded")
            await page.wait_for_selector("article.product_pod h3 a")
            listing_url = page.url
            title = await page.title()
            pager_locator = page.locator("li.current")
            pager_text = (await pager_locator.inner_text()).strip() if await pager_locator.count() else ""
            anchors = page.locator("article.product_pod h3 a")
            count = await anchors.count()
            page_urls: List[str] = []
            for i in range(count):
                href = await anchors.nth(i).get_attribute("href")
                absolute = urljoin(listing_url, href or "")
                page_urls.append(absolute)
                if absolute not in seen_book_urls:
                    seen_book_urls.add(absolute)
                    ordered_book_urls.append(absolute)

            has_next = await page.locator("li.next a").count() > 0
            log(f"step {page_index + 1} action: opened listing page index={page_index} url={listing_url} title={title!r} pager={pager_text!r} extracted_this_page={len(page_urls)} unique_total={len(ordered_book_urls)} has_next={has_next}")

            if page_index == 1:
                await capture(page, page_index + 1, "homepage_catalogue")
            elif has_next:
                await capture(page, page_index + 1, "intermediate_pagination")
            else:
                await capture(page, page_index + 1, "final_catalogue_page")

            if not has_next:
                log(f"step {page_index + 2} action: reached final catalogue page with no next control visible unique_total={len(ordered_book_urls)}")
                break

            next_href = await page.locator("li.next a").get_attribute("href")
            current_url = urljoin(listing_url, next_href or "")
            log(f"step {page_index + 2} action: followed next pagination to {current_url}")

        result = {"total_count": len(ordered_book_urls), "book_urls": ordered_book_urls}
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        log(f"step {page_index + 3} action: wrote deduplicated results to {output_path.name} total_count={result['total_count']}")

        preview_items = "".join(f"<li><a href=\"{u}\">{u}</a></li>" for u in ordered_book_urls[:25])
        summary_html = run_dir / "summary.html"
        summary_html.write_text(
            "<html><body><h1>Collected book detail URLs</h1>"
            f"<p>Total count: {result['total_count']}</p>"
            f"<p>First URL: {ordered_book_urls[0] if ordered_book_urls else ''}</p>"
            f"<p>Last URL: {ordered_book_urls[-1] if ordered_book_urls else ''}</p>"
            "<h2>Preview of first 25 URLs</h2><ol>" + preview_items + "</ol></body></html>",
            encoding="utf-8",
        )
        await page.goto(summary_html.as_uri(), wait_until="load")
        log(f"step {page_index + 4} action: displayed final collected-result summary with total_count={result['total_count']}")
        await capture(page, page_index + 4, "results_summary")
        log(f"final response: total_count={result['total_count']} book_urls_json={output_path.name}")
        await context.close()
        await browser.close()
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Books to Scrape catalogue pages and collect unique book detail URLs.")
    parser.add_argument(
        "--start_url",
        type=str,
        default="https://books.toscrape.com/",
        help="Starting catalogue URL to begin crawling from. Must be a fully qualified HTTP or HTTPS URL that points to the Books to Scrape homepage or another catalogue listing page. Default is https://books.toscrape.com/.",
    )
    parser.add_argument(
        "--output_json_name",
        type=str,
        default="book_urls.json",
        help="Filename for the JSON artifact containing the complete de-duplicated list of book detail page URLs and the total count. Provide a relative filename such as book_urls.json. Default is book_urls.json.",
    )
    asyncio.run(crawl_book_catalogue(start_url=parser.parse_args().start_url, output_json_name=parser.parse_args().output_json_name))
