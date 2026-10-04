# DriverForge

A fault and conformance test kit for Python instrument drivers, with source-linked wire transcripts and pytest integration.

**Status: refined planning repository; implementation has not started.** Start with [requirements and rationale](docs/REQUIREMENTS.md), then [START_HERE.md](START_HERE.md) and the [implementation plan](IMPLEMENTATION_PLAN.md).

Unit conversion, framing, timeout, and uncertain-write errors can invalidate measurements or repeat a hardware action. Testing these explicitly is useful even when no AI-generated driver is involved. This fits Walter's instrument automation and hardware abstraction experience.

Existing tools already cover parts of this problem. M0 must compare them and establish a useful addition or integration. The plan makes no claim of unique invention or practitioner adoption. All software and engineering validation remain pending.

The first release must work without hardware or model credentials. Live AI experiments and physical tests are separate. Commits stay local; publication is not authorized.
