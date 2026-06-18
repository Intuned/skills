# Auth Session API Reference (TypeScript)

## File Location

Auth session API files go in the **project root**, not in `api/`:

- `auth-sessions/create.ts` — login flow
- `auth-sessions/check.ts` — session validation

**Never** place them at `api/auth-sessions/create.ts` — auth session commands only look in the project root.

## The Create API (`auth-sessions/create.ts`)

### Function Signature

```typescript
import { BrowserContext, Page } from "playwright";
import { goToUrl } from "@intuned/browser";

export interface Params {
  username: string;
  password: string;
}

export default async function create(
  params: Params,
  page: Page,
  context: BrowserContext,
): Promise<void>;
```

### Best Practices

1. **Parameterize all credentials** — Every login field (username, password, API key, OTP secret) must be a typed parameter. Never hardcode credentials.
2. **Use `goToUrl`** for navigation — Not `page.goto()`.
3. **Use reliable selectors** — Build selectors using `build_reliable_selector` from the browser tools. Don't write selectors by guessing from HTML.
4. **Verify login succeeded** — After submitting, wait for a confirmation element that only appears when logged in (e.g., a user menu, dashboard heading, profile icon). Use `waitFor` with a timeout.
5. **Handle multi-step flows** — Some logins have multiple pages (username → password). Handle each step with proper waits.

### Example

```typescript
import { BrowserContext, Page } from "playwright";
import { goToUrl } from "@intuned/browser";

export interface Params {
  username: string;
  password: string;
}

export default async function create(
  params: Params,
  page: Page,
  context: BrowserContext,
): Promise<void> {
  await goToUrl({ page, url: "https://example.com/login" });

  // Fill login form using reliable selectors
  await page.locator("#email-input").fill(params.username);
  await page.locator("#password-input").fill(params.password);
  await page.locator("#submit-button").click();

  // Verify login succeeded — wait for element only visible when logged in
  await page
    .locator("#dashboard-title")
    .waitFor({ state: "visible", timeout: 10_000 });
}
```

### Handling 2FA (TOTP)

Build a `TOTP` from the secret and call `.generate()`, it returns the current 6-digit code. The defaults (SHA1, 6 digits, 30s period) match what most services use. Generate the code **inside** `create` so it's fresh every run, and add the secret to `Params`:

````typescript
import { BrowserContext, Page } from "playwright";
import { goToUrl } from "@intuned/browser";
import * as OTPAuth from "otpauth";

export interface Params {
  username: string;
  password: string;
  otpSecret: string; // TOTP secret (base32)
}

export default async function create(
  params: Params,
  page: Page,
  context: BrowserContext
): Promise<void> {
  await goToUrl({ page, url: "https://example.com/login" });

  await page.locator("#email-input").fill(params.username);
  await page.locator("#password-input").fill(params.password);
  await page.locator("#submit-button").click();

  // 2FA step — generate a fresh code right before filling it
  const otpInput = page.locator("#otp-input"); // use a reliable selector
  await otpInput.waitFor({ state: "visible", timeout: 10_000 });
  const totp = new OTPAuth.TOTP({ secret: params.otpSecret });
  const code = totp.generate();
  await otpInput.fill(code);
  await page.locator("#verify-button").click();

  // Verify login succeeded
  await page
    .locator("#dashboard-title")
    .waitFor({ state: "visible", timeout: 10_000 });
}


## The Check API (`auth-sessions/check.ts`)

### Function Signature

```typescript
import { BrowserContext, Page } from "playwright";
import { goToUrl } from "@intuned/browser";

export default async function check(
  page: Page,
  context: BrowserContext,
): Promise<boolean>;
````

Note: `check` does **not** receive a `params` argument — only `page` and `context`.

### Best Practices

1. **Navigate to a protected page** — Pick a page that redirects to login when not authenticated.
2. **Check for a logged-in-only element** — Look for something like a user menu, profile icon, or dashboard content. Don't just check for absence of a login form.
3. **Return a boolean** — `true` if valid, `false` if not. Don't throw exceptions for invalid sessions.
4. **Keep it fast** — The check runs before every API call in production. Target lightweight pages and avoid heavy loads.

### Example

```typescript
import { BrowserContext, Page } from "playwright";
import { goToUrl } from "@intuned/browser";

export default async function check(
  page: Page,
  context: BrowserContext,
): Promise<boolean> {
  await goToUrl({ page, url: "https://example.com/dashboard" });

  // Check if user menu is visible (only shows when logged in)
  const isValid = await page.locator("#user-menu-toggle").isVisible();

  return isValid;
}
```
