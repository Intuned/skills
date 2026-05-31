# Local runs verify logic; the deployed platform run is the gate for protected sites

Intuned's anti-detection features — stealth mode and CAPTCHA solving — work
**only on the deployed platform**, never under local `intuned dev run`. (Proxies
and `headful` are also platform/run-level.)

Consequence for the test loop:

- For **unprotected** targets (the Intuned sandbox, books.toscrape.com, docs),
  the local run `intuned dev run api <name> '<json>'` is the authoritative
  green-gate before deploy.
- For **protected** targets (e.g. Airbnb, CoinMarketCap, major retailers), a
  local run will likely be blocked, and that block is **expected — not a port
  failure**. The real verification is: enable `headful` + `stealthMode` (and
  `captchaSolver`/`proxy` if the deployed run shows a wall) in `Intuned.jsonc`,
  deploy, then `intuned platform runs start` and poll `runs get`. The deployed
  run is the only meaningful gate.

A naive "must be green locally before deploy" rule is therefore wrong for
protected sites and is explicitly relaxed there: gate on "logic reached the
wall," then let the deployed run be the judge.

Exception within the exception: an **expected-rejection** task (LinkedIn behind
an auth wall) must NOT have stealth/captcha enabled to defeat the wall — a clean,
reported rejection, locally and deployed, is its pass condition.
