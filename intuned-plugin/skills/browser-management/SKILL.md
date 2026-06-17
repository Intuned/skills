---
name: browser-management
description: "Start, stop, and manage the tabs of the persistent local browser that Intuned automations and the selector tools run against (`intuned dev browser`). Must Load when you need to start a browser or tab to work in, when creating separate tabs so parallel work doesn't collide, When no browser executable is found or when the browser is stuck and needs recovering."
---

## Prerequisite: a Chromium binary must be available

`intuned dev browser start` launches a real Chromium and has to find one. This requirement is satisfied by either:

1. Running inside an Intuned project that has Playwright installed (the CLI uses Playwright's bundled Chromium automatically), or
2. The `INTUNED_CHROMIUM_PATH` environment variable pointing at a Chromium (or Chrome) executable.

If no chromium executable is present, then you must initialize an pyproject.toml or a package.json in the working dir(depending on the language picked by the user), and install playwright in it. You will be able to use playwright's browser.

**IMPORTANT**: Even if you are in plan mode and considered read-only, you still can and should initialize a project in order to have a `pyproject.toml` or a `package.json` with a playwright library so that you can start a browser and proceed with your work.

# Browser & Tab Management

The capability is control over a single local browser for web automation. Lifecycle and tabs are managed via `intuned dev browser` (run in Bash). All browser _interactions_ (navigation, clicking, typing, reading the page) go through the browser tools (`navigate`, `find`, `computer`, …) — not the CLI.

**One browser at a time** — two concurrent browsers can't run.

**Headless**: Always start and work with a headless browser unless the user asks for a headful one or you encounter bot-detection cases.

## Lifecycle commands

| Command                                                  | Purpose                                                     |
| -------------------------------------------------------- | ----------------------------------------------------------- |
| `intuned dev browser start --headless`                   | Start the browser. Opens with one initial tab               |
| `intuned dev browser stop`                               | Stop the browser. Always stop when you're done with a task. |
| `intuned dev browser status`                             | Check if a browser is running and list its tabs.            |
| `intuned dev browser tabs create`                        | Create a new tab. Returns the new tab ID.                   |
| `intuned dev browser tabs list`                          | List all open tabs.                                         |
| `intuned dev browser tabs close <tab_id1> <tab_id2> ...` | Close one or more tabs.                                     |

For any flag not shown here, run `intuned dev browser --help` or `intuned dev browser tabs --help`.

## Working with multiple tabs

Use multiple tabs when a task needs to work against several pages at once.

- Create a fresh tab per URL you need to keep open: `intuned dev browser tabs create` (returns the new `tab_id`).
- Pass the right `tab_id` to each browser tool call so actions land on the page you mean.
- Close tabs you no longer need with `intuned dev browser tabs close <tab_id> ...` to keep the session tidy.

### Example: keeping 3 pages open

```
intuned dev browser tabs create   # → tab_id_1 → https://example.com/page/1
intuned dev browser tabs create   # → tab_id_2 → https://example.com/page/2
intuned dev browser tabs create   # → tab_id_3 → https://example.com/page/3
```

Then navigate and interact with each tab by passing its `tab_id` to the browser tools.

## Browser crash recovery

If a browser tool is denied with "Browser is closed", or the browser crashed: restart with `intuned dev browser start --headless`, then resume unfinished work with freshly created tabs — old tab IDs are no longer valid.

## When the proxy is set or cleared

Setting or clearing the dev proxy restarts the browser. After it restarts, existing tab IDs are invalid — start fresh and recreate tabs as needed. (Stealth mode and the CAPTCHA solver take effect on the platform, not in local dev — configure them via the `bot-detection` skill.)

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
