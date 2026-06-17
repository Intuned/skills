## intuned dev stealth

Write stealth-mode config into `Intuned.json`. Configure it here and it takes effect once the project runs on the platform — it doesn't engage during local dev (these commands set the config flag; the local browser isn't actually made stealthy), so there's nothing to validate locally. See the `bot-detection` skill.

### `intuned dev stealth enable [options]`

Set `stealthMode.enabled: true` in `Intuned.json`.

- `-n, --name <name>` (default `default`): browser instance name.
- `--settings-format <format>`: settings file format override.
- `--json`: machine-readable output.

### `intuned dev stealth disable [options]`

Set `stealthMode.enabled: false` in `Intuned.json`.

- `-n, --name <name>` (default `default`): browser instance name.
- `--json`: machine-readable output.

### When to use

Write stealth config when a site detects automation by browser fingerprint. It engages once deployed, so confirm it via a deployed run / `intuned dev test-job` after `intuned dev deploy`. While working locally, the anti-bot lever that actually engages is a user-supplied proxy (`intuned dev proxy`).
