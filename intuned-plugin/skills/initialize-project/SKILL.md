---
name: initialize-project
description: "Turn an empty workspace into an Intuned project — pick the language and template and install dependencies. Use when the workspace has no project files yet."
---

# Initialize Project

The capability is turning an empty workspace into an Intuned project: pick the language and a template, create it with `intunedctl dev init`, and install dependencies. Use the language the user already specified; if none was given, ask whether they want TypeScript or Python. **Do NOT add "(Recommended)"** to either option — both are equally supported. The only exception: when the user explicitly says "crawler", **Python is preferred** unless they request otherwise.

## What the template gives you

A template is a real, runnable starting point. Its **folder layout** shows how an Intuned project is organized, and when the user’s task lines up with what the template demonstrates, the included code often reflects **good practices** for scraping or automation (patterns, SDK usage). Reuse what fits the target site; replace, trim, or regenerate the rest (selectors, URLs, flows).

**Template credentials are not valid for the user’s site.** If the tree includes auth-related material under `.parameters` (for example `auth-sessions` or stored session parameters), those belong to the template’s example only and won’t work for the requested website. Obtain credentials (or sessions) for **that** site — write the credential parameter file with empty placeholder fields and ask the user to fill in the values directly (not in chat; see the `auth-sessions` skill). Don’t read those files to “verify” or copy secrets.

## Discovering and choosing a template

Always list templates dynamically first — never hardcode template IDs. Filter to the **starter** templates with `--tag starter`:

```bash
intunedctl dev list-templates --language <python|typescript> --tag starter
```

This outputs a JSON array of templates:

```json
[
  {
    "id": "template-id",
    "language": "python",
    "name": "Template Display Name",
    "tags": ["tag1", "tag2"]
  }
]
```

Pick the template that best matches the user's request:

- For generic browser scraping: use the default starter template for the language.
- For specific use cases: match the template `name` and `tags` to the user's goal. The `tags` field identifies the template's purpose (e.g., `"intuned-browser-sdk-apis"` for browser SDK projects).

## Initializing the project

```bash
intunedctl dev init . --template <template-id> --language <language> --non-interactive --install-deps
```

This creates all project files in the current workspace directory and installs dependencies. The `.` argument targets the current directory; `--non-interactive` is required so the CLI runs without prompts.

If any file being written already exists, the command errors and lists the conflicting files. Unrelated files already in the directory are not affected. To force overwriting existing files, add `--overwrite`:

```bash
intunedctl dev init . --template <template-id> --language <language> --non-interactive --overwrite --install-deps
```

**Optional capability flags** — add these flags based on what was encountered during exploration. They bake the settings directly into `Intuned.json` at init time:

- `--install-deps` — installs dependencies after project creation (runs `uv sync` for Python or `yarn install` for TypeScript).
- `--stealth` — writes stealth-mode config (`stealthMode` in `Intuned.json`). Takes effect on deployed runs, not in local dev. See the `bot-detection` skill.
- `--captcha-solve` — writes the captcha-solver config (`captchaSolver` in `Intuned.json`). Takes effect on deployed runs, not in local dev. See the `bot-detection` skill.
- `--proxy <url>` — sets the dev proxy URL (`proxy.dev` in `Intuned.json`). Add this if a user-supplied proxy was required to access the site during exploration (never invent a URL).
- `--proxy-deployed` — also sets the deployed proxy to the same URL (`proxy.deployed` in `Intuned.json`). Only add this alongside `--proxy` if the user confirmed they want the proxy to apply when the project runs on the Intuned platform.

**Important:** The `intunedctl dev init` command will show you what files were added, modified, line insertions and deletions. It will NOT show insertions and deletions of sensitive data such as user credentials under `.parameters` (e.g. `auth-sessions`). If the summary indicates those paths changed, you still **cannot** trust any template credentials for the user’s target site—**ask for the correct credentials** for the requested website (see [What the template gives you](#what-the-template-gives-you)). Do not read credential files to verify or copy values.

Give a close look at what changed and what is added. If a file was overwritten, review the changes and apply what you need.

## Show the project overview

After initialization completes, show the user a **file tree** summary of the project with a brief one-line description of the key files/folders. For example:

```
📁 Project initialized with template: <template-name>

├── src/
│   └── main.py          — entry point
├── Intuned.json         — project configuration
├── pyproject.toml       — Python dependencies
└── ...

Template includes: <brief note on what the template provides, e.g. "browser SDK with network interception support">
```

Don't include any file or folder that is considered hidden and starts with ".".

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
