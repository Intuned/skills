from intuned_browser import go_to_url
from playwright.async_api import Page


async def check(page: Page, **_kwargs) -> bool:
    # Open the protected list page. If the session is valid we stay on it; if not
    # the app redirects to /login. Derived from the craft's verified signals.
    await go_to_url(page=page, url="https://sandbox.intuned.dev/list-auth")

    if "/login" in page.url:
        return False

    return await page.get_by_role(
        "heading", name="List (Authenticated)"
    ).is_visible()
