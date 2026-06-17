## intuned dev proxy

Manage the dev proxy used by local browser instances. By default, setting/clearing restarts the browser.

### `intuned dev proxy set <proxy-url> [options]`

Set the dev proxy. Proxy URL format: `http://username:password@domain:port`.

- `<proxy-url>`: required. Full proxy URL including credentials if needed.
- `-n, --name <name>` (default `default`): browser instance name.
- `--no-browser-restart`: do not restart the browser after setting.
- `--deployed`: also set the deployed proxy (applies in deployed environments), in addition to dev.
- `--settings-format <format>`: settings file format override.
- `--json`: machine-readable output.

### `intuned dev proxy clear [options]`

Clear both the dev and deployed proxy.

- `-n, --name <name>` (default `default`): browser instance name.
- `--no-browser-restart`: do not restart the browser after clearing.
- `--json`: machine-readable output.

### When to use

A user-supplied proxy is the **only** anti-bot lever that actually works in local dev (stealth mode and the CAPTCHA solver are platform-only). Use it when the target site is geo-restricted or the user's IP is being rate-limited / blocked. Always supply a real user-given proxy URL — never invent one, and don't use `intuned://auto`.
