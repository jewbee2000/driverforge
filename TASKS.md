# Implementation tasks

All authorized deterministic milestones are complete. Executed commands, failures,
hashes and limitations are in evidence/progress.md and evidence/requirements-evidence.json.

- [x] M0 — Compare existing tools and freeze contracts. A bounded existing-tool comparison justified a PyMeasure-compatible extension; golden vectors and the adapter design are documented.
- [x] M1 — Test an existing driver through one adapter. The unchanged public driver completes three declared operations; deadline, device-error and framing behavior are independently observable.
- [x] M2 — Package reusable fault tests. All six seeded defects are detected; a separate consumer uses the documented public API and installed pytest fixture.
- [x] M3 — Make failures useful to an engineer. Source-linked reports preserve expected behavior, observed bytes, candidate/oracle hashes, reproduction commands and rejected attempts.
- [x] M4 — Verify adoption and prepare the local release. All applicable Must checks pass in a clean checkout; installation, resource bounds, data handling and the unpublished draft were verified.

- [x] Record Should/Could dispositions and verify Won't exclusions. DF-17 is implemented; DF-18 is deferred; DF-10 is not applicable with untrusted execution disabled.
- [x] Complete the independent consumer walkthrough and compare its cost with the baseline. This is agent-executed adoption evidence; practitioner feedback is unverified.
- [x] Publish the project to GitHub under the later authorization, with remote commit and public visibility verified in evidence/github-publication.json. Keep the website checkout unpushed.

Known upstream malformed/device-error failures remain failed. Physical validation,
live models and hostile-code isolation were not performed. Project GitHub publication
was separately authorized on 2026-10-04; the article remains unpublished.

Follow-up work is proposed in docs/NEXT_STEPS.md, outside the completed M0–M4 scope:

- [x] Automate the supported Windows/Python 3.12 checks in CI. PR #1 and hosted run 37231475370 passed all checks; evidence/ci retains the initial setup failure, correction, JUnit and inspected artifact hashes.
- [ ] Obtain a practitioner walkthrough and exercise a second existing driver.
- [ ] Resolve the integration contract's malformed/device-error semantics with source evidence.
- [ ] Validate a read-only operation on available hardware if access is arranged.
