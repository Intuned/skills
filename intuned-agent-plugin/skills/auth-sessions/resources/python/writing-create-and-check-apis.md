# Auth Session API Reference (Python)

## File Location

Auth session API files go in the **project root**, not in `api/`:

- `auth-sessions/create.py` — login flow
- `auth-sessions/check.py` — session validation

**Never** place them at `api/auth-sessions/create.py` — auth session commands only look in the project root.

## The Create API (`auth-sessions/create.py`)

### Function Signature

```python
from typing import TypedDict
from playwright.async_api import Page
from intuned_browser import go_to_url

class Params(TypedDict):  # Fields depend on the login form
    username: str
    password: str

async def create(page: Page, params: Params | None = None, **_kwargs):
```

### Best Practices

1. **Parameterize all credentials** — Every login field (username, password, API key, OTP secret) must be a typed parameter. Never hardcode credentials.
2. **Use `go_to_url`** for navigation — Not `page.goto()`.
3. **Use reliable selectors** — Build selectors using `build_reliable_selector` from the browser tools. Don't write selectors by guessing from HTML.
4. **Verify login succeeded** — After submitting, wait for a confirmation element that only appears when logged in (e.g., a user menu, dashboard heading, profile icon). Use `wait_for` with a timeout.
5. **Handle multi-step flows** — Some logins have multiple pages (username → password). Handle each step with proper waits.

### Example

```python
from typing import TypedDict
from intuned_browser import go_to_url
from playwright.async_api import Page

class Params(TypedDict):
    username: str
    password: str

async def create(page: Page, params: Params | None = None, **_kwargs):
    if params is None:
        raise ValueError("Params with username and password are required")

    await go_to_url(page=page, url="https://example.com/login")

    # Fill login form using reliable selectors
    email_input = page.locator("#email-input")
    await email_input.fill(params["username"])

    password_input = page.locator("#password-input")
    await password_input.fill(params["password"])

    submit_button = page.locator("#submit-button")
    await submit_button.click()

    # Verify login succeeded — wait for element only visible when logged in
    dashboard_heading = page.locator("#dashboard-title")
    await dashboard_heading.wait_for(state="visible", timeout=10_000)
```

### Handling 2FA (TOTP)

If the login asks for a 2FA / OTP / TOTP code, you need the TOTP **secret** stored as a credential (see `/intuned-agent-plugin/skills/auth-sessions/resources/handling-2fa.md` for the overall flow, how to collect it, and installing `pyotp`).

`pyotp.TOTP(secret).now()` returns the current 6-digit TOTP. Generate the code **inside** `create` so it's fresh every run, and add the secret to `Params`:

```python
from typing import TypedDict
import pyotp
from intuned_browser import go_to_url
from playwright.async_api import Page

class Params(TypedDict):
    username: str
    password: str
    otpSecret: str  # TOTP secret (base32)

async def create(page: Page, params: Params | None = None, **_kwargs):
    if params is None:
        raise ValueError("Params with username, password and otpSecret are required")

    await go_to_url(page=page, url="https://example.com/login")

    await page.locator("#email-input").fill(params["username"])
    await page.locator("#password-input").fill(params["password"])
    await page.locator("#submit-button").click()

    # 2FA step — generate a fresh code right before filling it
    otp_input = page.locator("#otp-input")  # use a reliable selector
    await otp_input.wait_for(state="visible", timeout=10_000)
    code = pyotp.TOTP(params["otpSecret"]).now()
    await otp_input.fill(code)
    await page.locator("#verify-button").click()

    # Verify login succeeded
    await page.locator("#dashboard-title").wait_for(state="visible", timeout=10_000)
```

## The Check API (`auth-sessions/check.py`)

### Function Signature

```python
from playwright.async_api import Page
from intuned_browser import go_to_url

async def check(page: Page, **_kwargs) -> bool:
```

### Best Practices

1. **Navigate to a protected page** — Pick a page that redirects to login when not authenticated.
2. **Check for a logged-in-only element** — Look for something like a user menu, profile icon, or dashboard content. Don't just check for absence of a login form.
3. **Return a boolean** — `True` if valid, `False` if not. Don't raise exceptions for invalid sessions.
4. **Keep it fast** — The check runs before every API call in production. Target lightweight pages and avoid heavy loads.

### Example

```python
from intuned_browser import go_to_url
from playwright.async_api import Page

async def check(page: Page, **_kwargs) -> bool:
    await go_to_url(page=page, url="https://example.com/dashboard")

    # Check if user menu is visible (only shows when logged in)
    user_menu = page.locator("#user-menu-toggle")
    is_valid = await user_menu.is_visible()

    return is_valid
```
