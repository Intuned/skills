import argparse
import asyncio
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List
from urllib.parse import urljoin

from playwright.async_api import async_playwright

WORKSPACE = Path(__file__).resolve().parent
FINAL_RUNS_DIR = WORKSPACE / "final_runs"


def crawl_pdf_listing(start_url: str = "https://sandbox.intuned.dev/pdfs", max_pages: int = 25) -> Dict[str, object]:
    """Crawl the Intuned PDFs listing and collect unique PDF document records.

    Args:
        start_url (str): The PDFs listing page URL to crawl. Accepted format is an
            absolute HTTP or HTTPS URL. Default is "https://sandbox.intuned.dev/pdfs".
        max_pages (int): Maximum number of listing pages to crawl as a safety bound
            when pagination is present. Accepted values are positive integers.
            Default is 25.

    Returns:
        Dict[str, object]: A dictionary containing the resolved start URL, the
        visited page URLs, the de-duplicated list of extracted records under
        "records", and the final unique record count under "total_count".
    """

    async def _run() -> Dict[str, object]:
        run_dir = _create_run_dir()
        screenshots_dir = run_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        run_log = run_dir / "final_script_log.txt"
        run_log.write_text("")
        shutil.copy2(Path(__file__), run_dir / "final_script.py")

        step = 0

        def log(message: str) -> None:
            with run_log.open("a", encoding="utf-8") as f:
                f.write(message + "\n")
            print(message)

        log(f"step 0 params: start_url={start_url} max_pages={max_pages}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1280, "height": 1800})
            page = await context.new_page()

            visited_pages: List[str] = []
            records_by_pdf: Dict[str, Dict[str, str]] = {}
            current_url = start_url
            page_index = 1

            while current_url and page_index <= max_pages:
                visited_pages.append(current_url)
                step_action = f"open listing page {page_index} at {current_url} and inspect the products table"
                log(f"step {page_index} action: {step_action}")
                await page.goto(current_url, wait_until="networkidle")
                await page.screenshot(path=str(screenshots_dir / f"final_execution_{page_index}_page_{page_index}_table.png"), full_page=True)

                headers = [h.strip() for h in await page.locator("table thead th").all_inner_texts()]
                log(f"step {page_index} observed_headers: {headers}")

                rows = page.locator("table tbody tr")
                row_count = await rows.count()
                log(f"step {page_index} observed_row_count: {row_count}")

                for i in range(row_count):
                    row = rows.nth(i)
                    cells = row.locator("td")
                    cell_count = await cells.count()
                    if cell_count < 4:
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
                        log(f"step {page_index} extracted_record: product_name={json.dumps(name)} manufacturer={json.dumps(manufacturer)} pdf_url={pdf_url}")
                    else:
                        log(f"step {page_index} duplicate_pdf_skipped: pdf_url={pdf_url}")

                next_url = await _find_next_page_url(page)
                if next_url and next_url not in visited_pages:
                    log(f"step {page_index} pagination: next page detected -> {next_url}")
                    current_url = next_url
                    page_index += 1
                else:
                    log(f"step {page_index} pagination: no further pagination detected")
                    current_url = ""

            final_records = sorted(records_by_pdf.values(), key=lambda r: (r["manufacturer"], r["product_name"], r["pdf_url"]))
            total_count = len(final_records)
            result = {
                "start_url": start_url,
                "visited_pages": visited_pages,
                "records": final_records,
                "total_count": total_count,
            }

            log(f"step {page_index + 1} action: capture final results summary with {total_count} unique PDF records")
            html = _build_results_html(result)
            await page.set_content(html, wait_until="load")
            await page.screenshot(path=str(screenshots_dir / f"final_execution_{page_index + 1}_final_results.png"), full_page=True)
            final_response = json.dumps(result, indent=2, ensure_ascii=False)
            log("final_response:")
            log(final_response)
            (run_dir / "result.json").write_text(final_response + "\n", encoding="utf-8")

            await browser.close()
            return result

    return asyncio.run(_run())


async def _find_next_page_url(page) -> str | None:
    next_candidates = page.locator("a[rel='next'], a[aria-label*='Next' i], a:has-text('Next'), button:has-text('Next')")
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


def _build_results_html(result: Dict[str, object]) -> str:
    rows = "".join(
        f"<tr><td>{_html_escape(item['product_name'])}</td><td>{_html_escape(item['manufacturer'])}</td><td><a href='{_html_escape(item['pdf_url'])}'>{_html_escape(item['pdf_url'])}</a></td></tr>"
        for item in result["records"]
    )
    visited = "".join(f"<li>{_html_escape(url)}</li>" for url in result["visited_pages"])
    return f"""
    <html>
      <body style='font-family: Arial, sans-serif; padding: 24px;'>
        <h1>PDF Crawl Results</h1>
        <p>Start URL: {_html_escape(result['start_url'])}</p>
        <p>Total unique PDF count: {result['total_count']}</p>
        <h2>Visited pages</h2>
        <ul>{visited}</ul>
        <h2>Records</h2>
        <table border='1' cellspacing='0' cellpadding='6'>
          <thead><tr><th>Product name</th><th>Manufacturer</th><th>PDF URL</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </body>
    </html>
    """


def _html_escape(value: object) -> str:
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _create_run_dir() -> Path:
    FINAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    existing = []
    for child in FINAL_RUNS_DIR.iterdir():
        if child.is_dir() and re.fullmatch(r"run_(\d+)", child.name):
            existing.append(int(child.name.split("_")[1]))
    next_id = max(existing, default=0) + 1
    run_dir = FINAL_RUNS_DIR / f"run_{next_id:03d}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl the Intuned PDFs listing and collect unique PDF URLs.")
    parser.add_argument(
        "--start_url",
        type=str,
        default="https://sandbox.intuned.dev/pdfs",
        help="The PDFs listing page URL to crawl. Accepted format is an absolute HTTP or HTTPS URL. Default is https://sandbox.intuned.dev/pdfs.",
    )
    parser.add_argument(
        "--max_pages",
        type=int,
        default=25,
        help="Maximum number of listing pages to crawl as a safety bound when pagination is present. Accepted values are positive integers. Default is 25.",
    )
    args = parser.parse_args()
    output = crawl_pdf_listing(start_url=args.start_url, max_pages=args.max_pages)
    print(json.dumps(output, indent=2, ensure_ascii=False))
