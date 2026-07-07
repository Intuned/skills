---
name: project-settings
user-invocable: false
description: "Reference for the `Intuned.json` project configuration file — what each field means (replication, apiAccess, headful, browserSize, region, authSessions, stealthMode, captchaSolver) and how to set default result sinks. Load when inspecting or editing Intuned.json settings."
---

# Intuned Project Settings

Configuration for `Intuned.json` at the project root — controls how the project runs locally and on the Intuned Platform.

Many settings have their own home: stealth and the CAPTCHA solver in the `bot-detection` skill; proxy in the `proxy` skill; auth sessions in the `auth-sessions` skill; project identity (`projectName`) via `intuned dev provision` (see `create-intuned-project`). Read this page to understand what the fields mean when you inspect or edit `Intuned.json`; reach for `search_intuned` → `query_docs_filesystem_intuned` for anything not covered here.

## Core properties

| Field               | Type    | Notes                                                                                                                                                                                  |
| ------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `replication`       | object  | `maxConcurrentRequests` (number, default `1`) + `size` (`"standard"` \| `"large"` \| `"x-large"`, default `"standard"`)                                                                |
| `apiAccess.enabled` | boolean | default `true`. Set `false` for jobs-only projects                                                                                                                                     |
| `authSessions`      | object  | `enabled` (bool), `type` (`"API"` \| `"MANUAL"`); MANUAL also needs `startUrl`, `finishUrl`, `browserMode` (`"fullscreen"` \| `"kiosk"`). Full flow lives in the `auth-sessions` skill |
| `headful`           | boolean | default `false`. Required `true` for CAPTCHA solving                                                                                                                                   |
| `browserSize`       | object  | `width` 200–3840 (default `1024`), `height` 200–2160 (default `800`)                                                                                                                   |
| `region`            | string  | default `"us"`. Options: `us`, `au`, `ca`, `nl`, `mx`, `ro`, `se`, `sg`, `es`, `za`, `de`, `in`, `hk`, `jp`, `pl`, `fr`, `gb`                                                          |

## Anti-bot toggles — `stealthMode` / `captchaSolver`

- **`stealthMode.enabled`** and **`captchaSolver.enabled`** are configured in `Intuned.json` (the `captchaSolver` solver also needs the `wait_for_captcha_solve` / `waitForCaptchaSolve` code helpers, and `captchaSolver` requires `headful: true`). The **`bot-detection`** skill owns the full config and decision flow.
- These engage on **deployed runs** — they don't activate during local dev, so configure them now and they take effect once the project runs on the platform. A normal user-supplied proxy (see the `proxy` skill) is the one anti-bot lever that also works locally.

## Default sinks — `defaults.sink`

Sinks deliver Run results to an external system (webhook or S3-compatible bucket). You can set a **project-wide default** in `Intuned.json` under `defaults.sink`, scoped per environment (`dev` for local runs, `deployed` for platform runs). Per-Job sinks in `intuned-resources/jobs/*.job.json` override this default.

```json
{
  "defaults": {
    "sink": {
      "dev": {
        "type": "webhook",
        "url": "https://example.com/hook",
        "skipOnFail": false
      },
      "deployed": {
        "type": "s3",
        "bucket": "my-bucket",
        "accessKeyId": "...",
        "secretAccessKey": "...",
        "skipOnFail": false
      }
    }
  }
}
```

**Shape** — every sink has `type` (`"webhook"` \| `"s3"`), `skipOnFail` (required bool), `apisToSend` (optional string array).

- `webhook`: adds `url` (required), `headers` (optional map).
- `s3`: adds `bucket`, `accessKeyId`, `secretAccessKey` (required); `region`, `prefix`, `endpoint`, `forcePathStyle` (optional).

For per-Job sink placement and advanced cases, see the `manage-jobs` skill and the Intuned docs.

## Reference shape

A representative `Intuned.json` — not every field is required; use this to orient when reading an existing file.

```json
{
  "workspaceId": "ws_...",
  "projectName": "my-project",
  "replication": { "maxConcurrentRequests": 1, "size": "standard" },
  "apiAccess": { "enabled": true },
  "authSessions": {
    "enabled": false,
    "type": "API"
  },
  "headful": false,
  "browserSize": { "width": 1024, "height": 800 },
  "region": "us",
  "stealthMode": { "enabled": false },
  "captchaSolver": { "enabled": false },
  "defaults": {
    "sink": {
      "deployed": {
        "type": "webhook",
        "url": "https://example.com/hook",
        "skipOnFail": false
      }
    }
  }
}
```

## When to search the docs

Go to `search_intuned` → `query_docs_filesystem_intuned` when you need:

- Fields not listed here (integrations, metadata, other `defaults` keys like `proxy` / `retry` / `requestTimeout`)
- The full CAPTCHA-provider catalog with provider-specific notes
- Region availability changes or new machine sizes
