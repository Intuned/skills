---
name: trace-debugging
description: "Debug an automation failure by reading its Playwright trace (.zip): extract it, pinpoint the failure, propose and verify a fix. Includes the Playwright trace file-format reference (.trace/.network/.stacks and resources/)."
---

# Debug Playwright Trace

Trace file to analyze: `$ARGUMENTS`

This is the capability of reading an Intuned automation run's Playwright trace (`.zip`) to find why the run failed: extract the trace, read its files, pinpoint the failure, propose a fix, and verify it on the live page. The first part below is the debugging workflow; the **Trace File Format Reference** at the end documents the `.trace` / `.network` / `.stacks` structure and the `resources/` layout.

## Setup

Unzip the trace file into a temp directory. Use this skill's bundled `scripts/unzip-trace.sh` — don't unzip it by hand. The path is relative to **this skill's own directory** (resolve it against the skill's base directory shown when the skill loads), run from the project root:

```bash
scripts/unzip-trace.sh <file-name.zip>
```

This gives you an unzipped trace directory containing `trace.trace`, `trace.network`, `trace.stacks`, and a `resources/` folder of screenshots, DOM snapshots, and response bodies.

## Context First

Before analyzing, understand the Intuned project this trace came from. Read the API implementation in `api/` for the API that produced this trace so you know what the code was trying to do — which selectors, navigations, and waits it expected. The trace tells you what actually happened; the code tells you what was supposed to happen. You need both to diagnose.

## Large File Handling

**Trace files can be massive.** A single trace can contain:

- `trace.trace`: 100,000+ lines for complex interactions
- `trace.network`: Thousands of HTTP transactions
- `resources/`: Hundreds of screenshots and response bodies, HTML files, CSS files, txt files. Only access them when you need them, and do it in small portions.

**Don't read entire trace files at once.** Always use:

- `head` to preview structure
- `grep` to find specific patterns
- `jq` with filters to extract relevant data
- Line-based reading for JSON Lines files

## Platform Error Detection Protocol

**Before starting any trace analysis, check for platform error indicators.** Platform-specific errors require different analysis than standard Playwright debugging, and this check must run **before** any other analysis.

1. **Scan for keywords in trace:**

   ```bash
   grep -i 'captcha\|timeout\|memory\|2mb\|result too big' .intuned-agent/trace-extract/trace.trace | head -5
   ```

2. **If ANY keywords found → consult the platform error reference IMMEDIATELY**

   - Load the `platform-errors` skill
   - Identify which error type matches the trace
   - Apply the platform-specific analysis from that skill

3. **If NO keywords found → proceed with the standard workflow below**

**DO NOT skip this check.** Platform errors include:

- **Execution Timeout** (10-min limit)
- **Result Too Big** (2 MB max)
- **Out of Memory** (2 GB RAM)
- **CAPTCHA Solving Timeout**

## How to Analyze

Work through the trace to answer, concretely: what was the run doing when it failed, what did the page actually look like at that moment, and what did the automation wait for that never appeared?

### Step 1: Get Overview (NEVER cat entire files)

**⚠️ REMINDER: If you haven't already, run the Platform Error Detection Protocol above FIRST.**

```bash
# Check file sizes first
wc -l .intuned-agent/trace-extract/trace.trace
wc -l .intuned-agent/trace-extract/trace.network

# Preview structure
head -5 .intuned-agent/trace-extract/trace.trace | jq '.'
head -5 .intuned-agent/trace-extract/trace.network | jq '.'
```

### Step 2: Find Errors

```bash
# Find all actions with errors
grep '"error"' .intuned-agent/trace-extract/trace.trace | jq '{callId, apiName, error: .error.message}'

# Find failed network requests (4xx/5xx)
grep '"status":4\|"status":5' .intuned-agent/trace-extract/trace.network | jq '{url: .snapshot.request.url, status: .snapshot.response.status}'
```

**Note on network status codes:** A non-2xx response does not automatically mean the automation failed. Many sites return misleading codes (e.g., 404 or 500 on XHR/API endpoints) while still serving valid data and rendering correctly. Cross-check any suspicious network response against the DOM snapshot or screenshot at the same point in the timeline before treating it as a cause.

### Step 3: Investigate Specific Action

Once you find a failing `callId`:

```bash
# Get all events for a specific callId
grep 'call@35' .intuned-agent/trace-extract/trace.trace | jq '.'

# Get the stack trace for this callId
jq '.stacks[] | select(.[0] == 35)' .intuned-agent/trace-extract/trace.stacks
```

### Step 4: Check Snapshots and Screenshots

> **Important:** Always look at **more than one screenshot** across different points in the timeline — do not rely on a single frame. Focus on the **right side of the timeline (the most recent events)** to understand what the final state was, then work backwards to understand what led to it. The last few screenshots often reveal the actual failure state (e.g., a blocked page, a CAPTCHA, a wrong element), while earlier ones show the sequence of actions that caused it.

```bash
# Find screenshot closest to failure time
grep 'screencast-frame' .intuned-agent/trace-extract/trace.trace | jq '{sha1, timestamp}' | head -20

# View the screenshot (use Read tool)
# Read .intuned-agent/trace-extract/resources/page@...-timestamp.jpeg
```

### Step 5: Trace Network Request to Response Body

```bash
# Find a specific request
grep 'api/endpoint' .intuned-agent/trace-extract/trace.network | jq '.snapshot.response.content'

# Get the SHA1 reference, then read the actual response
# Read .intuned-agent/trace-extract/resources/{sha1}.json
```

## Analysis Priority

**DOM and screenshots are the source of truth — they show what Playwright actually saw, and they always overrule the network log.** Network requests are secondary, useful only for bot detection, load timeouts, or missing critical resources. If the DOM shows the page rendered content (any UI, images, text, loading states), a non-2xx network code is not the failure cause; the failure is whatever the automation waited for that never appeared.

**Do not build conclusions on response codes alone.** A status code can be relevant but never automatically proves the page failed. Cross-check it against the trace evidence — DOM snapshots, screenshots, console output, follow-up requests, and whether the UI rendered the elements the automation expected. A page can return 404 and still render a React app, a breadcrumb, or a loading spinner, meaning navigation completed and the real failure is a selector, timing, or rendering issue. If you cite a status code in your diagnosis, explain why it is or isn't relevant based on that evidence.

## Common Failure Patterns

### Platform-Specific Errors — MANDATORY Reading Required

**⚠️ CRITICAL: When you detect ANY of these error patterns, you MUST IMMEDIATELY consult the platform error reference BEFORE analyzing further.**

**MANDATORY ACTION:** Load the **`platform-errors`** skill and match the trace to an error type.

**DO NOT proceed with analysis until you have done this.**

**Error Patterns That Trigger MANDATORY Reading:**

#### 1. CAPTCHA Solving Timeout

- Console logs mention "captcha", "recaptcha", or "solving"
- Error messages show "CAPTCHA Solve timed out", "Wrong captcha answer", "Verify you are human"
- `wait_for_captcha_solve` appears in stack traces

#### 2. Execution Timeout (10-min limit)

- Trace ends abruptly without clean error message
- Last action duration >8-9 minutes
- No explicit timeout error, just process termination

#### 3. Result Too Big (2 MB limit)

- Error message explicitly mentions "result too big" or "2MB limit"
- Large payload in final API response

#### 4. Out of Memory (2 GB RAM limit)

- Trace truncated or process killed without clean error
- Multiple pages/tabs open simultaneously

For full causes, solutions, and how each error appears in a trace, load the `platform-errors` skill.

---

### Timeout Errors (Standard Playwright)

**Symptoms:** `"Timeout 20000ms exceeded"`

```bash
grep 'Timeout' .intuned-agent/trace-extract/trace.trace | jq '{callId, apiName, error}'
grep 'call@<callId>' .intuned-agent/trace-extract/trace.trace | grep '"type":"log"' | jq '.message'
```

**Common causes:** Element not present, hidden, or disabled; slow network blocking page load.

### Element Not Found / Strict Mode Violation

**Symptoms:** `"Element not found"` or `"strict mode violation"`

```bash
grep 'call@<callId>' .intuned-agent/trace-extract/trace.trace | grep '"before"' | jq '.params'
grep 'snapshotName.*before@call@<callId>' .intuned-agent/trace-extract/trace.trace | jq '.snapshot.html' | head -100
```

### Network Failures

Network errors are useful signals for specific failure modes: bot detection (unexpected 403/CAPTCHA redirects), missing critical resources that block rendering, or load timeouts. For everything else, trust the DOM over the network log — a non-2xx status on a request does not mean Playwright failed to do its job.

```bash
grep '"status":' .intuned-agent/trace-extract/trace.network | grep -v '"status":2' | jq '{url: .snapshot.request.url, status: .snapshot.response.status}'
```

When you find a suspicious response, always verify against the DOM snapshot or screenshot at the same timestamp. **If the DOM shows the page rendered content — any UI, images, text, loading states — a non-2xx network code is not the root cause.** The root cause is what the automation waited for that never appeared. Do not let a network status override DOM evidence.

### Slow Performance

```bash
jq -s 'sort_by(.snapshot.time) | reverse | .[0:10] | .[] | {url: .snapshot.request.url, time: .snapshot.time}' .intuned-agent/trace-extract/trace.network
grep '"after"' .intuned-agent/trace-extract/trace.trace | jq -s 'map({callId, duration: (.endTime - .startTime // 0)}) | sort_by(.duration) | reverse | .[0:10]'
```

---

### Extra Techniques

1. **Headless Browser Detection**: Websites may fingerprint headless mode. If you see unexpected CAPTCHA or blocks, headless mode could be the cause.
2. **Proxy Impact**: Slow or flagged proxy IPs cause timeouts and failed navigations.
3. **User Agent & Network Fingerprinting**: Headers like `Accept-Language`, TLS fingerprint can trigger bot detection.

**Fixes to suggest:**

- Configure Stealth Mode — see the `bot-detection` skill for how to set it up.
- Run a headful browser — see the `project-settings` skill (`headful`) for how to enable it.
- Use `go_to_url` from intuned-browser (Python) or `goToUrl` from @intuned/browser (TypeScript)
- Add generous timeouts and proper network waits

**Important:** In your suggested-fix response, point the user to the `bot-detection` and `project-settings` skills so they know where to apply the stealth/headful changes.

## Propose and Verify a Fix

After gathering the trace evidence, use it to propose a concrete fix. **It is your responsibility to discover the DOM and build reliable selectors using your own tools** — do not rely on the trace's stale DOM snapshot for a new selector, since the live page may have changed.

Always verify your proposed fix on the live page: start a browser, navigate to the page, and test there before treating the fix as correct. For building reliable selectors, invoke the **`build-selectors`** skill rather than hand-writing them.

---

## Trace File Format Reference

Reference for the Playwright trace file format and how to inspect an unzipped trace directory. Work from an already-unzipped trace directory (produced by the Setup step above).

### Trace File Structure

A Playwright trace is a `.zip` file containing:

#### Root Files (JSON Data)

All root files are text files containing JSON data:

| File            | Format      | Purpose                                      |
| --------------- | ----------- | -------------------------------------------- |
| `trace.trace`   | JSON Lines  | Main trace data - actions, events, snapshots |
| `trace.network` | JSON Lines  | Network requests/responses (HAR format)      |
| `trace.stacks`  | Single JSON | Stack trace information                      |

#### `resources/` Directory

Binary and text assets captured during execution:

| Pattern                          | Content                       |
| -------------------------------- | ----------------------------- |
| `{sha1}.html`                    | HTTP response bodies (HTML)   |
| `{sha1}.css`                     | HTTP response bodies (CSS)    |
| `{sha1}.jpeg/png`                | HTTP response bodies (images) |
| `page@{pageId}-{timestamp}.jpeg` | Browser screenshots           |
| `src@{sha1}.txt`                 | Source code snapshots         |

---

### File Format Details

#### 1. `trace.trace` (Main Trace Data)

**Format**: JSON Lines (one JSON object per line)

Each line has a `type` field that categorizes the event:

##### Event Types

**`context-options`** - Browser configuration at startup

```json
{
  "type": "context-options",
  "browserName": "chromium",
  "platform": "linux",
  "wallTime": 1769418759548
}
```

**`before`** - Action started

```json
{
  "type": "before",
  "callId": "call@35",
  "startTime": 36167.701,
  "apiName": "Locator.click",
  "params": { "selector": "button#submit" },
  "pageId": "page@abc123",
  "beforeSnapshot": "before@call@35"
}
```

- `callId`: Unique identifier - links to `after`, `log`, and `trace.stacks`
- `apiName`: Playwright method called (e.g., `Page.goto`, `Locator.click`, `Locator.fill`)
- `params`: Parameters passed to the method
- `beforeSnapshot`: Reference to DOM snapshot before action

**`after`** - Action completed

```json
{
  "type": "after",
  "callId": "call@35",
  "endTime": 56169.834,
  "error": { "message": "Timeout 20000ms exceeded.", "stack": "..." },
  "afterSnapshot": "after@call@35"
}
```

- `error`: Present if action failed - contains `message`, `stack`, `name`
- `result`: Return value if successful

**`log`** - Internal Playwright logs

```json
{
  "type": "log",
  "callId": "call@35",
  "time": 36175.596,
  "message": "waiting for element to be visible, enabled and stable"
}
```

**`frame-snapshot`** - DOM state capture

```json
{
  "type": "frame-snapshot",
  "snapshot": {
    "callId": "call@35",
    "snapshotName": "before@call@35",
    "frameUrl": "https://example.com",
    "html": [...],
    "viewport": {"width": 1280, "height": 800}
  }
}
```

**`input`** - User input action coordinates

```json
{
  "type": "input",
  "callId": "call@35",
  "point": { "x": 304.8, "y": 657.68 },
  "inputSnapshot": "input@call@35"
}
```

**`screencast-frame`** - Screenshot reference

```json
{
  "type": "screencast-frame",
  "pageId": "page@abc123",
  "sha1": "page@abc123-1769418762.730672.jpeg",
  "width": 1280,
  "height": 661,
  "timestamp": 34614.557
}
```

- `sha1`: Points to file in `resources/`

**`console`** - Browser console output

```json
{
  "type": "console",
  "messageType": "error",
  "text": "Failed to load resource: 404",
  "time": 34618.375
}
```

---

#### 2. `trace.network` (Network Data)

**Format**: JSON Lines (one HTTP transaction per line, HAR format)

Each line is a complete HTTP transaction:

```json
{
  "type": "resource-snapshot",
  "snapshot": {
    "_frameref": "frame@abc123",
    "_monotonicTime": 33959.321,
    "startedDateTime": "2026-01-26T09:12:42.086Z",
    "time": 382.452,
    "request": {
      "method": "GET",
      "url": "https://example.com/api/data",
      "headers": [{ "name": "Accept", "value": "application/json" }],
      "queryString": [{ "name": "page", "value": "1" }]
    },
    "response": {
      "status": 200,
      "statusText": "OK",
      "headers": [{ "name": "Content-Type", "value": "application/json" }],
      "content": {
        "size": 38293,
        "mimeType": "application/json",
        "_sha1": "0c171aa9f50a285380c7c39bc68398ec212e239c.json"
      }
    },
    "timings": {
      "dns": 162.054,
      "connect": 60.407,
      "ssl": 33.007,
      "send": 0,
      "wait": 93.348,
      "receive": 33.636
    }
  }
}
```

**Key Fields:**

- `response.content._sha1`: Reference to actual response body in `resources/`
- `timings`: Breakdown of where time was spent (dns, connect, ssl, wait, receive)
- `-1` in timings means connection was reused

**Cache Detection:**

```json
"bodySize": -337,      // Negative = cached
"_transferSize": 0,    // No bytes transferred
"timings": {"wait": -1, "receive": 1.161}
```

---

#### 3. `trace.stacks` (Stack Traces)

**Format**: Single JSON object (NOT JSON Lines)

```json
{
  "files": ["/app/api/default.py", "/lib/playwright/locator.py"],
  "stacks": [
    [
      35,
      [
        [0, 244, 0, "automation"],
        [1, 182, 0, "click"]
      ]
    ]
  ]
}
```

**Structure:**

- `files`: Array of file paths (lookup table)
- `stacks`: Array of `[callId, [frames...]]`
- Each frame: `[fileIndex, lineNumber, columnNumber, functionName]`

**Reconstructing a stack trace:**

```
callId 35 → stacks[0]
Frame [0, 244, 0, "automation"] → files[0]:244 in automation()
Result: File "/app/api/default.py", line 244, in automation
```

---

#### 4. `resources/` Directory

**HTTP Response Bodies** - Named by SHA1 hash

```
resources/0c171aa9f50a285380c7c39bc68398ec212e239c.html
resources/2d16dd6171fd75a22a1ccad8ca27ab9ca73359f1.json
```

Referenced by `response.content._sha1` in `trace.network`

**Screenshots** - Named by page ID and timestamp

```
resources/page@727e3474116be118ee870cc181fe66bc-1769418762.730672.jpeg
```

Referenced by `sha1` in `screencast-frame` events in `trace.trace`

**Source Code** - Named with `src@` prefix

```
resources/src@03ffa5c2e624466686d8fb09128ed79e14dc3404.txt
```

Contains source code files for stack trace context

---

### Cross-Reference Guide

#### Finding Response Body for a Network Request

```bash
grep 'example.com/api' .intuned-agent/trace-extract/trace.network | jq '.snapshot.response.content._sha1'
# Then read: resources/{sha1}
```

#### Finding Screenshot for an Action

```bash
grep 'call@35' .intuned-agent/trace-extract/trace.trace | grep '"before"' | jq '.startTime'
grep 'screencast-frame' .intuned-agent/trace-extract/trace.trace | jq '{sha1, timestamp}' | grep -A1 -B1 '<similar-timestamp>'
# View: resources/{sha1}.jpeg
```

#### Finding Source Code for a Stack Frame

```bash
jq '.stacks[] | select(.[0] == 35)' .intuned-agent/trace-extract/trace.stacks
jq '.files[0]' .intuned-agent/trace-extract/trace.stacks
# Source code in: resources/src@{sha1}.txt
```

---

### Quick Reference Commands

```bash
# Check file sizes (ALWAYS do this first)
wc -l .intuned-agent/trace-extract/trace.trace .intuned-agent/trace-extract/trace.network

# Preview main trace
head -10 .intuned-agent/trace-extract/trace.trace | jq '.'

# Find all errors
grep '"error"' .intuned-agent/trace-extract/trace.trace | jq '{callId, apiName, error: .error.message}'

# List all actions with their status
grep '"after"' .intuned-agent/trace-extract/trace.trace | jq '{callId, hasError: (.error != null)}'

# Find specific action type
grep '"apiName":"Locator.click"' .intuned-agent/trace-extract/trace.trace | jq '.'

# Find failed network requests
grep '"status":4\|"status":5' .intuned-agent/trace-extract/trace.network | jq '{url: .snapshot.request.url, status: .snapshot.response.status}'

# List screenshots
ls .intuned-agent/trace-extract/resources/*.jpeg | head -20

# Count resources by type
ls .intuned-agent/trace-extract/resources/ | sed 's/.*\.//' | sort | uniq -c
```

---

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
