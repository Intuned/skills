---
name: bot-detection
description: "Get past bot-detection blocks, IP restrictions, and CAPTCHAs: detect the block, pick the right lever (proxy / stealth mode / CAPTCHA solver), configure stealth and the CAPTCHA solver in Intuned.json, and wire the CAPTCHA wait helpers into automation code. Load whenever a page is blocked, shows a CAPTCHA, or returns bot-detection signals."
---

# Handling Bot Detection and CAPTCHAs

When a page is blocked, shows a CAPTCHA, or returns bot-detection signals, this is the capability for getting past it. Intuned has four anti-bot levers: headful browser, a user-supplied **Proxy**, **Stealth Mode**, and the **CAPTCHA Solver**.

## What works where

| Lever               | What it fixes                              | Local dev                                  | Deployed platform run   |
| ------------------- | ------------------------------------------ | ------------------------------------------ | ----------------------- |
| Headful Mode        | Headless-browser detection                 | **Yes**: run headful (default is headless) | Yes (`headful: true`)   |
| User-supplied Proxy | IP / geo blocks, rate limiting             | **Yes** — set it and verify locally        | Yes (with `--deployed`) |
| Stealth Mode        | Browser-fingerprint / automation detection | Configure now, **runs only when deployed** | Yes                     |
| CAPTCHA Solver      | CAPTCHA / browser-check challenges         | Configure now, **runs only when deployed** | Yes                     |

**The headful mode and proxy are the only levers you can exercise and verify in local dev.** Stealth mode and the CAPTCHA solver are platform features: you **can and should** enable and configure them, write their config into `Intuned.json` now so they take effect the moment the project is deployed. You simply can't _run or validate_ them in local dev; to confirm they actually help, deploy the project (`intunedctl dev deploy`) and run it on the platform (deployed run / `intunedctl dev test-job`).

## Detecting a block

Treat any of these as a bot-detection signal:

- Blocked page or "Access Denied"
- CAPTCHA challenge
- Cloudflare / browser-check challenge
- 403 / 429 HTTP error
- Page appears broken or empty when it should have content
- Login redirected unexpectedly
- Any bot detection refusal

## Decision order

1. **Identify the block type.** Is it an IP/geo block (403/429, "Access Denied", unreachable) or an explicit CAPTCHA / browser-check / fingerprint challenge?

2. **If it could be headless detection and you're running headless: restart headful and retry first.** Many sites only block or mis-render for headless browsers, and headful is the cheapest lever you can verify locally. Restart with `intunedctl dev browser start` (omit `--headless`) and retry the same page before the deploy-only levers.

3. **If a proxy could fix it** (IP block, geo-restriction, rate limiting): use a **user-supplied** proxy if the user has one (it works locally, so you can verify it), or suggest Intuned's **auto proxy** if they don't (platform-provided, deployed only). **See the `proxy` skill** for which to use and the exact commands. If a user-supplied proxy restores access locally, you're done.

4. **If only stealth mode or the CAPTCHA solver would fix it** (browser fingerprint detection, or a CAPTCHA that no proxy resolves):

   - You **cannot** unblock this in local dev. Do not attempt to solve the CAPTCHA yourself, and do not click inside the CAPTCHA widget.
   - **Configure the right feature in `Intuned.json` now** so it takes effect once deployed (details below).
   - Tell the user clearly: this site needs stealth / CAPTCHA solving, which only run on the platform. They must **deploy** (`intunedctl dev deploy`) and validate via a **deployed run** or `intunedctl dev test-job` — it can't be confirmed with local `dev attempt` / `dev run`.

5. **Do NOT fall back to WebSearch** to scrape content — the browser (local or deployed) is the only valid access path. If you can't proceed locally, write the config, explain the deploy-and-test path, and stop. Don't silently skip live exploration and write code blind.

A proxy and stealth mode combine well: when a site both IP-blocks and fingerprints, apply the proxy (via the `proxy` skill) and configure stealth together.

## Stealth Mode

Stealth mode is a specialized browser configuration that patches automation-framework leaks and improves browser fingerprint spoofing so sites don't detect the browser as automated. It runs on a Chromium-based stealth browser that exists only on the Intuned platform, which is why it can't run in local dev. Configure it as soon as you see fingerprint-style detection, and it engages once deployed.

Enable it by using the CLI command:

```bash
intunedctl dev stealth enable
```

The `intunedctl dev stealth` command writes the config in Intuned settings for you.

**Requirements & limitations:**

- Requires **Playwright v1.55+**
- Works best with headful mode enabled
- No additional cost on Intuned platform plans

If a deployed run with stealth still hits CAPTCHA challenges, configure the CAPTCHA solver below.

## CAPTCHA Solver

The CAPTCHA solver is an Intuned platform feature that automatically detects and resolves CAPTCHA challenges without manual intervention, allowing automations to complete end-to-end unattended. It is a special platform feature with no local-browser equivalent, so it only runs on deployed platform runs. Configure it when stealth mode alone isn't enough to clear CAPTCHAs.

### Enable it in `Intuned.json`

```bash
intunedctl dev captcha-solve enable
```

The solver requires, mandatorily:

- `headful: true`
- `stealthMode.enabled: true`

The `intunedctl dev captcha-solve` command writes this config for you (`headful: true` + `stealthMode.enabled: true` + a `captchaSolver` block):

```json
{
  "headful": true,
  "stealthMode": { "enabled": true },
  "captchaSolver": {
    "enabled": true,
    "settings": {
      "autoSolve": true,
      "solveDelay": 2000,
      "maxRetries": 3,
      "timeout": 30000
    }
  }
}
```

| Setting      | Default    | Purpose                                    |
| ------------ | ---------- | ------------------------------------------ |
| `autoSolve`  | `true`     | Automatically solve detected CAPTCHAs      |
| `solveDelay` | `2000` ms  | Delay before solving (mimics human timing) |
| `maxRetries` | `3`        | Max solve attempts before failing          |
| `timeout`    | `30000` ms | Max wait time for resolution               |

Increase `timeout` and `maxRetries` for complex CAPTCHAs. This config only takes effect on a **deployed** platform run — there is no local solver to renavigate against. Validate it via a deployed run / `intunedctl dev test-job`.

### Wire the wait helpers into automation code

The CAPTCHA solver runs asynchronously in the background. Without helpers, your code can race past a CAPTCHA before it is solved, breaking the automation. **Always use a wait helper to pause execution and wait for resolution** after any navigation or action that can trigger a CAPTCHA. The helper calls belong in your code now even though the solver only runs on deployed/platform runs.

#### Python — `from intuned_runtime.captcha import ...`

`wait_for_captcha_solve(page, timeout_s, settle_period)` blocks until all CAPTCHAs on the page are solved:

```python
from intuned_runtime.captcha import wait_for_captcha_solve
from intuned_browser import go_to_url
await go_to_url(page,url="https://example.com/login")
# CAPTCHA may appear after navigation — always wait before proceeding
await wait_for_captcha_solve(page, timeout_s=120.0, settle_period=10.0)
await page.click("#submit")
```

**Wrapper pattern** — execute an action then wait. Use when the CAPTCHA is triggered by clicking a button (login, submit, navigate):

```python
@wait_for_captcha_solve(timeout_s=120.0, settle_period=10.0, wait_for_network_settled=True)
async def navigate(page):
  await go_to_url(page,url)
```

#### TypeScript — `from @intuned/runtime`

`waitForCaptchaSolve(page, options)` blocks until all CAPTCHAs on the page are solved:

```typescript
import { waitForCaptchaSolve } from "@intuned/runtime";

await page.goto("https://example.com/login");
// Always wait — CAPTCHA may not appear instantly after navigation
await waitForCaptchaSolve(page, {
  timeoutInMs: 120000,
  settleDurationMs: 5000,
});
await page.click("#submit");
```

`withWaitForCaptchaSolve(callback, options)` executes an action then waits for resolution. Preferred when the CAPTCHA is triggered by an action:

```typescript
import { withWaitForCaptchaSolve } from "@intuned/runtime";

await withWaitForCaptchaSolve(
  async (page) => {
    await page.click("#submit-button");
  },
  {
    page,
    timeoutInMs: 120000,
    settleDurationMs: 5000,
    waitForNetworkSettled: true,
  }
);
```

### Rules for generated code

Follow these in every automation that touches a CAPTCHA-protected page:

1. **Always call a wait helper after any navigation or action that can trigger a CAPTCHA.** Never assume the page is immediately ready.
2. **Use the wrapper pattern when the CAPTCHA is triggered by an action** (form submit, login click, or `page.goto`). Use the plain helper only when the page is already fully loaded.
3. **Set `timeout_s` / `timeoutInMs` to at least 60 seconds.** Complex CAPTCHAs take time; a low timeout causes false failures.
4. **Set `settle_period` / `settleDurationMs` to at least 5 seconds.** This prevents the helper from returning before the CAPTCHA has fully appeared.
5. **Never proceed to the next step before the wait resolves.** Interacting with the page while a CAPTCHA is active will fail.
6. **Enable the correct CAPTCHA type in `Intuned.json` under `captchaSolver`.** The helpers wait for solver completion — if the solver isn't configured for the CAPTCHA type on the page, the helpers will time out.
