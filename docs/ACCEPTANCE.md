# Acceptance and evidence plan

This is a test design, not a report of passing tests. The concrete contracts and thresholds are in [SPEC.md](SPEC.md). Machine-readable traceability is in [requirements.json](../requirements.json). Every listed test path is planned and must be created during implementation.

| ID | Required behavior | Independent acceptance evidence |
| --- | --- | --- |
| DF-01 | ProtocolSpec requires units, scaling, signedness, side effects, retry semantics, and source anchors; unresolved critical fields prevent generation. | Feed missing and contradictory fields; verify a structured ambiguity with cited source anchors. |
| DF-02 | The two reviewed fictional manuals and specs produce typed drivers with only supported operations. | Compare generated API and annotations to capability lists; unsupported operation raises the named exception. |
| DF-03 | Signed register and voltage scaling match golden wire vectors exactly. | Check FB2E → -12.34 C and 1.250 V → 04E2 against hand-calculated constants. |
| DF-04 | Framing and parsing reject truncated, overlong, nonfinite, malformed, and trailing input. | Inject each malformed response without calling production parsers in the oracle. |
| DF-05 | Read retry is bounded; uncertain side-effecting writes are never replayed automatically. | Fake clock and counted transport prove two maximum read attempts and one write. |
| DF-06 | Errors, cancellation, and close preserve operation ordering and typed outcomes. | Cancel a pending read then attempt another; no stale response can be reused. Close twice. |
| DF-07 | The oracle rejects six seeded driver defects. | Unsigned decode, factor-of-1000 voltage, swapped bytes, blind write retry, swallowed device error, stale response reuse each fail at least one assertion. |
| DF-08 | At least 20 conformance cases and 10 ambiguity or instruction-injection cases exist. | A manifest enumerates cases and expected decisions; source text cannot alter evaluator rules or run shell commands. |
| DF-09 | Offline demo requires neither a model key nor physical I/O and preserves a failed attempt. | Run with credentials absent and network disabled; inspect manifest and failure report. |
| DF-10 | Generated code cannot edit evaluation inputs or access credentials/network. | Isolation tests attempt forbidden writes and egress and hit the timeout limit; report unavailable isolation as blocked. |
| DF-11 | Reports trace results to protocol source, candidate hash, oracle version, and commands. | Verify artifact hashes and recompute expected output from a fresh checkout. |
| DF-12 | The public package passes lint, type checks, meaningful tests, and documented installation. | Fresh environment follows README and repeats the offline demonstration. |

## Test layers

Use schema tests for input constraints; deterministic unit and contract tests for semantics; property/stateful tests for combinations; mutation tests for whether the oracle catches wrong implementations; and one end-to-end offline demonstration for packaging and artifact integrity. Avoid test counts as a proxy for engineering quality. Every seeded critical defect must be caught for an identified behavioral reason.

Expected values must come from the written contract, hand arithmetic, independent geometry inspection, or explicit state tables. Do not compute expected output by invoking the implementation under test. Freeze the oracle and case inventory in a distinct commit before the product-agent experiment.

## Required release evidence

Provide a manifest with commit and dirty-tree hash, environment lock hash, requirement IDs, input hashes, oracle hash, actual commands, exit codes, artifact hashes, and known limitations. Record cases as pass, fail, blocked, or not run. Supply a readable report and a representative negative example. Do not ship a prewritten passing result in place of running tests.

Target validation after implementation: formatter/linter, strict type check on core modules, pytest with relevant property tests, and the documented offline demo. Add a CI workflow only when its commands work locally; do not add decorative green badges before a real run.
