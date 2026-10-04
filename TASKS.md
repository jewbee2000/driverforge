# Implementation tasks

All tasks below are unstarted. The preparation commit contains specifications and editorial drafts, not application code.

- [ ] M0 — Freeze the contract and environment. Evidence: Schema validation and hand arithmetic independently confirm the three seed vectors.
- [ ] M1 — Implement the transport and independent emulator. Evidence: A minimal hand-written driver passes the normal path and lifecycle cases; injected transport faults fail as specified.
- [ ] M2 — Generate and verify candidates. Evidence: Good and deliberately bad drivers produce distinguishable reproducible reports; all six mutations are caught.
- [ ] M3 — Add bounded repair and evaluation. Evidence: Replay produces rejection then success without modifying the oracle; unsupported ambiguity remains unresolved.
- [ ] M4 — Prepare the portfolio release. Evidence: All release requirements pass; post and repository are ready for review but remain local.

Update this file only after checking the milestone evidence. See IMPLEMENTATION_PLAN.md for dependencies and estimates.
