# Implementation tasks

Check off only after recording executed evidence. See evidence/progress.md.

- [x] M0 â€” Compare existing tools and freeze contracts. Gate: A concrete use case requires useful additional behavior beyond the baseline; otherwise deliver an integration/examples extension. Three hand-calculated vectors and the public-driver adapter design are documented.
- [x] M1 â€” Test an existing driver through one adapter. Gate: The external driver completes three declared operations without source changes. Deadline, device-error, and framing behavior are independently observable.
- [x] M2 â€” Package reusable fault tests. Gate: Every seeded defect is detected for its intended reason; the external consumer package runs through the documented public API.
- [x] M3 â€” Make failures useful to an engineer. Gate: A failure report identifies the operation, expected behavior, observed bytes, source, and reproduction command.
- [x] M4 â€” Verify adoption and prepare the local release. Gate: All applicable Must requirements pass; deferred Should items are explained. No claim of real hardware validation or publication is made.

- [x] Record dispositions for every Should/Could item and verify Won't claims remain excluded.
- [x] Complete the independent consumer walkthrough and compare its cost with the baseline.

See IMPLEMENTATION_PLAN.md and docs/REQUIREMENTS.md.
