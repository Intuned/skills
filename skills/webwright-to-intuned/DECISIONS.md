# Decisions

The load-bearing decisions behind this skill. Referenced from `SKILL.md`.

## 1. Default to a faithful 1:1 port, not idiomatic re-architecture

The skill's default is a **faithful 1:1 port**: one craft function becomes
exactly one `automation` API with identical behavior, re-fitted only at Intuned's
boundary (injected `page`, typed `params`, returned result). The logic is not
re-architected.

Chosen over free-form re-architecture (e.g. auto-decomposing every crawl into
`list` + `details` with `extend_payload`) because the premise is that a
parameterized CLI already maps cleanly onto a single parameterized Intuned API —
a 1:1 claim. A mechanical, bounded transform is deterministic and testable;
open-ended re-architecture invites hallucination and is hard to verify against
the craft's known-good output. Re-architecture is allowed only through the small
enumerated exceptions below. **"No crawl fan-out by default"** is part of this: a
crawl that returns a list is faithfully one `automation` returning that list.

## 2. Auth crafts → Intuned AuthSessions (overrides decision 1)

A login craft logs in inline; faithful-port would keep that inline. For auth we
deliberately override: decompose into **AuthSessions**.

- Login → `auth-sessions/create.py` (`async def create(page, params)`); credentials
  become create params (default = the task's credentials).
- A derived `auth-sessions/check.py` (`async def check(page) -> bool`) validates an
  existing session via a logged-in-only signal.
- `Intuned.jsonc` enables `authSessions`; the `automation` assumes a valid session
  and does only the post-login work.

This is the one structural re-architecture accepted by default, because
AuthSessions is Intuned's flagship auth mechanism (sessions stored, revalidated,
reused) and a login craft decomposes into it cleanly. Cost: more surface area
(create + check + manifest + params) and a two-step local test
(`intuned dev run authsession create '{creds}'` → run the api with
`--auth-session <id>`). The trickiest derived artifact is `check.py`; verify its
logged-in signal in the test loop, never assume it.

## 3. Local runs verify logic; the deployed platform run is the gate for protected sites

Stealth mode and CAPTCHA solving work **only on the deployed platform**, never
under local `intuned dev run` (proxies and `headful` are also platform/run-level).

- **Unprotected** targets (Intuned sandbox, books.toscrape.com, docs): the local
  run is the authoritative green-gate before deploy.
- **Protected** targets (Airbnb, CoinMarketCap, major retailers): a local run will
  likely be blocked, and that block is **expected — not a port failure**. Enable
  `headful` + `stealthMode` (and `captchaSolver`/`proxy` if the deployed run shows
  a wall) in `Intuned.jsonc`, deploy, then `intuned platform runs start` + poll
  `runs get`. The deployed run is the only meaningful gate.

So a naive "must be green locally before deploy" is wrong for protected sites and
is relaxed there. **Exception within the exception:** an **expected-rejection**
task (LinkedIn behind an auth wall) must NOT enable stealth/captcha to defeat the
wall — a clean reported rejection, locally and deployed, is its pass.
