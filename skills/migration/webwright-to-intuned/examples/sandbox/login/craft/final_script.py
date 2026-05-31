import argparse
import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright


WORKSPACE = Path(__file__).resolve().parent
START_URL = "https://sandbox.intuned.dev/list-auth"


def login_and_extract_list(email: str = "demo@email.com", password: str = "DemoUser2024!") -> list[dict[str, str]]:
    """Log into the Intuned sandbox and extract the authenticated list table.

    Args:
        email (str): Login email credential to enter on the Intuned sign-in form. Provide a valid email string accepted by the site. Default is `demo@email.com`.
        password (str): Login password credential to enter on the Intuned sign-in form. Provide the plaintext password string accepted by the site. Default is `DemoUser2024!`.

    Returns:
        list[dict[str, str]]: A structured list of every row currently shown in the authenticated table, with keys derived from the visible column headers.
    """
    return asyncio.run(_login_and_extract_list_async(email=email, password=password))


async def _login_and_extract_list_async(email: str, password: str) -> list[dict[str, str]]:
    run_dir = _prepare_run_dir()
    screenshots_dir = run_dir / "screenshots"
    log_path = run_dir / "final_script_log.txt"
    _reset_log(log_path)
    _log(log_path, f"step 0 params: email={email} password={password}")
    _log(log_path, f"step 1 action: navigate to protected URL {START_URL} and capture redirected login page")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 2200})
        page = await context.new_page()

        await page.goto(START_URL, wait_until="networkidle")
        await page.screenshot(path=str(screenshots_dir / "final_execution_1_redirected_login_page.png"), full_page=True)
        _log(log_path, f"step 1 evidence: url={page.url} title={(await page.title())}")

        _log(log_path, "step 2 action: fill email and password fields with provided credentials")
        await page.locator('input[type="email"]').fill(email)
        await page.locator('input[type="password"]').fill(password)
        await page.screenshot(path=str(screenshots_dir / "final_execution_2_credentials_filled.png"), full_page=True)

        _log(log_path, "step 3 action: submit the login form using the Sign in button")
        await page.get_by_role("button", name="Sign in").click()
        await page.wait_for_url("**/list-auth/", wait_until="networkidle")
        await page.screenshot(path=str(screenshots_dir / "final_execution_3_authenticated_list_page.png"), full_page=True)
        _log(log_path, f"step 3 evidence: authenticated_url={page.url} heading_visible={await page.get_by_role('heading', name='List (Authenticated)').is_visible()}")

        _log(log_path, "step 4 action: extract all rows from the authenticated table and capture results")
        table = page.locator("table")
        headers = [text.strip() for text in await table.locator("thead th").all_inner_texts()]
        rows = table.locator("tbody tr")
        extracted: list[dict[str, str]] = []
        for i in range(await rows.count()):
            values = [text.strip() for text in await rows.nth(i).locator("td").all_inner_texts()]
            row_obj = {headers[j]: values[j] if j < len(values) else "" for j in range(len(headers))}
            extracted.append(row_obj)
        await page.screenshot(path=str(screenshots_dir / "final_execution_4_table_results_visible.png"), full_page=True)
        _log(log_path, f"step 4 evidence: column_headers={json.dumps(headers, ensure_ascii=False)} row_count={len(extracted)}")

        _log(log_path, "step 5 action: write the extracted structured list to final_script_log.txt and render an on-page verification summary for screenshot evidence")
        extracted_json = json.dumps(extracted, ensure_ascii=False)
        _log(log_path, f"step 5 evidence: wrote extracted structured list to final_script_log.txt with {len(extracted)} rows")
        _log(log_path, f"final_response: {extracted_json}")
        summary = json.dumps({"row_count": len(extracted), "headers": headers, "items": extracted}, ensure_ascii=False, indent=2)
        await page.evaluate("""(summaryText) => {
            const existing = document.getElementById("extraction-verification");
            if (existing) existing.remove();
            const wrap = document.createElement("div");
            wrap.id = "extraction-verification";
            wrap.style.position = "fixed";
            wrap.style.right = "16px";
            wrap.style.bottom = "16px";
            wrap.style.width = "520px";
            wrap.style.maxHeight = "45vh";
            wrap.style.overflow = "auto";
            wrap.style.zIndex = "99999";
            wrap.style.background = "white";
            wrap.style.border = "3px solid #111827";
            wrap.style.boxShadow = "0 12px 30px rgba(0,0,0,0.35)";
            wrap.style.padding = "12px";
            const title = document.createElement("div");
            title.textContent = "Extraction verification summary (also written to final_script_log.txt)";
            title.style.fontWeight = "700";
            title.style.marginBottom = "8px";
            const pre = document.createElement("pre");
            pre.textContent = summaryText;
            pre.style.whiteSpace = "pre-wrap";
            pre.style.fontSize = "12px";
            pre.style.lineHeight = "1.35";
            wrap.appendChild(title);
            wrap.appendChild(pre);
            document.body.appendChild(wrap);
        }""", summary)
        await page.screenshot(path=str(screenshots_dir / "final_execution_5_extraction_summary_and_table.png"), full_page=True)

        await browser.close()

    shutil.copy2(Path(__file__), run_dir / "final_script.py")
    return extracted


def _prepare_run_dir() -> Path:
    final_runs = WORKSPACE / "final_runs"
    final_runs.mkdir(exist_ok=True)
    existing = []
    for path in final_runs.glob("run_*"):
        try:
            existing.append(int(path.name.split("_")[1]))
        except Exception:
            pass
    run_id = max(existing, default=0) + 1
    run_dir = final_runs / f"run_{run_id:03d}"
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "screenshots").mkdir(exist_ok=True)
    return run_dir


def _reset_log(log_path: Path) -> None:
    log_path.write_text("")


def _log(log_path: Path, message: str) -> None:
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(message + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log into the Intuned sandbox and extract the authenticated list.")
    parser.add_argument("--email", type=str, default="demo@email.com", help="Login email credential to enter on the Intuned sign-in form. Provide a valid email string accepted by the site. Default is `demo@email.com`.")
    parser.add_argument("--password", type=str, default="DemoUser2024!", help="Login password credential to enter on the Intuned sign-in form. Provide the plaintext password string accepted by the site. Default is `DemoUser2024!`.")
    args = parser.parse_args()
    result = login_and_extract_list(email=args.email, password=args.password)
    print(json.dumps(result, ensure_ascii=False, indent=2))
