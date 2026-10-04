# DriverForge implementation plan

## Purpose and feasibility

Instrument drivers whose behavior can be checked against the wire protocol.

This is the closest match to Walter's Python test automation, instrument interfaces, typed configuration, and hardware abstraction experience. It creates a compact artifact that another test engineer can audit without needing a lab.

High for the specified two fictional instruments. I can author the manuals, emulator, typed driver interfaces, conformance suite, report, and local demo with minimal guidance. Arbitrary manufacturer PDFs and real instrument validation are later extensions.

45–65 engineering hours is a planning range, not a promise about agent wall-clock time. Expect roughly 30–60 minutes of optional owner review at the specification and final-demo checkpoints; publication and real hardware require separate action.

## The result a visitor should see

A temperature module reports a negative temperature. A generated driver mistakenly decodes the signed register as unsigned. The independent byte-level suite rejects it; a corrected driver passes. An ambiguous write command is rejected rather than guessed.

## Technical approach

Python 3.12, Pydantic, asyncio, Typer, pytest, Hypothesis, Ruff, mypy. Use a small local HTML report initially. FastAPI is optional only after the CLI works. Use synthetic transports first; no serial device, Modbus server on a network, database, or cloud service is required.

The public repository must be useful without live AI. The strongest evidence is a requirement that becomes an independent check, a candidate that fails it, and a justified repair. Do not turn the project into a generic chat interface. Retain the original research's specification, verification, and bounded repair approach while narrowing the first release to something one coding agent can complete.

## M0 Freeze the contract and environment

Work: Create manuals, reviewed specs, requirement matrix, golden vectors, and ambiguity corpus. Select stable package versions that actually install; lock them.

Exit evidence: Schema validation and hand arithmetic independently confirm the three seed vectors.

Requirements: DF-01 DF-03 DF-08. Planning estimate: 6–9 h.


## M1 Implement the transport and independent emulator

Work: Build fake-clock transport, deterministic device state, errors, deadlines, and request transcript recording. Author the oracle before generated code.

Exit evidence: A minimal hand-written driver passes the normal path and lifecycle cases; injected transport faults fail as specified.

Requirements: DF-02 DF-04 DF-05 DF-06. Planning estimate: 10–14 h.


## M2 Generate and verify candidates

Work: Implement typed generation contract, recorded candidate adapter, candidate artifact storage, and isolation runner.

Exit evidence: Good and deliberately bad drivers produce distinguishable reproducible reports; all six mutations are caught.

Requirements: DF-03 DF-07 DF-10. Planning estimate: 10–14 h.


## M3 Add bounded repair and evaluation

Work: Implement allowed tool calls, attempt caps, error taxonomy, checkpoint/resume, and deterministic baseline comparison. Add a live adapter only with credentials and a budget.

Exit evidence: Replay produces rejection then success without modifying the oracle; unsupported ambiguity remains unresolved.

Requirements: DF-01 DF-08 DF-09 DF-11. Planning estimate: 10–15 h.


## M4 Prepare the portfolio release

Work: Finish CLI/report, fresh-install checks, architectural explanation, evidence, and update the blog from measured results.

Exit evidence: All release requirements pass; post and repository are ready for review but remain local.

Requirements: DF-09 DF-11 DF-12. Planning estimate: 9–13 h.


## Model evaluation after the deterministic release

Evaluate both protocol tasks across three independent trials per condition: deterministic template baseline, one-shot live generation, and bounded repair. Use the same manuals and frozen conformance suite. That is six trials per condition, eighteen across all three conditions. Also report the 10 ambiguity/injection cases separately. Publish all failures. The release criterion is complete deterministic conformance and detection of all six mutations; no unmeasured target pass rate for the model is a release claim.

The evaluator's inputs are frozen before the campaign. One-shot and repair runs use the same budgets except for the explicitly reported repair allowance. Capture all attempts; do not discard unsuccessful trials. Separate a replay demonstration from a live model evaluation. These comparisons are project-local experiments, not claims about every AI model or engineering task.

## Risks and fallback decisions

The main risk is a plausible driver and emulator sharing the same semantic error. Separate their codecs, use hand-calculated vectors, and mutate each critical behavior. Real vendor manuals introduce ambiguity and device quirks that this synthetic result cannot establish. If isolation cannot be provisioned, finish the transport, emulator, and conformance tool, and mark live code execution unavailable.

## Owner involvement

No response from Walter is needed for routine naming, data models, fixtures, UI choices, or test implementation within this specification. The agent can define missing synthetic examples and document assumptions. Ask only when a decision would materially change the project's claim or exceed the authorized environment. An optional final review of the first-person article would improve the voice; no invented memory or measured result should be used to avoid that review.

Before any live API campaign, a model adapter, credential, and spending ceiling are needed. None is required for the deterministic product or replay. Physical validation requires Walter to perform or arrange the measurement. Remote publication requires a later instruction because the present instruction forbids pushes.

## Definition of finished

All required behaviors in docs/SPEC.md have independent evidence. The README gives a working fresh-clone setup and offline demo. Artifacts are real, versioned, and labeled by scope. The code, tests, environment lockfile, architecture, evidence, and article are locally committed. A future publication step creates or selects the GitHub repository, pushes the reviewed commits, verifies public links, then publishes the matching website article. Until that later step, remote GitHub and live-site completion remain pending.
