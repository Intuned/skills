## intuned dev browser

Manage persistent browser instances for local development and automation.

- `intuned dev browser start [options]`:
  - Start a managed browser that will be used for different automations. The browser starts in a separate subprocess and is ready for use.
  - Returns the name of the browser created.
  - Returns the initial tab ID.
  - Use this browser and the tabs in it for all automation work. Used for all MCP tools and used with other Intuned CLI commands.
  - Options:
    - `--headless`: Start a headless browser. Not recommended, easy to get bot detected.
    - `--proxy`: Proxy URL to use for the browser. Recommended only when explicitly asked to use a given proxy.
    - `--json`: Return a JSON output.

- `intuned dev browser stop`:
  - Stop a running browser instance.

- `intuned dev browser status [options]`:
  - Return a summary of browser status, including: CDP Address, CDP Port, PID, Headless, Started, and Tabs.
  - Options:
    - `--json`: Return result in JSON format.

- `intuned dev browser tabs create [options]`:
  - Create a new tab in the browser.
  - Returns the tab ID of the created tab.
  - Options:
    - `--url`: Initial URL for the new tab.
    - `--json`: Return JSON result.

- `intuned dev browser tabs close <tab-id>`:
  - Close a tab in the browser by its tab ID.

- `intuned dev browser tabs list [options]`:
  - Return a list of all currently open tabs in the browser. Includes: tab ID, title, and URL.
  - Options:
    - `--json`: Return the result in JSON.
