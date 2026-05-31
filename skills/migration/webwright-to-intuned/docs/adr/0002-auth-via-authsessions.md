# Auth crafts are ported to Intuned AuthSessions, overriding faithful-port

A Crafted CLI that logs in does so inline (fill credentials, submit, then act).
The faithful-port default (ADR 0001) would keep that login inline inside the
`automation`. For auth, we deliberately override it: a login craft is
**decomposed into Intuned AuthSessions**.

- The login portion becomes `auth-sessions/create.py` (`async def create(page, params)`),
  credentials become create params (default = the task's credentials).
- A `auth-sessions/check.py` (`async def check(page) -> bool`) is derived to
  validate an existing session via a logged-in-only signal.
- `Intuned.jsonc` enables `authSessions`; the `automation` assumes a valid
  session is already applied and only does the post-login work.

This is the one structural re-architecture we accept by default. Rationale:
AuthSessions is Intuned's flagship mechanism for auth — sessions are stored,
revalidated, and reused across runs instead of logging in every time — and a
login craft decomposes into it cleanly (login → `create`, post-login →
`automation`).

Cost we accept: more surface area (create + check + manifest + params) and a
two-step local test (`intuned dev run authsession create '{creds}'` → run the
api with `--auth-session <id>`). The trickiest derived artifact is `check.py`;
its logged-in signal must be verified in the test loop, not assumed.
