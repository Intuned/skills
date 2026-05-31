# Test results — webwright-to-intuned

End-to-end verification of the skill by porting real Webwright crafts into
deployed Intuned projects in a workspace. Each port was driven by hand following
`reference/transformation-rules.md`; every gotcha hit was folded into
`reference/gotchas.md`.

Pipeline verified per port: **validate craft → scaffold (`intuned dev init`) →
transform → local gate (`intuned dev run`) → deploy (`intuned dev deploy`) →
platform standalone run (`intuned platform runs start`)**.

## Coverage matrix

| Craft (input) | Exercises | Local run | Deploy | Platform run | Result |
|---|---|---|---|---|---|
| `techcrunch_ai_craft` → `techcrunch-startup-news` / `news` | faithful scrape + params (`days_back`, `category_url`); dropped `output_filename` | ✅ 30 items | ✅ | ✅ **SUCCEEDED** | 30 items, identical local & platform |
| `sandbox-login_craft` → `sandbox-login` / `list` | **AuthSessions exception** (ADR 0002): `create.py`+`check.py`, session-applied automation | ✅ create+check+run | ✅ | ✅ with `authSession:{id}` | 10 rows extracted |
| `sandbox-pdf-crawl_craft` → `sandbox-pdf-crawl` / `crawl` | crawl, pagination helper, no fan-out | ✅ 2 PDFs | ✅ | ✅ **completed** | 2 unique PDF records |
| `form-fill-dummy_craft` → `form-fill-dummy` / `submit` | multi-step form RPA, 9 params, **Browserbase block stripped** (G13) | ✅ all steps execute | ✅ | ✅ **completed** | faithful: `submitted=false` matches craft's final verdict (G14) |
| `books-discover_craft` → `books-discover` / `discover` | real-site crawl, full pagination, **Browserbase block stripped** (G13), no fan-out | ✅ 1000 URLs / 50 pages | ✅ | ✅ **completed**, 1000 URLs / 50 pages | 1000 unique book URLs, matches craft |

**Five** ports verified through a deployed **platform standalone run**.

### Bundled examples vs verified ports
The `examples/` folder bundles **four demonstrations** — `sandbox/pdf-crawl`,
`sandbox/login`, `real/techcrunch-startup-news`, `real/books-discover`. All four
are among the verified ports above. `form-fill-dummy` is also verified here but is
not bundled as an example (its "no visible confirmation" outcome makes it a weaker
teaching example than a clean crawl).

Deployed projects (one per port): `techcrunch-startup-news`, `sandbox-login`,
`sandbox-pdf-crawl`, `form-fill-dummy`, `books-discover` — each deployed and its
standalone platform run completed successfully.

> Note (extends G12): with `--wait`, the payload may sit at `result` directly;
> with `runs get` it sits at `result.output`. Read defensively
> (`result.output or result`).

## What this proves
- The **faithful-port contract** (ADR 0001) works: strip browser bootstrap →
  `automation(page, params)`, `page.goto`→`go_to_url`, drop harness params
  (`output_filename`) and artifacts, defaults reproduce the task. A scrape ran
  byte-identical locally and on the platform.
- The **AuthSessions exception** (ADR 0002) works **end to end on the platform**:
  the craft's live-verified login selectors ported into `create.py`, a derived
  `check.py`, and a deployed run consuming a platform-created session.
- The **local-vs-platform gate split** (ADR 0003) holds: unprotected sandbox/
  news targets pass locally; the platform run is the real gate.

## Gotchas discovered while testing (now in gotchas.md)
- G10 platform auth-session run shape (`authSession:{id}`, pre-created).
- G11 don't regex-edit `.jsonc` (eats `//` in URLs).
- G12 platform output is nested (`result.output`) + async + UPPERCASE status.
- G13 strip Browserbase/CDP provider blocks too, not just local launch.
- G14 ambiguous "submitted" — judge against the craft's own final verdict.

## Not yet ported (protected sites / expected-rejection — by design need deploy gate)
`airbnb_source`, `crypto`, `ecommerce-price-compare` (headful+stealth, verified
only via platform run), `linkedin-profile` (expected-rejection — no stealth),
`books-discover` (craft phase failed in the Webwright loop; re-craft needed),
`docs-crawler`, `sandbox-book-consultation`. The skill handles these via the
stealth/expected-rejection rules in `transformation-rules.md`; they were not run
end-to-end here because protected-site verification consumes deployed runs and
several target sites actively block automation.
