import argparse
import asyncio
import html
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright


def scrape_techcrunch_startup_news(days_back: int = 7, category_url: str = "https://techcrunch.com/category/startups/", output_filename: str = "startup_news_last_7_days.json") -> dict[str, Any]:
    """Scrape recent TechCrunch startup news items from the Startups listing page.

    Args:
        days_back (int): Number of trailing days of startup news to include, measured
            backward from the run time in whole days. Must be a positive integer.
            Default is 7.
        category_url (str): TechCrunch listing URL that should contain startup news
            results. Expected format is a full HTTPS URL string, typically the
            TechCrunch Startups category page. Default is
            "https://techcrunch.com/category/startups/".
        output_filename (str): Filename for the structured JSON output saved inside
            the active run directory. Should be a JSON filename such as
            "startup_news_last_7_days.json". Default is
            "startup_news_last_7_days.json".

    Returns:
        dict[str, Any]: Summary data containing the run directory, output file path,
        cutoff timestamp, number of matching records, the scraped records, and a
        human-readable final response string.
    """
    return asyncio.run(_scrape_techcrunch_startup_news_async(days_back, category_url, output_filename))


async def _scrape_techcrunch_startup_news_async(days_back: int, category_url: str, output_filename: str) -> dict[str, Any]:
    workspace = Path(os.environ.get("WORKSPACE_DIR", Path.cwd()))
    final_runs = workspace / "final_runs"
    final_runs.mkdir(parents=True, exist_ok=True)

    existing = sorted([p for p in final_runs.glob("run_*") if p.is_dir()])
    next_id = max([int(p.name.split("_")[1]) for p in existing], default=0) + 1
    run_dir = final_runs / f"run_{next_id:03d}"
    screenshots_dir = run_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "final_script_log.txt"
    output_path = run_dir / output_filename
    script_copy = run_dir / "final_script.py"
    script_copy.write_text(Path(__file__).read_text(), encoding="utf-8")
    log_path.write_text("", encoding="utf-8")

    step = 0

    def log(message: str) -> None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(message + "\n")
        print(message)

    def parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    if days_back <= 0:
        raise ValueError("days_back must be a positive integer")

    now = datetime.now(timezone.utc).astimezone()
    cutoff = now - timedelta(days=days_back)
    log(f"step 0 params: days_back={days_back} category_url={category_url} output_filename={output_filename}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1800})
        page = await context.new_page()

        step += 1
        log(f"step {step} action: open the TechCrunch Startups category page at {category_url}")
        await page.goto(category_url, wait_until="domcontentloaded", timeout=90000)
        await page.screenshot(path=str(screenshots_dir / f"final_execution_{step}_open_startups_page.png"))

        step += 1
        log(f"step {step} action: capture visible startup news titles and timestamps on the listing page for verification")
        await page.screenshot(path=str(screenshots_dir / f"final_execution_{step}_visible_startup_results.png"))

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
        raw_items = await page.locator('main li').evaluate_all(js)
        log(f"step {step} observed: extracted {len(raw_items)} raw dated listing items from main li nodes")

        filtered = []
        for item in raw_items:
            dt = parse_dt(item.get("datetime"))
            if not dt:
                continue
            if dt >= cutoff:
                item["datetime_iso"] = dt.isoformat()
                filtered.append(item)

        filtered.sort(key=lambda x: x["datetime_iso"], reverse=True)

        step += 1
        log(f"step {step} action: filter extracted items to the last {days_back} days using cutoff {cutoff.isoformat()}")
        log(f"step {step} observed: {len(filtered)} items match the last-{days_back}-days requirement")

        payload = {
            "task": f"Scrape TechCrunch startup news from the last {days_back} days",
            "category_url": category_url,
            "days_back": days_back,
            "run_timestamp": now.isoformat(),
            "cutoff_timestamp": cutoff.isoformat(),
            "count": len(filtered),
            "items": filtered,
        }
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        step += 1
        log(f"step {step} action: save structured JSON output to {output_path.name}")

        final_response = f"Scraped {len(filtered)} TechCrunch startup news items from the last {days_back} days; saved results to {output_path}."
        log(f"final response: {final_response}")

        verification_html = f"""
        <!doctype html>
        <html><head><meta charset='utf-8'><title>Run Verification</title>
        <style>
        body {{ font-family: Arial, sans-serif; margin: 24px; }}
        h1, h2 {{ margin: 0 0 12px 0; }}
        pre {{ white-space: pre-wrap; word-break: break-word; background: #f4f4f4; padding: 12px; border: 1px solid #ccc; }}
        table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }}
        .meta {{ margin-bottom: 20px; }}
        </style></head><body>
        <h1>TechCrunch startup news scrape verification</h1>
        <div class='meta'>
          <p><strong>Run dir:</strong> {html.escape(str(run_dir))}</p>
          <p><strong>Output file:</strong> {html.escape(output_path.name)}</p>
          <p><strong>Count:</strong> {len(filtered)}</p>
          <p><strong>Cutoff timestamp:</strong> {html.escape(cutoff.isoformat())}</p>
          <p><strong>Final response:</strong> {html.escape(final_response)}</p>
        </div>
        <h2>Log file contents</h2>
        <pre>{html.escape(log_path.read_text(encoding='utf-8'))}</pre>
        <h2>Saved JSON preview</h2>
        <pre>{html.escape(json.dumps(payload, indent=2, ensure_ascii=False)[:9000])}</pre>
        <h2>Matching items preview</h2>
        <table><thead><tr><th>#</th><th>Title</th><th>Datetime</th><th>Author(s)</th><th>URL</th></tr></thead><tbody>
        {''.join(f"<tr><td>{i+1}</td><td>{html.escape(item['title'])}</td><td>{html.escape(item['datetime_iso'])}</td><td>{html.escape(', '.join(item['authors']))}</td><td>{html.escape(item['href'])}</td></tr>" for i, item in enumerate(filtered[:12]))}
        </tbody></table>
        </body></html>
        """
        verify_path = run_dir / "verification.html"
        verify_path.write_text(verification_html, encoding="utf-8")

        step += 1
        log(f"step {step} action: open a local verification page that displays the saved log contents and JSON output for evidence")
        await page.goto(verify_path.resolve().as_uri(), wait_until="domcontentloaded")
        await page.screenshot(path=str(screenshots_dir / f"final_execution_{step}_verification_log_and_output.png"))

        await browser.close()

    print(final_response)
    return {
        "run_dir": str(run_dir),
        "output_path": str(output_path),
        "count": len(filtered),
        "cutoff_timestamp": cutoff.isoformat(),
        "items": filtered,
        "final_response": final_response,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape recent TechCrunch startup news from the Startups category page.")
    parser.add_argument("--days_back", type=int, default=7, help="Number of trailing days of startup news to include, measured backward from the run time in whole days. Must be a positive integer. Default is 7.")
    parser.add_argument("--category_url", type=str, default="https://techcrunch.com/category/startups/", help="TechCrunch listing URL that should contain startup news results. Expected format is a full HTTPS URL string, typically the TechCrunch Startups category page. Default is https://techcrunch.com/category/startups/.")
    parser.add_argument("--output_filename", type=str, default="startup_news_last_7_days.json", help="Filename for the structured JSON output saved inside the active run directory. Should be a JSON filename such as startup_news_last_7_days.json. Default is startup_news_last_7_days.json.")
    args = parser.parse_args()
    result = scrape_techcrunch_startup_news(days_back=args.days_back, category_url=args.category_url, output_filename=args.output_filename)
    print(json.dumps(result, indent=2, ensure_ascii=False))
