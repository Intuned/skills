# Handling 2FA (TOTP) During Login

> **Collect the secret, not a code.** A 6-digit code expires in ~30s and is single-use, so a stored one is useless on the next run. Store the **secret** and generate a fresh code every login. Never ask the user to type a code into chat.

## Step 1: Ask the user to write down the TOTP secret as a credential

Ask the user to write `otpSecret` field value in `.parameters/auth-sessions/create/default.json`
so now it is stored along other credantail fields like username and password.

## Step 2: Find the OTP field

At the 2FA step, find the OTP input and the verify/submit button. You will generate a code in step 3 and then fill it with `form_input`, codes are only valid ~30s, so have the field ready before generating.

## Step 3: Generate a code

Run the script, it picks the right library for the project automatically (`otpauth` for a Node/TypeScript project, `pyotp` for Python, and an ephemeral `pyotp` run when there's no project yet, e.g. during planning). The secret is read inside the runtime and never touches the command line; the script prints only the 6-digit code.

```bash
/intuned-agent-plugin/skills/auth-sessions/scripts/generate-2fa-code.sh .parameters/auth-sessions/create/default.json
```

Arguments: `[path-to-param.json]` (default `.parameters/auth-sessions/create/default.json`) and an optional `[secret-key]` (default `otpSecret`). The code is valid ~30s, so generate it right before filling it.

> Pass `.parameters/auth-sessions/create/{name}.json` for a named credential set, and a second argument if the secret is stored under a key other than `otpSecret`.

Then fill in the generated code and submit. It should log in.
If it failed to login, try one more time with a fresh token and submit it right away, if it fails then this means that the submitted user token is not valid, ask the user to verify his token and provide a valid token.

## Step 4: Wire generation into `create` (codegen)

The real generation lives **inside** `create` function so it's fresh on every run. The library is imported at runtime there, so `uvx`/`npx` can't replace a real dependency for the `create` code itself. See the per-language guide for the in-code wiring:

- Python: `/intuned-agent-plugin/skills/auth-sessions/resources/python/writing-create-and-check-apis.md`
- TypeScript: `/intuned-agent-plugin/skills/auth-sessions/resources/typescript/writing-create-and-check-apis.md`

## Notes

- The library that will be used in `create` function must be installed, make sure you install it or it ask the Scaffolder subagent to install it. typescript->`otpauth`. python->`pyotp`
- The auth-session localization agent must use the bash script `generate-2fa-code.sh` to generate the code and login. Make sure to prompt it about this when you want to use that subagent.
- The auth-session codegen subagent must use the proper library to generate the otp code.
