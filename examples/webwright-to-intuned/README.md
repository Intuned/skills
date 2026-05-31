# Examples

Four Webwright **Crafted CLIs** to port with the `webwright-to-intuned` skill —
**two on Intuned's public sandbox** (always reproducible) and **two on real
third-party sites** (representative of production work). Each folder holds the
craft (the draft you port); run the skill against it to produce the Intuned
project.

Each example folder contains:

```
<example>/
└── craft/                 # the Webwright Crafted CLI — the draft you port
    ├── final_script.py    #   the parameterized logic
    ├── plan.md            #   the # Parameters table (authoritative param spec)
    ├── task.json          #   task text + start_url
    └── final_runs/run_*/  #   one known-good output (match its shape/count)
```

Point the skill at a craft — e.g. ask the agent:

```
Port the Webwright craft in examples/<group>/<name>/craft to Intuned
```

Check your port against the craft's `final_runs/` known-good output. For the full
verification procedure (local gate, deploy gate, expected results per example),
see [`TESTING.md`](./TESTING.md).

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
**Port exercises:** the default **faithful 1:1 port** — pagination loop and table
extraction preserved verbatim; only the boundary changes (browser bootstrap
stripped, `page.goto` → `go_to_url`, output returned instead of written). No
`extend_payload`.

### 2. `sandbox/login` — AuthSessions exception (auth)
**Task:** log into the sandbox, land on the protected list, extract the rows.
**Port exercises:** the one sanctioned re-architecture (AuthSessions, DECISIONS.md
§2) — the inline login splits into an `auth-sessions/create.py` (using the craft's
live-verified selectors) plus a derived `check.py`, and the api runs
already-authenticated. Credentials are the **public demo creds** printed on the
sandbox login page.

## Real-site examples

### 3. `real/techcrunch-startup-news` — faithful scrape
**Task:** scrape TechCrunch startup news from the last N days.
**Port exercises:** parameter mapping in the faithful path — `days_back` +
`category_url` survive as typed params whose defaults reproduce the task; the
harness-only `output_filename` param is **dropped**.

### 4. `real/books-discover` — faithful crawl (full pagination)
**Task:** crawl `books.toscrape.com` and return every book detail URL.
**Port exercises:** a crawl over real-site pagination ported to a single
`automation` returning a flat de-duplicated list — the canonical "return all the
URLs" faithful port, on an external site.
