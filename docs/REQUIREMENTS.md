# DriverForge requirements and rationale

Revision 2026-10-04. Status: planned, not implemented. This audit supersedes the earlier unprioritized feature list. [requirements.json](../requirements.json) is the machine-readable register; [SPEC.md](SPEC.md) supplies detailed reference-case constants and contracts. Keep them synchronized.

## Purpose and practical value

A fault and conformance test kit for Python instrument drivers, with source-linked wire transcripts and pytest integration.

**Intended user:** A test engineer adding or changing a driver for a bench instrument, especially when the instrument is unavailable in CI.

**Job to be done:** Connect an existing driver through a small adapter, declare the supported protocol behavior, inject broken or delayed responses, and get an actionable regression report.

**Why it matters:** Unit conversion, framing, timeout, and uncertain-write errors can invalidate measurements or repeat a hardware action. Testing these explicitly is useful even when no AI-generated driver is involved. This fits Walter's instrument automation and hardware abstraction experience.

## Existing tools and the proposed contribution

PyMeasure already has expected_protocol tests and a test Generator; QCoDeS documents PyVISA simulation; instrbuilder already generates SCPI drivers from command metadata. Driver generation and fake instruments are not novel. PyMeasure issue 1081 provides a concrete example of a user struggling to inspect the exact bytes behind an instrument error; it does not establish the root cause or prove this proposed tool would fix it.

The proposed contribution is a reusable fault campaign with explicit retry and unknown-outcome semantics, exact byte evidence, and a small adapter for an existing driver. Whether this saves work compared with ordinary PyMeasure tests must be demonstrated in M0. Confidence: medium; strongest of the three for a near-term useful release.

Research checked on 2026-10-04. This is a bounded comparison of public documentation and selected source code, not proof that no competing tool exists. No interviews, field deployments, or independent user adoption have been conducted. Do not claim industry validation or unique invention. A useful integration or plugin is an acceptable outcome.

- [PyMeasure protocol tests and Generator](https://pymeasure.readthedocs.io/en/stable/dev/adding_instruments/tests.html)
- [QCoDeS simulated instruments](https://microsoft.github.io/Qcodes/examples/writing_drivers/Creating-Simulated-PyVISA-Instruments.html)
- [PyVISA simulation](https://pyvisa.readthedocs.io/projects/pyvisa-sim/en/latest/)
- [instrbuilder](https://github.com/lucask07/instrbuilder)
- [PyMeasure exact-byte debugging issue 1081](https://github.com/pymeasure/pymeasure/issues/1081)
- [QCoDeS testing without hardware discussion](https://github.com/microsoft/Qcodes/discussions/6237)

## Priorities and release policy

Must means release blocking for its stated applicability. Should is valuable but can be deferred with a written reason. Could is optional and must not delay a useful core. Won't means excluded from v1. Conditional Must requirements do not force an optional feature into the release; if that feature is enabled, its checks are mandatory.

M0 must establish a concrete gap or a useful integration before broad implementation. If the baseline already solves the chosen workflow, deliver the smallest reusable extension/examples package and document that choice. Do not pad scope to preserve the project name. Keep all required evidence and explain any revised requirement before implementing it.

Requirements are proposed engineering decisions, not discovered industry standards. The sample thresholds in SPEC.md are explicit reference-case choices. Users must be able to state their own contracts where the public interface supports them.

## Reference profiles and external inputs

The numeric protocol limits and driver behaviors in SPEC.md apply to the two fictional reference profiles. Existing upstream drivers are judged against their own explicit supported-operation contracts; the tool must report a real failure without rewriting the upstream driver or disguising it as a pass. A consumer walkthrough may correct a test adapter or an intentionally broken consumer candidate; it must not fabricate a correction to an unresolved upstream bug.

## Requirement register
### DF-01 — Must — M0

ProtocolSpec requires units, scaling, signedness, side effects, retry semantics, and source anchors; unresolved critical fields prevent dependent checks or generation.

**Rationale:** A plausible guess about scaling or side effects is worse than an explicit unsupported field.

**Acceptance:** Feed missing and contradictory fields; verify a structured ambiguity with cited source anchors.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_spec_validation.py`. **Status:** not implemented.

### DF-02 — Must — M1

Two reviewed fictional protocol fixtures have typed reference drivers exposing only supported operations; generation is optional.

**Rationale:** Two deliberately different protocols expose ASCII and register assumptions without claiming broad device support.

**Acceptance:** Compare reference API and annotations to capability lists; unsupported operations have explicit outcomes. Use hand-authored or checked-in candidates for the offline demo.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_capabilities.py`. **Status:** not implemented.

### DF-03 — Must — M0

Signed register and voltage scaling match golden wire vectors exactly.

**Rationale:** Independent constants expose signedness and unit errors that a driver and emulator could otherwise share.

**Acceptance:** Check FB2E → -12.34 C and 1.250 V → 04E2 against hand-calculated constants.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_golden_bytes.py`. **Status:** not implemented.

### DF-04 — Must — M2

Framing and parsing reject truncated, overlong, nonfinite, malformed, and trailing input.

**Rationale:** Malformed traffic must not become a plausible measurement.

**Acceptance:** Inject each malformed response without calling production parsers in the oracle.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_hostile_frames.py`. **Status:** not implemented.

### DF-05 — Must — M2

Read retry is bounded; uncertain side-effecting writes are never replayed automatically.

**Rationale:** A lost acknowledgment does not prove a write failed; replaying it may repeat an action.

**Acceptance:** Fake clock and counted transport prove two maximum read attempts and one write.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_retry_semantics.py`. **Status:** not implemented.

### DF-06 — Must — M2

Errors, cancellation, and close preserve operation ordering and typed outcomes.

**Rationale:** Late responses and cancellation are common ways to associate a valid value with the wrong request.

**Acceptance:** Cancel a pending read then attempt another; no stale response can be reused. Close twice.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_lifecycle.py`. **Status:** not implemented.

### DF-07 — Must — M2

The oracle rejects six seeded driver defects.

**Rationale:** A suite that accepts known defects is not credible evidence of conformance.

**Acceptance:** Unsigned decode, factor-of-1000 voltage, swapped bytes, blind write retry, swallowed device error, stale response reuse each fail at least one assertion.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_mutation_detection.py`. **Status:** not implemented.

### DF-08 — Must — M2

At least 20 conformance cases and 10 missing/contradictory-source cases have explicit decisions; enabled model extraction also receives instruction-injection cases.

**Rationale:** Coverage must include decisions to abstain, not just normal command responses.

**Acceptance:** A manifest enumerates cases and expected decisions; source text cannot alter evaluator rules or run shell commands.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_case_inventory.py`. **Status:** not implemented.

### DF-09 — Must — M3

Offline demo requires neither a model key nor physical I/O and preserves a failed attempt.

**Rationale:** A test engineer should be able to evaluate the tool without buying a device or model subscription.

**Acceptance:** Run with credentials absent and network disabled; inspect manifest and failure report.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_offline_demo.py`. **Status:** not implemented.

### DF-10 — Must — M3

Generated code cannot edit evaluation inputs or access credentials/network.

**Rationale:** Optional candidate execution cannot be allowed to alter the evidence used to judge it.

**Acceptance:** Isolation tests attempt forbidden writes and egress and hit the timeout limit; report unavailable isolation as blocked.

**Applies:** Only when executing untrusted generated code; unavailable isolation disables this feature, not the core test kit. **Planned evidence:** `tests/acceptance/test_isolation.py`. **Status:** not implemented.

### DF-11 — Must — M3

Reports trace results to protocol source, candidate hash, oracle version, and commands.

**Rationale:** Engineers need to see the actual bytes and requirement behind a verdict to debug a failure.

**Acceptance:** Verify artifact hashes and recompute expected output from a fresh checkout.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_provenance.py`. **Status:** not implemented.

### DF-12 — Must — M4

The public package passes lint, type checks, meaningful tests, and documented installation.

**Rationale:** An installable maintained package is more useful than a notebook tied to its author's machine.

**Acceptance:** Fresh environment follows README and repeats the offline demonstration.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_reproducibility.py`. **Status:** not implemented.

### DF-13 — Must — M0

Compare a pinned PyMeasure expected_protocol/PyVISA-sim baseline with the proposed fault kit on the same driver operations.

**Rationale:** Existing tools already cover normal protocol testing; duplication is not a useful portfolio result.

**Acceptance:** Record setup steps, handwritten adapter/test code size, supported fault cases, and missing semantics in docs/BASELINE.md. If the baseline meets all needs, implement a small compatible extension or examples package instead of a new driver framework.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_baseline_artifacts.py`. **Status:** not implemented.

### DF-14 — Must — M1

Test at least one pinned, real public PyMeasure driver without rewriting its implementation, through an injectable transport adapter.

**Rationale:** The original fictional devices alone did not demonstrate adoption by an existing engineering codebase.

**Acceptance:** M0 chooses a redistributable public driver and cites its commit plus public protocol documentation. Exercise at least three operations and three distinct fault cases; save exact requests and responses. Do not label the result physical validation or a reproduced upstream bug without matching evidence.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_existing_driver_adapter.py`. **Status:** not implemented.

### DF-15 — Must — M2

A declarative fault schedule supports timeout, fragmented response, malformed response, device error, and late response after cancellation or timeout.

**Rationale:** Repeatable negative cases are the main added value over a canned happy-path emulator.

**Acceptance:** Each fault has onset, affected operation, expected outcome, and deterministic transcript. The adapter reports unsupported capabilities explicitly; upstream synchronous APIs need not pretend to support async cancellation.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_fault_schedule.py`. **Status:** not implemented.

### DF-16 — Must — M2

Expose a pytest fixture/API that exercises supported existing-driver adapters without requiring a new hardware abstraction layer.

**Rationale:** Requiring a driver rewrite would erase most of the adoption benefit.

**Acceptance:** A separate consumer package runs a driver conformance test using only public APIs. Its upstream source remains unchanged; unsupported framing or retry behaviors are reported rather than silently treated as tested.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_pytest_consumer.py`. **Status:** not implemented.

### DF-17 — Should — M3

Compare two run reports by operation and requirement with readable byte-level differences.

**Rationale:** A comparison makes driver and dependency upgrades easier to review.

**Acceptance:** A single changed terminator, scale, and retry count each produce a specific diff; unchanged data produce no regression.

**Applies:** If selected after Must requirements pass **Planned evidence:** `tests/acceptance/test_report_diff.py`. **Status:** not implemented.

### DF-18 — Could — M3

Add manual-to-spec generation and bounded model repair after the deterministic conformance tool works.

**Rationale:** Agent-assisted development already demonstrates the intended portfolio skill; a product model is optional.

**Acceptance:** Any enabled experiment retains all attempts, freezes the oracle first, uses at most three repair attempts by default, and labels replay separately from live evaluation. No credentials or API budget means this experiment is not run.

**Applies:** If selected after Must requirements pass **Planned evidence:** `tests/acceptance/test_optional_generation.py`. **Status:** not implemented.

### DF-19 — Must — M2

Publish a versioned input and result schema, stable requirement IDs, public Python API, and a scriptable CLI with clear failure semantics.

**Rationale:** CI must not confuse an unsupported check or crashed evaluator with a valid result.

**Acceptance:** For normal check commands: exit 0 only when every applicable required check passes; exit 1 for violations; exit 2 for invalid, incomplete, unsupported, or failed execution. Results preserve individual pass/fail/inconclusive/not_applicable states. The demo command separately verifies its expected negative cases. Unknown schema versions are rejected.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_public_contract.py`. **Status:** not implemented.

### DF-20 — Must — M4

Declare resource limits and measure repeatable performance for the supported workload in the pinned environment.

**Rationale:** A tool that hangs or silently drops large input cannot be trusted in an engineering workflow.

**Acceptance:** During M0 freeze input-size/case limits and a target runtime with machine details. M4 records actual elapsed time and peak memory; an oversized input or elapsed-time limit produces a bounded error and incomplete result. CAD work runs in a killable worker. Compare against the baseline; do not claim universal performance.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_resource_limits.py`. **Status:** not implemented.

### DF-21 — Must — M4

Keep offline workflows local by default and document dependency, fixture, manual, and example licensing.

**Rationale:** Engineers must be able to inspect data handling and legally reuse the code and examples.

**Acceptance:** No credentials or telemetry are needed; the offline demo completes with egress disabled after installation. Source examples have provenance and redistributable licenses, or use a download recipe and lawful independently authored fixtures. Escape user text in HTML; reject output path traversal and avoid executing input data.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_data_and_license_boundaries.py`. **Status:** not implemented.

### DF-22 — Must — M4

Demonstrate adoption from a separate clean consumer directory using only the documented public interface.

**Rationale:** A successful bundled demo alone is not evidence that another engineer can use the tool.

**Acceptance:** Record a complete cold-start walkthrough: install, configure one non-default input, get an expected failure, correct it, and reproduce success without editing package source. Include actual commands, setup time, code/config size, and limitations versus the baseline. Label agent-executed walkthroughs as such; practitioner validation remains unverified until real feedback exists.

**Applies:** Core v1 release **Planned evidence:** `tests/acceptance/test_consumer_walkthrough.py`. **Status:** not implemented.

## Explicit scope exclusions

### DF-W01 — Won't have in v1

**Universal PDF-to-driver generation.** Manufacturer prose and undocumented behavior cannot be validated reliably from a small benchmark.

Verification: Absent from the v1 supported-features list; README and reports do not claim this capability.

### DF-W02 — Won't have in v1

**A replacement for PyMeasure, QCoDeS, PyVISA, or a hardware abstraction platform.** Integrating one ecosystem is feasible and lowers adoption cost.

Verification: Absent from the v1 supported-features list; README and reports do not claim this capability.

### DF-W03 — Won't have in v1

**Automatic discovery or writes to real instruments.** The first release is an offline test tool; real-device behavior needs a separately reviewed setup.

Verification: Absent from the v1 supported-features list; README and reports do not claim this capability.

### DF-W04 — Won't have in v1

**Full Modbus TCP/RTU stack, every vendor, or universal SCPI compliance.** The register example checks PDU semantics only; transport standards and vendor coverage require additional evidence.

Verification: Absent from the v1 supported-features list; README and reports do not claim this capability.

### DF-W05 — Won't have in v1

**Claims that emulator conformance proves physical accuracy or instrument safety.** Physical calibration, hardware quirks, and safe operating limits are outside software simulation.

Verification: Absent from the v1 supported-features list; README and reports do not claim this capability.

## Completion and actual usefulness

Technical readiness requires passing evidence for every applicable Must requirement, explicit dispositions for Should items, a negative-case demonstration, a clean installation, and an external consumer example. A failing or inconclusive required check blocks a successful result. All planned test paths above are future work.

Practical usefulness is a separate hypothesis. Record the baseline comparison and the consumer walkthrough, including friction and limitations. A later independent engineer using the tool on their own driver, trace, or CAD assembly would be stronger evidence. Do not contact anyone or fabricate that validation. The first release may honestly be described as a useful candidate tool with demonstrated workflows, not a field-proven industry standard.

Retain the agentic workflow: commit the contract and independent oracle before candidate repair; make small reviewable changes; inject known defects; preserve failed attempts and environment hashes. Product AI features are optional. Development history and reproducible engineering checks are the primary portfolio evidence. No pushes, deployment, paid APIs, or hardware purchases are authorized by this plan.
