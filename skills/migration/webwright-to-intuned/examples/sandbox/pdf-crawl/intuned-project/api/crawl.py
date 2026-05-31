# Ported from the sandbox-pdf-crawl Crafted CLI — faithful 1:1 port.
import re
from typing import Any, TypedDict
from urllib.parse import urljoin

from intuned_browser import go_to_url
from playwright.async_api import Page


class Params(TypedDict, total=False):
    start_url: str
    max_pages: int


async def _find_next_page_url(page: Page) -> str | None:
    # Preserved verbatim from the craft.
    next_candidates = page.locator(
        "a[rel='next'], a[aria-label*='Next' i], a:has-text('Next'), button:has-text('Next')"
    )
    if await next_candidates.count() > 0:
        first = next_candidates.first
        tag = await first.evaluate("el => el.tagName.toLowerCase()")
        if tag == "a":
            href = await first.get_attribute("href")
            if href:
                return urljoin(page.url, href)
    numbered_links = page.locator("a[href]")
    current_match = re.search(r"(?:page=|/page/)(\d+)", page.url)
    current_num = int(current_match.group(1)) if current_match else 1
    count = await numbered_links.count()
    for i in range(count):
        href = await numbered_links.nth(i).get_attribute("href")
        text = (await numbered_links.nth(i).inner_text()).strip()
        if not href:
            continue
        absolute = urljoin(page.url, href)
        match = re.search(r"(?:page=|/page/)(\d+)", absolute)
        if match and int(match.group(1)) == current_num + 1:
            return absolute
        if text.isdigit() and int(text) == current_num + 1:
            return absolute
    return None


async def automation(page: Page, params: Params | None = None, **_kwargs) -> dict[str, Any]:
    params = params or {}
    start_url = params.get("start_url", "https://sandbox.intuned.dev/pdfs")
    max_pages = int(params.get("max_pages", 25))

    visited_pages: list[str] = []
    records_by_pdf: dict[str, dict[str, str]] = {}
    current_url = start_url
    page_index = 1

    while current_url and page_index <= max_pages:
        visited_pages.append(current_url)
        print(f"open listing page {page_index} at {current_url}")
        await go_to_url(page, url=current_url, retries=3)

        rows = page.locator("table tbody tr")
        row_count = await rows.count()
        for i in range(row_count):
            cells = rows.nth(i).locator("td")
            if await cells.count() < 4:
                continue
            name = (await cells.nth(0).inner_text()).strip()
            manufacturer = (await cells.nth(1).inner_text()).strip()
            pdf_href = await cells.nth(3).locator("a").get_attribute("href")
            if not pdf_href:
                continue
            pdf_url = urljoin(page.url, pdf_href)
            if pdf_url not in records_by_pdf:
                records_by_pdf[pdf_url] = {
                    "product_name": name,
                    "manufacturer": manufacturer,
                    "pdf_url": pdf_url,
                }

        next_url = await _find_next_page_url(page)
        if next_url and next_url not in visited_pages:
            current_url = next_url
            page_index += 1
        else:
            current_url = ""

    final_records = sorted(
        records_by_pdf.values(),
        key=lambda r: (r["manufacturer"], r["product_name"], r["pdf_url"]),
    )
    print(f"{len(final_records)} unique PDF records across {len(visited_pages)} page(s)")
    return {
        "start_url": start_url,
        "visited_pages": visited_pages,
        "records": final_records,
        "total_count": len(final_records),
    }
