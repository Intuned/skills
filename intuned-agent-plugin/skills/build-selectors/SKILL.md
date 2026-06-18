---
name: build-selectors
user-invocable: false
description: "Build reliable selectors for an Intuned API using the browser selector tools — never by hand. Load whenever you need selectors for a page before writing or fixing API code, including auth-session login flows."
---

# Build Selectors

Building selectors is the capability of turning a live page into reliable selectors an Intuned API can rely on. You find elements with the browser tools and build stable selectors for them.

## Golden rule: never write selectors by hand

Every selector MUST come from the `build_reliable_selector` or `build_field_selector` tools. **Never write, guess, or copy a selector from the DOM yourself.** Hand-written selectors (generated class names, inspected XPath, HTML structure) are fragile and break when the site changes; the tools analyze the page — and multiple pages when you give them — to produce selectors you can't replicate by hand.

If a selector didn't come from those two tools, it's invalid.

## The selector tools

The loop for every element is always **find it → build its selector immediately → move on**. Element IDs are ephemeral (see below), so never batch all the finds and build later.

### `find` — locate an element

Handles natural language and exact visible text:

```text
find("the product title")    # by description
find("next page button")     # by description
find("Add to Cart")          # by exact visible text
```

- If you can see the **exact text** on the page, pass only that text (`find("Hello World")`), not prose around it (`find("the row that says Hello World")`) — then use `build_field_selector` to reach the parent/row.
- Use natural-language queries when there's no text anchor (`"the main search input"`) or the text repeats and needs disambiguation.
- If `find` fails: `query_by_selector` (when you know a CSS pattern like `input[type=email]`), or `inspect_element` (to examine structure).

For hidden data that needs interaction: find the trigger (expander, "Show more", tab) → build its selector → click to reveal → find and build the revealed data.

### `build_reliable_selector` — standalone, list, and page-level elements

For repeating items (table rows, list items, cards), unique page elements (a price, a title, a status badge), and page-level controls (buttons, headings, nav links). **Give candidates from multiple pages when you have multiple URLs** — find the same element on each page and pass each page's `element_id` as a candidate. Building from one page produces fragile selectors.

```text
# After navigating URL 1: find → element_id "abc12"
# After navigating URL 2: find → element_id "def34"
build_reliable_selector(candidates: [
  {tab_id: "<tab>", element_id: "abc12"},   # from URL 1
  {tab_id: "<tab>", element_id: "def34"},   # from URL 2
])
```

Element IDs die on navigation, so capture each page's candidate before navigating away (or build per-page if IDs would go stale). If `find` returns nothing on a given page, omit that page from the candidates — not every element exists everywhere.

### `build_field_selector` — fields inside a container

For a value relative to a parent (price within a product card, name within a row). Use after the container's `build_reliable_selector` exists.

```text
build_field_selector(
  tab_id: "<tab>",
  element_id: "el-price",                  # the price inside the card
  container_element_id: "el-product-card", # the card container
  description: "product price in dollars",
  reason: "extract the price from each product card",
)
```

### `description` and `reason`

Both tools take these — they guide the internal builder:

- **`description`** — a semantic label for what the element _is_: `"product title text"`, `"next page button"`, `"row in the products table"`. Never a CSS selector, XPath, or tag name (`"div.product-title"`, `"tr"`), never vague (`"the element"`).
- **`reason`** — _why_ you need it: `"extract the title from each row"`, `"click to go to the next page"`. Not `"need selector"`.

### Recovering from a build failure

A failure (e.g. "could not find element with element_id on page N") usually means a stale or wrong `element_id`. Re-find the element on that page for a fresh id and retry — don't retry with the same arguments.

## Element IDs are ephemeral

Element IDs are destroyed by **any** page change — navigation, reload, and **pagination** (clicking "Next", loading more, anything that re-renders). After any of these, every prior `element_id` is gone; re-find before building. This is why you build a selector immediately after finding, and why you never include `element_id` values anywhere — only the built selectors are stable.

`element_id` values are **temporary IDs injected dynamically by the browser tools; they do not exist in the real DOM.** Their only job is to make the browser tools (`find`, `build_reliable_selector`, `build_field_selector`, etc.) work. Never use an `element_id` in real automation API code (in `query_selector` / `.locator()` / any selector you write into the project): use the built selectors instead.

For quick navigation actions (scroll, expand, switch tabs) use the `computer` tool with coordinates; use element IDs for anything you need a selector for.

## Blocked pages

If a page is blocked / 403 / unreachable, stop — selectors built there would be invalid. Defer the bot-detection strategy to the **bot-detection** skill.

## Authenticated access

**If the prompt says there's a 2FA / OTP / TOTP step:**: generate a code with `/intuned-agent-plugin/skills/auth-sessions/scripts/generate-2fa-code.sh <param-file>` and fill it into the OTP input, then build reliable selectors for the OTP input and verify button. Then to generate the code: Use the language's import (`import * as OTPAuth from "otpauth"` for TS, `import pyotp` for Python). Read `/intuned-agent-plugin/skills/auth-sessions/resources/handling-2fa.md` for details. Never ask the user for a code. You must produce a code that generates the TOTP programatically from the user's token.

## Parallel tool calling

When you are finding elements that are not correlated, and building reliable selectors or building field selecotrs for different elements, call these tools in parallel for optimal execution time.
