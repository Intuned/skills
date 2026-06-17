---
name: platform-errors
description: "Understand and resolve Intuned platform errors — Execution Timeout, Result Too Big / Out of Memory, CAPTCHA Solving Timeout, and related codes. Covers how to identify each in logs and traces, which are code-fixable vs platform-level, and how to remediate. Load when diagnosing a platform error code or failure."
---

# Platform Errors

This skill covers errors related to Intuned's platform: the known error types, how to identify each in logs and traces, which are fixable in code versus platform-level (not fixable by code), and how to remediate.

---

## Execution Timeout

**Background**: Intuned API has a default execution timeout of 10 minutes. If an API takes more than 10 minutes without extending timeout, it will fail with this error.

Every API execution has a **10-minute timeout**. If your automation takes longer than 10 minutes, it will be terminated.

| Error Message                   | Meaning                       |
| ------------------------------- | ----------------------------- |
| "API Timeout"                   | Execution exceeded 10 minutes |
| "Execution Timed Out"           | Same as above                 |
| "execution exceeded time limit" | Same as above                 |

**Causes**: There could be many causes to this:

- Infinite loops: A code might be infinitely looping, which prevents the execution of `extend_timeout`.
- Downloading Large Files: Downloading files blocks the execution of the API until it is complete. Sometimes downloading all attachments without extending timeout between each download causes this error.
- Slow Playwright code: If the code makes sense and everything seems fine, sometimes Playwright autowaiting can take very long to extract large websites. Without having `extend_timeout` between every extracted row, this causes the error.

**Solutions**:

- Add `extend_timeout` where it fits.
- Use faster extraction methods, such as `page.evaluate()` since it doesn't require autowaiting.
- Check for infinite loops by adding logs.
- Use query_selector instead of locators.

**Identifying in trace**: Look for the last successful action before the trace abruptly ends. Check if there's a pattern of slow actions or repeated similar actions that might indicate a loop.

### Extending the timeout

Use `extend_timeout()` to reset the 10-minute timer. Each call gives you a fresh 10 minutes from that point.

**Import:**

```python
from intuned_runtime import extend_timeout
```

**Usage:**

```python
extend_timeout()  # Resets timer to 10 minutes
```

**Inside loops** — call after processing each item:

```python
for item in items:
    await process_item(item)
    extend_timeout()  # Reset after each item
```

**During pagination** — when processing multiple pages:

```python
for page_num in range(100):
    await process_page(page_num)
    extend_timeout()
```

**Before long operations** — before operations that might take time:

```python
extend_timeout()
await page.goto(slow_loading_url)
```

**Key points:**

1. **Default timeout is 10 minutes** - Cannot be changed
2. **extend_timeout() resets to 10 minutes** - It doesn't add time, it resets
3. **Call frequently** - Don't batch calls, call after each item in loops
4. **Multiple calls are safe** - Call as many times as needed
5. **No return value** - The function just resets the timer

---

## Result Too Big

**Background**: Intuned's platform accepts a maximum of 2 MB result size.

**Causes**: The returned object from the Automation API exceeds 2MB. It can have large strings, or too many values. This usually happens when there are large result fields like Markdown content or HTML Content.

**Solutions**:

- Reduce the size of the returned object by truncating long texts.
- Use better HTML or Markdown locators that are descrpitive. You should use reliable locators from the live website.
- Never remove the long field from the returned result, the returned object is required and meant to be extracted.

**Identifying in trace**: Check network responses and extracted data for unusually large payloads. Look for full HTML/markdown content being captured instead of parsed data.

---

## Ran out of memory

**Symptom**: failed attempts have `error.code = "script-process-crashed"` with a message like `Execution ran out of memory.` or `Process exited unexpectedly with code <N>`. All 3 retries failing identically with `script-process-crashed` is the canonical OOM signature — the worker was killed by the OS for exceeding its memory budget.

**First, rule out a code bug.** Most OOMs come from heavy websites, not the script — but check the API for:

- Recursion without a base case
- Unbounded accumulation in a loop (HTML, payloads, dedup indexes)
- Retained `page.content()` across many pages

If you find one, fix it directly — no spec change needed.

**Otherwise, two remediations:**

1. **Split the API with `extend_payload`** so each item runs in a fresh worker. Plan-independent and preferred when feasible — see how APIs chain to each other.
2. **Upgrade `replication.size`** in `Intuned.json`:

   | `replication.size` | RAM | vCPU |
   |---|---|---|
   | `standard` (default) | 2 GB | 6 shared |
   | `large` | 4 GB | 8 shared |
   | `x-large` | 8 GB | 1 performance |

   `large` and `x-large` are gated by the workspace plan:

   | Plan | Sizes available |
   |---|---|
   | `FREE` | `standard` only |
   | `DEVELOPER` | `standard`, `large`, `x-large` |
   | `STARTUP` | `standard`, `large`, `x-large` |

   Run `intunedctl auth whoami` to read the workspace's **Plan**. If the target size is available, surface the upgrade as one of the options the user can choose. If it's gated, surface both options: upgrade the plan to unlock the larger size, or stay on the current plan.

Both options are user-owned (size = billing, split = API contract). Don't apply either without asking. Same for memory-saving refactors that drop state or change return shape.

**Validation — e2e is required.** A local `intunedctl dev attempt api` runs outside the platform's memory cap and proves nothing about OOM. Always validate with the `test-intuned-project` skill (`intunedctl dev test-job`) at the original failing scale and parameters. A local run alone never qualifies as a passing fix.

**Identifying in trace**: OOM crashes often produce a truncated trace because the process was killed mid-write. Signals: all 3 attempts fail identically with `script-process-crashed`, the trace ends mid-aggregation/serialization, multiple pages/tabs open simultaneously without being closed.

---

## Captcha Solving Timeout

**Background**: Intuned Uses a CAPTCHA solver. It works by Deteching CAPTCHA challengers and then solving it automatically.
This extension can run into some errors

**Causes**: The main cause of this is that the browser is being detected as a BOT, or not having enough solve timeout.
Detected browsers can't solve CAPTCHAs and can have troubles even after solving them.

**Solutions**:

- Make sure Stealth Mode is enabled.
- Suggest increasing the timeout, 180 - 240 seconds is usually enough to solve a CAPTCHA challenger, taking more than this means that something is wrong. Suggest this if the captcha wasn't solved within the given timeout.
- Suggest increasing the settle period in the CAPTCHA helpers. This is a debounce delay: after the captcha queue appears empty (no more captchas in "solving" state), the code waits for this duration before doing a final confirmation check. This prevents false positives where a captcha briefly disappears from the solving queue but reappears shortly after (e.g. multi-step challenges or slow page transitions). The default is **5 seconds**. Increase it when the page takes longer than usual to settle after a captcha is submitted.
  - **Python**: `settle_period` (in seconds) — e.g. `wait_for_captcha_solve(page, settle_period=10.0)`
  - **TypeScript**: `settleDurationMs` (in milliseconds) — e.g. `waitForCaptchaSolve(page, { settleDurationMs: 10_000 })` or `withWaitForCaptchaSolve(cb, { page, settleDurationMs: 10_000 })`
- Suggest increasing `solveDelay` in Intuned.json settings for `captchaSolver` field. increasing Solve Delay mimics human interraction and improves the captcha solver's performance.
- Suggest increasing `maxRetries` if they were not enough. maxRetries determine Max solve attempts before failing
- Suggest using a proxy.

**Identifying in trace**:

- Look for when the "Verify" or "Submit" button is clicked for the CAPTCHA challenger, or any indicator of submitting the CAPTCHA. If things are good, it will be submitted and solved correctly. If the browser is detected as a bot, it will show "Solve Failed" or a similar failure message and keep retrying until the timeout is reached.
- **Verify the CAPTCHA was not solved via screenshots and page snapshot**: After the CAPTCHA helper returns, check the screenshots and page snapshot. If the CAPTCHA challenge is still visible (e.g. the checkbox, image grid, or challenge modal is still present on the page), the CAPTCHA was **not** solved. Do not rely solely on the helper returning without error.
- **Check subsequent actions**: Locators and selectors used after the CAPTCHA helper must target the **target page** (the page behind the CAPTCHA), not the CAPTCHA iframe or overlay. If those actions fail or the page is still showing the CAPTCHA challenge, it confirms the CAPTCHA was never resolved.

See the **bot-detection** skill for stealth-mode and detection remediation.

---

## CAPTCHA Helper Returns Immediately / Skips Waiting

**Background**: The CAPTCHA helper can silently return without waiting if it is called before the page has finished loading. This is a race condition, not an error — no exception is raised.

**Cause**: If the helper is called while the page is still loading, the CAPTCHA hasn't rendered yet so the helper sees an empty queue, settles immediately, and exits without waiting. The plain call pattern (`wait_for_captcha_solve(page)` / `waitForCaptchaSolve(page)`) does not wait for the page to finish loading before checking.

**Solutions**:

- **Preferred**: Pass the navigation/action as `func` to the wrapper pattern, which enables `wait_for_network_settled=True` by default:

  - **Python**:

  ```python
  @wait_for_captcha_solve(timeout_s=120.0, settle_period=15.0, wait_for_network_settled=True)
  async def navigate(page):
    await go_to_url(page,url)
  ```

  - **TypeScript**:

  ```typescript
  await withWaitForCaptchaSolve(
    async (page) => {
      await goToUrl({ page, url });
    },
    { page, timeoutInMs: 120_000 }
  );
  ```

- **Alternative**: Manually wait for the page to load before calling the plain helper:
  - **Python**: `await page.wait_for_load_state("networkidle")` then `await wait_for_captcha_solve(page, ...)`
  - **TypeScript**: `await page.waitForLoadState("networkidle")` then `await waitForCaptchaSolve(page, ...)`

**Identifying in trace**: The captcha helper completes almost instantly after the navigation with no captcha-related events in between. The subsequent code runs before the page has rendered the CAPTCHA challenge.

---

## Invalid CAPTCHA Type

**Background**: The CAPTCHA Solver supports a specific set of CAPTCHA types configured in Intuned settings (under `captchaSolver` in `Intuned.json`). If the encountered CAPTCHA is not among the supported/enabled types, the solver will not attempt to solve it — the CAPTCHA helper will return without the CAPTCHA ever being solved.

**Causes**: The page contains a CAPTCHA type that is either:

- Not supported by the Intuned CAPTCHA solver at all.
- Supported but not enabled in the project's Intuned settings.

**Identifying in trace**:

- **CAPTCHA never started solving**: If the trace shows the CAPTCHA helper was called but solving never started (no solver activity, no "solving" state in the queue), the CAPTCHA type is likely unsupported or disabled. This is different from a timeout — the solver simply never engaged.
- **Identify CAPTCHA type from network requests and DOM**: Look at the network requests and page DOM in the trace to identify the type, then check the matching settings key under `captchaSolver` in `Intuned.json`:
  - **reCAPTCHA** (`googleRecaptcha`) — requests/iframes to `google.com/recaptcha/` or `recaptcha.net/recaptcha/`
  - **FunCaptcha / Arkose** (`funcaptcha`) — requests to `funcaptcha.com` or `arkoselabs.com`
  - **Cloudflare Turnstile** (`cloudflare`) — iframe `src` contains `challenges.cloudflare.com` or `turnstile`
  - **Cloudflare Interstitial** (`cloudflare`) — full-page Cloudflare challenge before the target site loads
  - **AWS WAF CAPTCHA** (`awscaptcha`) — script `src` contains `awswaf`, or `<awswaf-captcha>` element in DOM
  - **GeeTest** (`geetest`) — DOM contains `.geetest_captcha` or `.geetest_btn_click`
  - **Lemin CAPTCHA** (`lemin`) — iframe `src` contains `lemincaptcha`, or `.lemin-captcha-container` in DOM
  - **Text CAPTCHA** (`text`) — visible text question paired with a text input
  - **Custom CAPTCHA** (`customCaptcha`) — image + input pair matched by custom selectors in settings

**Solutions**:

- Check the Intuned settings (`Intuned.json`) to confirm which CAPTCHA types are enabled under `captchaSolver`. Cross-reference the identified type with the settings keys listed above.
- If the required CAPTCHA type is supported but not enabled, add and enable it in the settings.
- If the CAPTCHA type is not supported, report it so support can be added to the platform.
