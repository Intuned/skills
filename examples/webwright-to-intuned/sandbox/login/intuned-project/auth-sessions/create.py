from typing import TypedDict

from intuned_browser import go_to_url
from playwright.async_api import Page


class Params(TypedDict):
    username: str
    password: str


async def create(page: Page, params: Params | None = None, **_kwargs):
    # Ported from the sandbox-login Crafted CLI (login portion). Uses the craft's
    # live-verified selectors, not the template's stale #email-input ids.
    if params is None:
        raise ValueError("Params with username and password are required")

    # Navigating to the protected page redirects to the login form.
    await go_to_url(page=page, url="https://sandbox.intuned.dev/list-auth")

    await page.locator('input[type="email"]').fill(params["username"])
    await page.locator('input[type="password"]').fill(params["password"])
    await page.get_by_role("button", name="Sign in").click()

    # Confirm we landed back on the authenticated list page. Intuned captures the
    # browser state (cookies) after create() returns.
    await page.get_by_role("heading", name="List (Authenticated)").wait_for(
        state="visible", timeout=15_000
    )
