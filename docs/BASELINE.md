# M0 comparison and usefulness gate

Experiment: Python 3.12.2, PyMeasure 0.16.0, PyVISA 1.16.2,
PyVISA-sim 0.7.1. Run `python examples/baseline/run_baseline.py` from the root.
Executed results are in [baseline.json](../evidence/baseline.json). The script
exercises voltage_dc, current_dc and resistance on the unchanged Agilent34410A.
Both backends pass the three synthetic happy paths. expected_protocol also
injects malformed text; upstream returns `garbage`, which an explicit numeric
consumer contract must reject. This is an observed supported-operation mismatch,
not a reproduced hardware bug or a claim that the vendor emits that text.

Install: local venv, `pip install -r requirements.lock`. No VISA vendor runtime,
instrument, Qt GUI binding, or model service is needed. The baseline is 51 lines
of Python and 20 lines of YAML before automatic formatting; final measured code
sizes and timings will be saved with the consumer walkthrough.

| Behavior | expected_protocol | PyVISA-sim YAML | Proposed extension |
| --- | --- | --- | --- |
| Three numeric operations | executed, pass | executed, pass | same unchanged driver |
| Malformed/device-error bytes | pairs supported | dialogues supported | no novelty claim |
| Missing response/timeout | custom method mock possible | missing dialogue response | scheduled fake deadline |
| Fragments | byte adapter supports partial reads | raw-byte dialogues | recorded individual chunks |
| Terminators | explicitly excluded in helper | EOM configured | bytes include terminators |
| Late response/cancel | custom test code needed | no declarative timed schedule in inspected definitions | discard/close evidence |
| Retry count/unknown-write verdict | handwritten assertions | handwritten assertions | reusable verdict/attempt count |
| Source-linked JSON/HTML | test author supplies it | test author supplies it | automatic local artifacts |

These are bounded observations from executed examples and inspected pinned source,
not an exhaustive search. Ordinary pytest plus mocks can express the entire
workflow. DriverForge packages the repeated fault assertions and evidence; no
claim of a new protocol simulator or framework is justified. Proceed with a
small compatible fault kit and a public pytest fixture, not driver generation.
Keep the upstream implementation intact and label unsupported cancellation and
retry contracts explicitly. A failed upstream case remains failed.

QCoDeS documents the same PyVISA-sim approach; installing a second instrument
framework would not improve this narrow comparison. instrbuilder already builds
SCPI drivers from command metadata, so another generator is deferred.

Primary sources inspected 2026-10-04:

- [PyMeasure expected_protocol](https://pymeasure.readthedocs.io/en/stable/dev/adding_instruments/tests.html)
- [Pinned driver source](https://github.com/pymeasure/pymeasure/blob/597e0c6760288f6fe1c5a677e9d53a2b7a033566/pymeasure/instruments/agilent/agilent34410A.py)
- [PyVISA-sim definitions](https://pyvisa.readthedocs.io/projects/pyvisa-sim/en/latest/definitions.html)
- [QCoDeS simulation example](https://microsoft.github.io/Qcodes/examples/writing_drivers/Creating-Simulated-PyVISA-Instruments.html)
- [instrbuilder](https://github.com/lucask07/instrbuilder)
- [Keysight 34410A/11A command quick reference](https://www.keysight.com/us/en/assets/9018-61141/programming-guides/9018-61141.pdf)
- [Keysight user's guide](https://www.keysight.com/us/en/assets/9018-05586/user-manuals/9018-05586.pdf)

Keysight's URLs currently serve a regional asset landing page to the browser tool.
No manual copy is shipped. The public driver and PyMeasure API documentation
also state the exact commands/units used; integration readings are independently
authored synthetic examples. Issue 1081 is motivation only, not this experiment.
