# Public contract v1

Install DriverForge as a small local pytest/library extension. It supplies no new
instrument abstraction required for PyMeasure users. The unchanged upstream
driver receives PyMeasureFaultAdapter via the existing adapter constructor.

Public imports from driverforge: ProtocolSpec, Ambiguity, Measurement,
FaultTransport, FakeClock, Fault, ThermoBlock, PressureBrick, run_campaign,
CampaignResult, CaseResult, asset, reference_cases, factory_for, and typed errors.
driverforge.pymeasure_adapter exposes PyMeasureFaultAdapter and agilent34410a.
driverforge.report exposes write_report and compare_reports. The installed pytest
fixture driverforge_transport is a factory for fresh FaultTransport instances.

Schemas ship in driverforge/schemas: spec-v1.json, campaign-v1.json, result-v1.json
(JSON Schema 2020-12). Unknown versions and extra input keys are rejected.
Critical missing/contradictory spec fields produce structured inconclusive
ambiguities with source anchors and block dependent cases. The three built-in
profiles have fixed reviewed wire semantics: edited scale, units, request, timeout,
or retry fields cannot silently reconfigure those reference drivers. Such checks
are inconclusive. New consumer expected readings and fault schedules are supported
through explicit campaign cases and public local callables; arbitrary vendor
protocol implementation is outside this release.

FaultTransport accepts a mapping from operation name to (exact request bytes,
response bytes or None), and Fault objects with kind, operation, onset (one-based
occurrence), expected_outcome, data_hex/chunks_hex, and delay_ms. It records raw
fragments/terminators, fake timestamps, transmission counts, timeout and discarded
late bytes. Cancellation is a deterministic event during a pending exchange,
closing the transport. This is not an asynchronous serial implementation.

run_campaign(factory, spec, cases) constructs fresh trusted driver instances per
case and compares observed outcomes to explicit expected values in the input.
The oracle computes no expected reading through the driver codec. A separate
frozen open evaluation inventory validates the reference implementation.
The API runs local reviewed Python in the caller process; it is not a sandbox.
The CLI accepts only built-in reviewed candidate names and uses a killable worker.
Generated scripts and import paths are rejected, not executed.

Normal check exits: 0 only when every declared case passes; 1 for contract
violations; 2 for invalid/incomplete/unsupported or crashed execution. Each case
retains pass/fail/inconclusive/not_applicable vocabulary. Unsupported upstream
capabilities appear as not_applicable context, not passing checks. Demo has a
separate gate: both references pass, all six expected negative fixtures fail, and
an unresolved ambiguity is retained. A demo's success does not change a normal
check's failed verdict. Diff exits 0 for unchanged, 1 for differences, 2 for errors.

Limits frozen in M0: 64 KiB JSON inputs, 100 cases, 16 operations, 16 faults/case,
256 response bytes, 250 ms reference exchange, 500 ms total read budget, 4 MiB
reports. CLI worker wall limit is at most 10 seconds. API users must bound their
own blocking callables. Resource evidence measures fresh trusted Windows workers.
Timeouts give an incomplete result; no successful verdict is reused from a
previous run.

Reports use normalized UTF-8/LF JSON for semantic input hashes and copy the
candidate source file. Manifests record candidate, oracle vector, evaluator,
source/manual, lockfile and output hashes, source commit/dirty status (unavailable
outside a checkout), commands and exit status. Data stays local. Spec passages
and driver text are escaped in HTML under a restrictive content security policy.
