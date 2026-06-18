# Intuned CLI hooks

These are **Intuned CLI hooks** — event handlers the `intuned` CLI fires around
every command it runs (`onCommandStart` / `onCommandComplete`), receiving the
command and its result as JSON on stdin. They are **not** Claude Code hooks.

The plugin's session-start hook (`scripts/setup-cli-hooks.sh`, via
`intuned dev agent-hooks setup`) installs these into the project's
`.intuned/agent-hooks/` so they're active for the session. They give the agent
predictable, machine-readable CLI behavior and tidy artifacts under
`.intuned-agent/`.

## Command shaping (`onCommandStart`)

Adjust a command's options _before_ it runs:

| Hook                                  | What it does                                                                                                                                                                                                    |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `validate-output-path.ts`             | For `platform attempts trace` / `log`, injects a default `-o` output path under `.intuned-agent/platform-attempts/<runId>/` when the user didn't pass one — so results always land in a known place.            |
| `inject-non-interactive.ts`           | Injects `--non-interactive` into `platform attempts get` / `log` / `trace` so the CLI never blocks on a prompt when the agent runs it.                                                                          |
| `inject-settings-format.ts`           | Injects `settingsFormat: "json"` into `dev init` / `dev stealth` / `dev captcha-solve` / `dev proxy` so settings are read/written as JSON.                                                                      |
| `artifacts-command-start-mutation.ts` | For API and auth-session attempt commands: creates the run directory under the artifacts root, redirects the command's output there, and obfuscates sensitive parameter values (e.g. auth-session credentials). |

## Artifacts capture (command lifecycle)

| Hook                                  | What it does                                                                                                                                                                             |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `artifacts-command-events-capture.ts` | Records command start/complete events and writes result and metadata artifacts into the per-run folder under `.intuned-agent/`.                                                          |
| `artifacts-common.ts`                 | Shared library (types + helpers) used by the TypeScript hooks above — reading hook input, classifying commands, resolving run dirs, obfuscating values, writing JSON. Not a hook itself. |

## Browser & tab lifecycle (`onCommandComplete`)

| Hook                         | What it does                                                                                                                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connect-browser-control.sh` | On browser start, tab create, or stealth/captcha toggle, tells the MCP control server to connect to the browser so network tracking starts immediately — without waiting for the first tool call. |
| `network-tracking-hint.sh`   | On browser start or tab create, prints where the tab's network traces are recorded (`.intuned-agent/tab_<id>/network/`).                                                                          |
| `cleanup-tab-data.sh`        | On browser stop, tab close, or stealth/captcha toggle, removes the matching `.intuned-agent/tab_*` folders.                                                                                       |
