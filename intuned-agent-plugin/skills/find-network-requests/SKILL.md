---
name: find-network-requests
user-invocable: false
description: "Identify and document the network request(s) an Intuned API depends on, using the on-disk traffic captures. Load when an API depends on a backend/XHR/fetch request rather than DOM scraping."
---

# Find Network Requests

Finding network requests is the capability of identifying the backend request(s) an API depends on and documenting them well enough to reproduce the call in code.

## Where the captures live

Captured traffic is on disk at `.intuned-agent/tab_{tab_id}/network/`:

- `requests.txt` — index of every captured request
- `request_bodies/{n}.body` — response body for request `n`
- `request_bodies/{n}.request` — request body for request `n` (POST/PUT/PATCH only)

## Trigger the request first if it's interaction-gated

If a request fires only after an interaction (pagination, search, submit), perform that interaction first so it gets captured, then inspect the relevant request(s).

## Document the request

Document the request so it can be reproduced in code:

- **method** and **URL / pattern**
- **headers**
- **query parameters and/or body**
- **pagination** (how the request advances through pages)
- **response mapping** — how fields in the response body map to the data you need

In Intuned code, requests are reproduced with `page.evaluate()` plus the browser's built-in `fetch()` — never an external HTTP library.
