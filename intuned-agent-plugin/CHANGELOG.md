# Changelog

All notable changes to the Intuned Agent Plugin are documented here.

## 0.1.0 - 2026-06-18

- Initial release.
- 21 authoring skills covering project scaffolding, API implementation,
  testing, editing, and debugging of Intuned browser-automation projects.
- Browser MCP server (`browser`) exposing navigation, extraction, pagination,
  and file-handling tools under `mcp__plugin_intuned_browser__*`.
- Live documentation via the `intuned-docs` HTTP MCP server.
- SessionStart hook that runs `intuned dev agent-hooks setup` to wire up CLI
  hooks (artifact capture, result compaction, browser network tracking).
- PreToolUse hook that injects CDP connection details before browser tool calls.
