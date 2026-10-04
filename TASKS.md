# Implementation tasks

All tasks are unstarted. Check off only after recording executed evidence.

- [ ] M0 — Compare existing tools and freeze contracts. Gate: A concrete use case requires useful additional behavior beyond the baseline; otherwise deliver an integration/examples extension. Three hand-calculated vectors and the public-driver adapter design are documented.
- [ ] M1 — Test an existing driver through one adapter. Gate: The external driver completes three declared operations without source changes. Deadline, device-error, and framing behavior are independently observable.
- [ ] M2 — Package reusable fault tests. Gate: Every seeded defect is detected for its intended reason; the external consumer package runs through the documented public API.
- [ ] M3 — Make failures useful to an engineer. Gate: A failure report identifies the operation, expected behavior, observed bytes, source, and reproduction command.
- [ ] M4 — Verify adoption and prepare the local release. Gate: All applicable Must requirements pass; deferred Should items are explained. No claim of real hardware validation or publication is made.

- [ ] Record dispositions for every Should/Could item and verify Won't claims remain excluded.
- [ ] Complete the independent consumer walkthrough and compare its cost with the baseline.

See IMPLEMENTATION_PLAN.md and docs/REQUIREMENTS.md.
