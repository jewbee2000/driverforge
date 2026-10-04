# DriverForge specification

Status: implemented reference contract. M0 selected a PyMeasure-compatible
extension; executed behavior/resource evidence is linked from REQUIREMENTS.md.
These constants describe synthetic profiles, not physical measurements.


## Scope and assumptions

The regression suite contains two deliberately fictional instruments: ThermoBlock T1 using a small line-oriented ASCII protocol, and PressureBrick P1 using a Modbus-style register PDU over an in-memory transport. The manuals are authored for this project and must be labeled fictional. We test function/data encoding; full Modbus TCP transaction framing and serial RTU CRC are outside version 1.

Start with Markdown manuals and explicit source anchors. An optional later extraction stage proposes a typed ProtocolSpec, but it may return an unresolved ambiguity; v1 accepts explicitly authored specifications. The checked-in example ProtocolSpecs are reviewed project fixtures. Do not assume arbitrary PDFs can be interpreted correctly.

## Wire contracts to freeze before implementation

ThermoBlock requests end with LF; CRLF is accepted on responses. `*IDN?` returns `WALT,THERMOBLOCK-T1,0001,1.0`. `MEAS:TEMP?` returns a signed decimal Celsius value such as `-12.34`. `SOUR:VOLT 1.250` is a side-effecting set command; accepted range is 0.000 through 5.000 V inclusive. `OUTP OFF` disables output. Error responses are `ERR,<numeric_code>,<message>`. Limit a response to 256 bytes. Reject nonfinite numbers, unsolicited trailing frames, unrecognized units, and malformed encodings.

PressureBrick uses big-endian 16-bit registers. Register 0x0000 holds signed temperature in 0.01 degrees C; bytes FB 2E represent -1234 counts, therefore -12.34 degrees C. Register 0x0001 holds unsigned pressure in 0.1 kPa. Register 0x0010 holds a 0–5000 mV setpoint; the public driver API accepts volts. PDU function 0x03 reads a single register; 0x06 writes one. A read-temperature request is `03 00 00 00 01`; a response is `03 02 FB 2E`. A 1.250 V write is `06 00 10 04 E2`; successful response must echo it exactly. Exception `83 02` becomes IllegalAddress, not a measurement. These explicit vectors are minimum oracle seeds, not the entire conformance suite.

One transport operation has a 250 ms deadline. An idempotent read may be retried once, within a total 500 ms budget. A write that times out after transmission has an unknown outcome and must not be retried automatically. A fake clock makes deadline tests deterministic. Close is idempotent and prevents subsequent requests. Cancellation closes or drains the transport so old responses cannot satisfy later operations.

## Data and software boundaries

ProtocolSpec includes protocol/version, command name, request grammar or register/function, response schema, units, signedness, scaling, legal range, timeout, retry policy, side-effect class, and source anchor for every field. Missing behavior must be `unresolved`, not a guessed default.

The reference driver's public API is identify(), read_temperature(), read_pressure() where supported, set_voltage(volts), disable_output(), and close(). Unsupported capabilities are explicit. Return measurements with value, unit, sampled_at, received_at, and quality. sampled_at is nullable when the wire protocol does not report acquisition time; do not mislabel host receipt time as physical sampling time. Use typed exceptions for parse errors, deadline exceeded, device errors, unsupported operations, and unknown write outcomes.

Proposed package layout: src/driverforge/{spec,transport,driver,generate,report}, emulators/, manuals/, examples/specs/, tests/unit/, tests/conformance/, evaluation/, docs/, evidence/. The emulator and golden vectors derive from the manual, never the generated driver or a shared codec that could duplicate its bug. Common neutral datatypes are acceptable; shared encoding logic is not.

## Demonstration and outputs

Target command contract, to be implemented: `python -m driverforge demo --offline --output artifacts/demo`. It emits spec.json, candidate.py, conformance.json, report.html, and manifest.json. It exits 0 only if the demonstration observed the intended bad-candidate rejection and the good candidate passed every required check. `python -m driverforge check <driver> --spec <spec>` exits nonzero on violations. These commands are specified interfaces, not existing software in the planning repository.

The report shows source passage → interpreted field → wire bytes → driver result → verdict. It includes at least one failed candidate and one unresolved ambiguity, and clearly labels replay versus live generation.

## Scope exclusions and later work

No arbitrary PDF extraction, real device writes, universal driver generator, enterprise fleet management, or claim of universal Modbus/SCPI compliance. One existing public PyMeasure driver and its injectable adapter are now required by DF-14; additional ecosystems and CAN decoding remain later work. A physical instrument can independently validate one adapter later; its purchase is not a prerequisite.

## Public interface applicability

The numeric protocol limits and driver behaviors in SPEC.md apply to the two fictional reference profiles. Existing upstream drivers are judged against their own explicit supported-operation contracts; the tool must report a real failure without rewriting the upstream driver or disguising it as a pass. A consumer walkthrough may correct a test adapter or an intentionally broken consumer candidate; it must not fabricate a correction to an unresolved upstream bug.

## Acceptance requirements

The authoritative rationale, applicability, and independent acceptance evidence for these requirements are in [REQUIREMENTS.md](REQUIREMENTS.md). Reference-case behavior above does not replace the public-interface requirements.

| ID | Priority | Milestone | Requirement |
| --- | --- | --- | --- |
| DF-01 | must | M0 | ProtocolSpec requires units, scaling, signedness, side effects, retry semantics, and source anchors; unresolved critical fields prevent dependent checks or generation. |
| DF-02 | must | M1 | Two reviewed fictional protocol fixtures have typed reference drivers exposing only supported operations; generation is optional. |
| DF-03 | must | M0 | Signed register and voltage scaling match golden wire vectors exactly. |
| DF-04 | must | M2 | Framing and parsing reject truncated, overlong, nonfinite, malformed, and trailing input. |
| DF-05 | must | M2 | Read retry is bounded; uncertain side-effecting writes are never replayed automatically. |
| DF-06 | must | M2 | Errors, cancellation, and close preserve operation ordering and typed outcomes. |
| DF-07 | must | M2 | The oracle rejects six seeded driver defects. |
| DF-08 | must | M2 | At least 20 conformance cases and 10 missing/contradictory-source cases have explicit decisions; enabled model extraction also receives instruction-injection cases. |
| DF-09 | must | M3 | Offline demo requires neither a model key nor physical I/O and preserves a failed attempt. |
| DF-10 | must | M3 | Generated code cannot edit evaluation inputs or access credentials/network. |
| DF-11 | must | M3 | Reports trace results to protocol source, candidate hash, oracle version, and commands. |
| DF-12 | must | M4 | The public package passes lint, type checks, meaningful tests, and documented installation. |
| DF-13 | must | M0 | Compare a pinned PyMeasure expected_protocol/PyVISA-sim baseline with the proposed fault kit on the same driver operations. |
| DF-14 | must | M1 | Test at least one pinned, real public PyMeasure driver without rewriting its implementation, through an injectable transport adapter. |
| DF-15 | must | M2 | A declarative fault schedule supports timeout, fragmented response, malformed response, device error, and late response after cancellation or timeout. |
| DF-16 | must | M2 | Expose a pytest fixture/API that exercises supported existing-driver adapters without requiring a new hardware abstraction layer. |
| DF-17 | should | M3 | Compare two run reports by operation and requirement with readable byte-level differences. |
| DF-18 | could | M3 | Add manual-to-spec generation and bounded model repair after the deterministic conformance tool works. |
| DF-19 | must | M2 | Publish a versioned input and result schema, stable requirement IDs, public Python API, and a scriptable CLI with clear failure semantics. |
| DF-20 | must | M4 | Declare resource limits and measure repeatable performance for the supported workload in the pinned environment. |
| DF-21 | must | M4 | Keep offline workflows local by default and document dependency, fixture, manual, and example licensing. |
| DF-22 | must | M4 | Demonstrate adoption from a separate clean consumer directory using only the documented public interface. |
