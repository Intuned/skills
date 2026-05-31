# Critical Points
- [ ] CP1: Navigate to the protected start URL `https://sandbox.intuned.dev/list-auth` and confirm it redirects to the login page for authenticated access.
- [ ] CP2: Enter the provided demo email into the email field on the login form.
- [ ] CP3: Enter the provided demo password into the password field on the login form.
- [ ] CP4: Submit the login form using the visible Sign in control.
- [ ] CP5: After authentication, land on the protected List (Auth) page at `/list-auth/` with the heading `List (Authenticated)` visible.
- [ ] CP6: The authenticated table results are visibly displayed with the expected columns (Id, Name, Supplier Name, Supplier Phone Number, Effective Date, Expiration Date, Contract State).
- [ ] CP7: Extract every row currently shown in the authenticated table into a structured list preserving all visible columns.
- [ ] CP8: Record the final extracted structured list in `final_script_log.txt` so the result is auditable.

# Parameters
- email (str): Login email credential to enter on the sign-in form — from task phrase `sign in with email "demo@email.com"` — default `demo@email.com`
- password (str): Login password credential to enter on the sign-in form — from task phrase `password "DemoUser2024!"` — default `DemoUser2024!`

# Fixed (NOT parameterised)
- start_url: Hard-coded to the task site protected page `https://sandbox.intuned.dev/list-auth` because it is site/task specific.
- site_name_and_selectors: Hard-coded to the Intuned sandbox login form and authenticated table structure because these are implementation details of the target site, not user-varying task inputs.
- run_artifact_layout: Hard-coded to `final_runs/run_<id>/` with screenshots and log files because this is required by the benchmark harness.
