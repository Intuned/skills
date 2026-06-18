---
name: proxy
user-invocable: false
description: "Route browser traffic through a proxy to beat IP blocks, geo-restrictions, and rate limiting — either a user-supplied proxy (works in local dev and once deployed) or Intuned's platform auto proxy (deployed only, no proxy of your own needed). Load when a site IP-blocks, geo-restricts, or rate-limits you."
---

# Proxy

A proxy routes browser traffic through a different IP address so requests appear to come from another location. Use a proxy to bypass IP-based blocking, geo-restrictions, and rate limiting — cases where stealth mode won't help because the site is blocking your **IP address** rather than your browser fingerprint.

A **user-supplied** proxy is the one anti-bot lever you can apply and verify in **local dev**. Stealth mode, the CAPTCHA solver, and Intuned's **auto proxy** are platform features — you configure them now and they only engage once the project is deployed.

Before reaching for any proxy, confirm the site is actually **IP-blocking** (test without a proxy first) rather than fingerprinting or showing a CAPTCHA — those need stealth / the CAPTCHA solver (see the `bot-detection` skill).

## Which proxy to use

**If the user has their own proxy** — use it. Ask them for the URL; **never invent one**. A user-supplied proxy works in **both** local dev and deployed runs, so you can apply and verify it locally. Format: `http://username:password@domain:port`.

> Do not use askUserQuestion to ask the user for the proxy, ask it immediately as a free text.

**If the user does NOT have a proxy** — suggest Intuned's **auto proxy** (`intuned://auto`). It's platform-provided, so the user doesn't need to supply or pay for one. Like stealth mode and the CAPTCHA solver, it's a **deployed** feature: configure it now and it takes effect once the project runs on the platform — it does **not** engage in local dev (the CLI will note "auto proxy is not available in connected mode; it will be resolved on deployed projects"). Set it on the **deployed** proxy only:

```bash
intuned dev proxy set "intuned://auto" --deployed
```

(equivalently, `proxy.deployed: "intuned://auto"` in `Intuned.json`). Don't set `intuned://auto` as the local dev proxy — it has no effect there.

## Setting a proxy via CLI

Set the proxy and restart the browser in a single step:

```bash
intuned dev proxy set "<proxy-url>"
```

To also apply the proxy when the project runs on the Intuned platform (deployed), add `--deployed`:

```bash
intuned dev proxy set "<proxy-url>" --deployed
```

Use `--deployed` selectively — only when the site also blocks Intuned's platform IPs in production.

**If a browser is open, the proxy only takes effect once the browser is restarted.** The CLI command above handles that restart automatically.

## Configuring a proxy in `Intuned.json`

The CLI writes this config for you, but you can also set it directly:

```json
{
  "proxy": {
    "dev": "http://username:password@domain:port",
    "deployed": "http://username:password@domain:port"
  }
}
```

| Field      | Description                                              |
| ---------- | -------------------------------------------------------- |
| `dev`      | Proxy used during local development (`intuned dev`)      |
| `deployed` | Proxy used when the project runs on the Intuned platform |

## Proxy types

| Type            | Description                          | Cost               | Best for                                          |
| --------------- | ------------------------------------ | ------------------ | ------------------------------------------------- |
| **Residential** | IPs from real ISP users              | Per GB (expensive) | Heavily protected sites that block datacenter IPs |
| **Datacenter**  | IPs from cloud data centers          | Per IP/month       | General use where IP rotation is sufficient       |
| **ISP**         | Datacenter-hosted but ISP-registered | Per IP/month       | Balance of reliability and cost                   |

## When a proxy isn't the right lever

If the site is detecting your browser fingerprint or showing a CAPTCHA (rather than IP-blocking), a proxy won't fix it — see the `bot-detection` skill for stealth mode and the CAPTCHA solver.
