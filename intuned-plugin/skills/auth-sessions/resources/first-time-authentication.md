# Handling First Time Authentication

This guide explains how to log in when auth session APIs (`create`/`check`) are not ready yet.

## Step 1: Check for Stored Credentials

Always check for stored credentials first. Run the `auth-sessions` skill's bundled `scripts/list-credentials.sh` (path relative to that skill's directory; run from the project root):

```bash
scripts/list-credentials.sh
```

- If it returns field names (e.g. `username`, `password`) → skip to **Step 3**, credentials are ready.
- If it returns empty → proceed to **Step 2**.

## Step 2: Collect Credentials

**Don't ask the user to type credentials into the chat — you must never see the secret values.** Instead, write the parameter file yourself with the login form's field names and **empty placeholder values**, then ask the user to open that file and fill in the real values directly.

Write `.parameters/auth-sessions/create/default.json` with empty values:

```json
{
  "username": "",
  "password": ""
}
```

Then tell the user something like: "I've created `.parameters/auth-sessions/create/default.json` with the fields it needs — open it and fill in your values. Don't paste them here; I won't read the file." **Wait for them to confirm they've filled it** before continuing, and do not read the file back.

Rules:
- Set this up once. If the file already exists with the right fields, assume the user filled it (you can't see the values) — don't recreate it. Only re-ask if a run actually fails on authentication.
- Match the field names to what the `auth-sessions/create` API expects as its input parameters.
- For projects with multiple logins, use a different file name (e.g. `.parameters/auth-sessions/create/admin.json`). Default is `default.json`.
- Treat these files as sensitive — don't echo their contents back to the user.

## Step 3: Log In Using Stored Credentials

Navigate to the login page, fill the form using `form_input` with `auth_param`, and submit:

```
form_input(element_id="...", tab_id="...", auth_param="username")
form_input(element_id="...", tab_id="...", auth_param="password")
```

- Never use literal credential values. Always use `auth_param`.
- Confirm you reach the authenticated state after submitting.
- If the website is already logged in, proceed normally.
