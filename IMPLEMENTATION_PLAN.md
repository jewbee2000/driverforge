# DriverForge implementation plan

Revised 2026-10-04. Begin with [requirements and rationale](docs/REQUIREMENTS.md). The previous all-features-at-once plan is superseded by this useful-core-first sequence. Application implementation has not started.

## Purpose and feasibility

A fault and conformance test kit for Python instrument drivers, with source-linked wire transcripts and pytest integration. Unit conversion, framing, timeout, and uncertain-write errors can invalidate measurements or repeat a hardware action. Testing these explicitly is useful even when no AI-generated driver is involved. This fits Walter's instrument automation and hardware abstraction experience.

The proposed contribution is a reusable fault campaign with explicit retry and unknown-outcome semantics, exact byte evidence, and a small adapter for an existing driver. Whether this saves work compared with ordinary PyMeasure tests must be demonstrated in M0. Confidence: medium; strongest of the three for a near-term useful release.

50–80 engineering hours as an initial planning range, to revise after M0. The public-driver integration is a release requirement; live model generation is optional.

Core software can be built with minimal owner guidance, but novelty and adoption are not established. Use existing libraries and routine design judgment. Do not require physical measurements to finish a software release; do not claim those measurements occurred.

## Build sequence

### M0 Compare existing tools and freeze contracts

Work: Run the baseline comparison; select the public driver and lawful source material. Freeze protocol schemas, independent golden vectors, applicability rules, and the fault matrix.

Exit evidence: A concrete use case requires useful additional behavior beyond the baseline; otherwise deliver an integration/examples extension. Three hand-calculated vectors and the public-driver adapter design are documented.

Primary requirements: DF-01 DF-03 DF-13. All earlier contracts remain regression requirements.

### M1 Test an existing driver through one adapter

Work: Build minimal transport, fake clock, transcript capture, and reference drivers; exercise the public driver before generation features.

Exit evidence: The external driver completes three declared operations without source changes. Deadline, device-error, and framing behavior are independently observable.

Primary requirements: DF-02 DF-14. All earlier contracts remain regression requirements.

### M2 Package reusable fault tests

Work: Build fault schedules, pytest fixture, independent oracle, six mutations, and machine-readable verdicts.

Exit evidence: Every seeded defect is detected for its intended reason; the external consumer package runs through the documented public API.

Primary requirements: DF-04 DF-05 DF-06 DF-07 DF-08 DF-15 DF-16 DF-19. All earlier contracts remain regression requirements.

### M3 Make failures useful to an engineer

Work: Create source-to-byte HTML reports and optional report comparison. Preserve rejected attempts. Treat live model generation as a separate optional experiment.

Exit evidence: A failure report identifies the operation, expected behavior, observed bytes, source, and reproduction command.

Primary requirements: DF-09 DF-10 DF-11 DF-17 DF-18. All earlier contracts remain regression requirements.

### M4 Verify adoption and prepare the local release

Work: Run fresh-install consumer checks, resource limits, input privacy/license checks, lint/types/tests, and the offline demo. Update the draft from observed evidence.

Exit evidence: All applicable Must requirements pass; deferred Should items are explained. No claim of real hardware validation or publication is made.

Primary requirements: DF-12 DF-20 DF-21 DF-22. All earlier contracts remain regression requirements.

## Method and dependencies

Use Python with a repository-local pinned environment; select compatible versions during M0. Read SPEC.md for existing reference-case constants. Requirements proceed M0 → M1 → M2 → M3 → M4; the machine-readable register identifies primary milestones and baseline dependencies. Tests and documentation evolve with each slice rather than accumulating at the end.

For every nontrivial feature: state the requirement, write an independent failing check, implement the smallest slice, inspect actual output, record evidence, and commit locally. Preserve known failures and explain repairs. A product model, elaborate UI, web service, or paid API is not needed for the useful first release. Reuse primary-source libraries after verifying current installation and capabilities.

## Model evaluation after the deterministic release


Evaluate both protocol tasks across three independent trials per condition: deterministic template baseline, one-shot live generation, and bounded repair. Use the same manuals and frozen conformance suite. That is six trials per condition, eighteen across all three conditions. Also report the 10 ambiguity/injection cases separately. Publish all failures. The release criterion is complete deterministic conformance and detection of all six mutations; no unmeasured target pass rate for the model is a release claim.

The evaluator's inputs are frozen before the campaign. One-shot and repair runs use the same budgets except for the explicitly reported repair allowance. Capture all attempts; do not discard unsuccessful trials. Separate a replay demonstration from a live model evaluation. These comparisons are project-local experiments, not claims about every AI model or engineering task.

## Risks and decision rules

The largest product risk is duplicating existing software or building a demonstration that accepts only its own fixtures. The M0 comparison and M4 independent consumer walkthrough are release gates. Prefer a narrow library/plugin when it satisfies the same needs. Do not silently drop external integration in order to finish a more impressive-looking demo.

If a technical dependency or required semantic cannot be implemented, record it as blocked or unsupported and do not label the release complete. If the entire useful contribution disappears after the baseline comparison, stop broad implementation and report the concrete result; do not invent novelty or ask for routine design approvals.

## Owner involvement and publication

No owner guidance is needed for routine architecture, naming, examples, or tests within these requirements. Physical tests, paid live model campaigns, and remote publication require separate resources or authorization. Do not contact maintainers or prospective users automatically. No pushes, deployment, or remote commits. Local commits are authorized.

## Definition of finished

All applicable Must requirements have independent executed evidence. Should/Could omissions and Won't scope are explicit. A clean consumer walkthrough works on a non-default input, and reports show a real detected failure and repair. The first-person article is updated only from observed work, remains unpublished, and has no invented anecdotes, physical measurements, or live-model scores. Hosted repositories and website publication remain pending a later instruction.
