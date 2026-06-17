## intunedctl dev attempt

Useful for running and testing an API locally with a single attempt.

Use the Bash tool to run the command and set the `timeout` to at least `600000` (10 min). If it exits with code `143`, call `extendTimeout` inside the API code and increase the Bash `timeout`.

### Local testing mode: `MODE=generate_code`

When testing locally, set `export MODE=generate_code` before `dev attempt` (once per shell session). This puts the runtime in code-generation mode: **file/attachment uploads are mocked** — `save_file_to_s3` / `upload_file_to_s3` skip the real S3 upload and return a mock `Attachment` (`bucket: "testing_bucket"`, `region: "testing_region"`, UUID key), and signed URLs return a placeholder. The download still runs, so the attachment path is exercised **without needing real S3 credentials or a provisioned project**.

```bash
export MODE=generate_code
intunedctl dev attempt api <api-name> .parameters/api/<api-name>/default.json --cdp-browser-name default --cdp-tab-id <tab-id>
```

For an API that captures attachments, a **non-empty** list of these mocks confirms the upload path works; an empty list is correct only when the page genuinely has no files. Real uploads to managed S3 happen on deployed runs and `dev test-job`, which need the project provisioned.

- `intunedctl dev attempt api <api-name> <parameters> [options]`:

  - Run a single API locally and print its results to stdout.
  - `<api-name>`: The name of the API to run.
  - `<parameters>`: Parameters can be either:
    - Inline JSON: `'{"parameter_1":"value"}'`
    - Path to a `.json` file containing the JSON parameters.
      This is usually used with `.parameters/api/<api-name>/<parameter_name>.json`.
  - Options:
    - `--proxy`: Used to attempt the API on this proxy. Takes no effect if `--cdp-browser-name` is passed.
    - `--headless`: Run the attempt in a headless browser (default: false). This will not open a browser window. Takes no effect when `--cdp-browser-name` is passed.
    - `--cdp-browser-name`: Attempt the API on a given browser instance. This is typically used when you have already started a browser using `intunedctl dev browser start` and want to run on that already open browser.
    - `--cdp-tab-id`: Attempt the API on a specific tab in the given browser. Must be used together with `--cdp-browser-name`.
    - `--trace`: Capture a Playwright trace of the attempt, useful for debugging. Works perfectly with the `trace-debugging` skill.
    - `--timeout <time>`: Timeout for each attempt - milliseconds or ms-formatted string (default: "10 mins").
    - `--start-to-end-timeout <time>`: Overall timeout from start to end of command - milliseconds or ms-formatted string (default: "12 hours").
  - `--timeout` vs `--start-to-end-timeout`: `--timeout` can be extended using `extendTimeout` (TS) or `extend_timeout` (Python). When one of these is called, the timeout refreshes and resets to its value. `--start-to-end-timeout` is not affected by extending the timeout. It is a hard limit on the total execution time.
  - It is recommended to attempt the API on an existing browser. You can always create a new tab on an existing browser you created previously and attempt on it.

- `intunedctl dev attempt authsession check <id> [options]`:

  - Run a single AuthSession:Check attempt against an existing session. Auth sessions must be enabled in `Intuned.json`.
  - `<id>`: auth session ID under `./auth-sessions-instances/<id>`.
  - Shared options: `--proxy`, `--timeout`, `--start-to-end-timeout`, `--headless`, `--trace`, `--traces-path`, `--auth-session-instances-path`, `--keep-browser-open`, `--cdp-url`, `--cdp-browser-name`, `--cdp-tab-id`.

- `intunedctl dev attempt authsession create <parameters> [options]`:
  - Run a single AuthSession:Create attempt. Auth sessions must be enabled in `Intuned.json`.
  - `<parameters>`: Inline JSON or path to a JSON file.
  - `--id <id>`: ID of the auth session to create (default `auth-session-{timestamp}`). Files end up in `./auth-sessions-instances/<id>`.
  - Shared options as above.

For runs with retry logic (closer to production behavior), use `intunedctl dev run` instead — see `dev_run.md`.
