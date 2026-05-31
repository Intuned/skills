# Ported from the sandbox-login Crafted CLI (post-login extraction portion).
# The AuthSession is already applied when this runs, so there is no login here.
from typing import Any, TypedDict

from intuned_browser import go_to_url
from playwright.async_api import Page


class Params(TypedDict, total=False):
    pass


async def automation(page: Page, params: Params | None = None, **_kwargs) -> dict[str, Any]:
    # Session already applied — open the protected list and extract every row.
    await go_to_url(page=page, url="https://sandbox.intuned.dev/list-auth")

    table = page.locator("table")
    headers = [t.strip() for t in await table.locator("thead th").all_inner_texts()]
    rows = table.locator("tbody tr")

    extracted: list[dict[str, str]] = []
    for i in range(await rows.count()):
        values = [t.strip() for t in await rows.nth(i).locator("td").all_inner_texts()]
        extracted.append(
            {headers[j]: (values[j] if j < len(values) else "") for j in range(len(headers))}
        )

    print(f"extracted {len(extracted)} rows; headers={headers}")
    return {"row_count": len(extracted), "headers": headers, "items": extracted}
