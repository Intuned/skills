## intuned dev captcha-solve

Write CAPTCHA-solver config into `Intuned.json`. Configure it here and it runs once the project runs on the platform — it doesn't engage during local dev (these commands set the config; no solver runs against the local browser), so there's nothing to validate locally. See the `bot-detection` skill.

### `intuned dev captcha-solve enable [options]`

Write the captcha solver config into `Intuned.json` (with all providers pre-configured). Requires `headful: true` + `stealthMode.enabled: true` to take effect on the platform.

- `-n, --name <name>` (default `default`): browser instance name.
- `--settings-format <format>`: settings file format override.
- `--json`: machine-readable output.

### `intuned dev captcha-solve disable [options]`

Remove / disable the captcha solver config in `Intuned.json`.

- `-n, --name <name>` (default `default`): browser instance name.
- `--json`: machine-readable output.

### When to use

Write CAPTCHA-solver config when the target site presents CAPTCHAs. It engages once deployed, so confirm it via a deployed run / `intuned dev test-job` after `intuned dev deploy`. While working locally, the anti-bot lever that actually engages is a user-supplied proxy (`intuned dev proxy`).
