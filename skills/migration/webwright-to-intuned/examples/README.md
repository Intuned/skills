# Examples

Four end-to-end demonstrations of the `webwright-to-intuned` skill — **two on
Intuned's public sandbox** (always reproducible) and **two on real third-party
sites** (representative of production work).

Each example folder contains:

```
<example>/
├── craft/                 # INPUT: the Webwright Crafted CLI (what you convert)
│   ├── final_script.py    #   the parameterized logic
│   ├── plan.md            #   the # Parameters table (authoritative param spec)
│   ├── task.json          #   task text + start_url
│   └── final_runs/run_*/  #   one known-good output (for the Fork-A comparison)
└── intuned-project/       # REFERENCE: what a correct conversion looks like
    ├── api/<name>.py       #   the ported automation
    ├── .parameters/...     #   defaults that reproduce the task
    └── Intuned.jsonc       #   manifest (workspaceId is a placeholder)
```

Run the skill against `craft/` and compare your output to `intuned-project/`:

```
/intuned-port examples/<group>/<name>/craft
```

| # | Example | Group | Demonstrates |
|---|---|---|---|
| 1 | [`sandbox/pdf-crawl`](./sandbox/pdf-crawl) | sandbox | Faithful crawl → flat list (no fan-out) |
| 2 | [`sandbox/login`](./sandbox/login) | sandbox | **AuthSessions** exception (login → create/check) |
| 3 | [`real/techcrunch-startup-news`](./real/techcrunch-startup-news) | real site | Faithful scrape + date-window params, dropped harness param |
| 4 | [`real/books-discover`](./real/books-discover) | real site | Faithful crawl across full pagination |

---

## Sandbox examples

### 1. `sandbox/pdf-crawl` — faithful port (crawl)
**Task:** crawl `sandbox.intuned.dev/pdfs` and return every PDF URL with its product.
**Shows:** the default **faithful 1:1 port** — pagination loop and table extraction
preserved verbatim; only the boundary changes (browser bootstrap stripped,
`page.goto` → `go_to_url`, output returned instead of written). No `extend_payload`.

### 2. `sandbox/login` — AuthSessions exception (auth)
**Task:** log into the sandbox, land on the protected list, extract the rows.
**Shows:** the one sanctioned re-architecture ([ADR 0002](../docs/adr/0002-auth-via-authsessions.md)).
The inline login splits into [`auth-sessions/create.py`](./sandbox/login/intuned-project/auth-sessions/create.py)
(craft's **live-verified** selectors) + a derived [`check.py`](./sandbox/login/intuned-project/auth-sessions/check.py);
[`api/list.py`](./sandbox/login/intuned-project/api/list.py) runs already-authenticated.
Credentials are the **public demo creds** printed on the sandbox login page.

## Real-site examples

### 3. `real/techcrunch-startup-news` — faithful scrape
**Task:** scrape TechCrunch startup news from the last N days.
**Shows:** parameter mapping in the faithful path — `days_back` + `category_url`
survive as typed params whose defaults reproduce the task; the harness-only
`output_filename` param is **dropped**. Verified end to end (local + deployed
platform run returned identical counts).

### 4. `real/books-discover` — faithful crawl (full pagination)
**Task:** crawl `books.toscrape.com` and return every book detail URL.
**Shows:** a crawl over real-site pagination ported to a single `automation`
returning a flat de-duplicated list — the canonical "return all the URLs"
faithful port, on an external site.

---

All four conversions and the gotchas they surfaced are recorded in
[`../docs/TEST-RESULTS.md`](../docs/TEST-RESULTS.md).
