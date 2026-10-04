# Progress

## 2026-10-04 M2/M3 fault kit and report milestone

Installed public pytest fixture/API and versioned input/result schemas. CLI
contracts: check 0/1/2 for success/violations/incomplete; built-in candidates only,
killable trusted worker; generated scripts rejected. All six scheduled fault types
have deterministic traces. Added bounded resource/data checks and report diff.
Checks: ruff check and format --check pass; mypy passes; pytest 93 passed / one
fresh-install evidence test deliberately deselected while its run is pending.
This is not yet an all-checks release claim. Two Hypothesis domain checks ran 100
examples each; source injection stays inert data. Credentials-free/socket-audit
denied demo passed; denial itself was verified. No OS sandbox is claimed.

The first separate consumer venv installed the wheel from --no-index cached
dependencies, failed at 2500 V versus expected 2.5, then passed after config factor
1000 -> 1. Source hashes remained unchanged. First setup duration 58.771 s; reports
and actual commands retained in evidence/consumer. A final formatted wheel run is
pending. Three fresh worker measurements each for baseline/core/upstream passed
the frozen 10 s / 256 MiB limits (evidence/performance.json); different workloads
are explicitly not a speedup comparison. Inspected source/bytes in HTML with the
in-app browser and saved evidence/signed-failure.png.

Corrected cross-checkout evidence serialization: fixtures now force UTF-8/LF and
.gitattributes fixes EOL. Parsed expected values were unchanged; only serialization
hashes were regenerated. No candidate was repaired by changing expected outcomes.
Licensing inventory covers 42 pinned distributions. M2/M3 gates met. Next: final
clean checkout installation, full checks, updated unpublished article and M4 evidence.

## 2026-10-04 M0/M1 vertical slice

Implemented explicit ProtocolSpec schema and source-linked ambiguity outcomes;
11 independent missing/contradictory cases and unknown-version checks pass.
Built trusted typed fictional references, counted in-memory fault transport and
fake clock, plus an adapter for the existing PyMeasure driver. Installed upstream
source hash matches raw pinned commit (evidence/upstream.json); no modifications.
Commands: `python -m pytest -q` exit 0, 61 passed (one upstream SCPI FutureWarning).
`python -m mypy` exit 0 after explicit type repairs. Golden bytes passed exactly.
`python -m driverforge demo --offline --output artifacts/demo` exit 0: 39 reference
cases, six rejected mutations. Inspected unsigned failure: expected -12.34,
observed 643.02, request 0300000001, response 0302fb2e.
`python -m driverforge check agilent34410a --spec examples/specs/agilent34410a.json
--output artifacts/agilent` exit 1 as intended: six cases pass, malformed and
synthetic device-error cases fail. Cancellation/framing/retry limitations remain
explicit. No upstream repair or physical reproduction claimed. M0/M1 gates met.
Next: harden public failure semantics, resource/data boundaries, package consumer,
and fresh-install release evidence before checking M2–M4.

## 2026-10-04 implementation — contract/oracle milestone

Read all working agreements, requirements, spec, acceptance plan, implementation
plan, agent workflow, tasks and blog handoff. Environment: Python 3.12.2 (py -3.12),
Windows 11 Home 10.0.26300, i9-11900H, 16 logical CPUs, 64 GiB installed RAM.
Created `.venv`; pip installed compatible dependencies and `pip check` passed.
Pinned observed versions in requirements.lock. Git ownership mismatch is handled
with per-command `-c safe.directory=<this repository>`; no global Git change.
Docker 28.0.4 CLI exists; daemon unavailable. Untrusted execution remains disabled.

Commands executed: `python examples/baseline/run_baseline.py` exit 0, both existing
tools passed the same three operations; malformed text outcome retained.
`python tools/author_contracts.py` exit 0 froze literal vectors and case inventory.
`pytest tests/acceptance/test_golden_bytes.py -q` exit 2 as expected before package
implementation (import missing). Initial setup failure retained in initial_failures.md.
Bounded comparison justifies a small PyMeasure-compatible extension, not a new
hardware abstraction framework. Limits and hand calculations in docs/DECISIONS.md.
Next: implement validated spec and the smallest reference/public-driver slice.

2026-10-03 — Preparation only. Requirements, acceptance designs, milestones, agent guidance, and unpublished article draft created. Application code, executable acceptance tests, model campaigns, and physical validation have not been implemented or run. Next task: M0 in IMPLEMENTATION_PLAN.md.

## 2026-10-04 requirements audit

Added explicit Must/Should/Could/Won't priorities, per-requirement rationale and acceptance, existing-tool evidence, M0 differentiation gate, and external consumer release criteria. No application implementation or tests were run. All application requirements remain not implemented.

Planning verification: work/verify_project_packages.py checked unique IDs, priorities, nonempty rationale and acceptance, valid dependency references, milestone/spec mapping, local document links, unchanged unpublished website draft status, and absent project remotes. git diff --check passed. Space plan readback verified all 22 requirement IDs and five exclusions under the correct parent. These checks validate documentation consistency, not application behavior.
