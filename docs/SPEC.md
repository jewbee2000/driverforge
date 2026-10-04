# DriverForge specification

Status: implementation-ready proposal. No implementation or benchmark results are claimed.


## Scope and assumptions

Version 1 supports two deliberately fictional instruments: ThermoBlock T1 using a small line-oriented ASCII protocol, and PressureBrick P1 using a Modbus-style register PDU over an in-memory transport. The manuals are authored for this project and must be labeled fictional. We test function/data encoding; full Modbus TCP transaction framing and serial RTU CRC are outside version 1.

Start with Markdown manuals and explicit source anchors. An extraction stage proposes a typed ProtocolSpec, but it may return an unresolved ambiguity. The checked-in example ProtocolSpecs are reviewed project fixtures. Do not assume arbitrary PDFs can be interpreted correctly.

## Wire contracts to freeze before implementation

ThermoBlock requests end with LF; CRLF is accepted on responses. `*IDN?` returns `WALT,THERMOBLOCK-T1,0001,1.0`. `MEAS:TEMP?` returns a signed decimal Celsius value such as `-12.34`. `SOUR:VOLT 1.250` is a side-effecting set command; accepted range is 0.000 through 5.000 V inclusive. `OUTP OFF` disables output. Error responses are `ERR,<numeric_code>,<message>`. Limit a response to 256 bytes. Reject nonfinite numbers, unsolicited trailing frames, unrecognized units, and malformed encodings.

PressureBrick uses big-endian 16-bit registers. Register 0x0000 holds signed temperature in 0.01 degrees C; bytes FB 2E represent -1234 counts, therefore -12.34 degrees C. Register 0x0001 holds unsigned pressure in 0.1 kPa. Register 0x0010 holds a 0–5000 mV setpoint; the public driver API accepts volts. PDU function 0x03 reads a single register; 0x06 writes one. A read-temperature request is `03 00 00 00 01`; a response is `03 02 FB 2E`. A 1.250 V write is `06 00 10 04 E2`; successful response must echo it exactly. Exception `83 02` becomes IllegalAddress, not a measurement. These explicit vectors are minimum oracle seeds, not the entire conformance suite.

One transport operation has a 250 ms deadline. An idempotent read may be retried once, within a total 500 ms budget. A write that times out after transmission has an unknown outcome and must not be retried automatically. A fake clock makes deadline tests deterministic. Close is idempotent and prevents subsequent requests. Cancellation closes or drains the transport so old responses cannot satisfy later operations.

## Data and software boundaries

ProtocolSpec includes protocol/version, command name, request grammar or register/function, response schema, units, signedness, scaling, legal range, timeout, retry policy, side-effect class, and source anchor for every field. Missing behavior must be `unresolved`, not a guessed default.

The generated driver's public API is identify(), read_temperature(), read_pressure() where supported, set_voltage(volts), disable_output(), and close(). Unsupported capabilities are explicit. Return measurements with value, unit, sampled_at, received_at, and quality. sampled_at is nullable when the wire protocol does not report acquisition time; do not mislabel host receipt time as physical sampling time. Use typed exceptions for parse errors, deadline exceeded, device errors, unsupported operations, and unknown write outcomes.

Proposed package layout: src/driverforge/{spec,transport,driver,generate,report}, emulators/, manuals/, examples/specs/, tests/unit/, tests/conformance/, evaluation/, docs/, evidence/. The emulator and golden vectors derive from the manual, never the generated driver or a shared codec that could duplicate its bug. Common neutral datatypes are acceptable; shared encoding logic is not.

## Demonstration and outputs

Target command contract, to be implemented: `python -m driverforge demo --offline --output artifacts/demo`. It emits spec.json, candidate.py, conformance.json, report.html, and manifest.json. It exits 0 only if the demonstration observed the intended bad-candidate rejection and the good candidate passed every required check. `python -m driverforge check <driver> --spec <spec>` exits nonzero on violations. These commands are specified interfaces, not existing software in the planning repository.

The report shows source passage → interpreted field → wire bytes → driver result → verdict. It includes at least one failed candidate and one unresolved ambiguity, and clearly labels replay versus live generation.

## Scope exclusions and later work

No arbitrary PDF extraction, real device writes, universal driver generator, enterprise fleet management, or claim of universal Modbus/SCPI compliance. A later PyVISA adapter, OpenHTF plug, or CAN decoder is worthwhile only after the two-instrument suite is complete. A physical instrument can independently validate one adapter later; its purchase is not a prerequisite.

## Acceptance requirements

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
