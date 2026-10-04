# Agent-executed consumer walkthrough

The separate example consumes only documented public APIs and the wheel-installed
pytest fixture. The installed package and the upstream instrument source are not
edited. A fresh venv installs pinned cached dependencies with --no-index. This is
an agent walkthrough, not feedback from an independent test engineer.

The non-default input is a synthetic 2.500 V response. Initial consumer config
uses calibration_factor=1000; the expected contract remains 2.5 V. Pytest exits 1
and the report records observed 2500.0. Changing only calibration_factor to 1 and
run_name to corrected yields exit 0 and observed 2.5. Both reports keep the same
request/response transcript. See evidence/consumer/walkthrough.json for actual
commands, elapsed setup time, source/config size and wheel hash.

Baseline friction: expected_protocol needs only command/response pairs and
ordinary assertions for these happy paths. PyVISA-sim adds a YAML device, resource
and EOM setup. A consumer fault campaign adds explicit expected outcomes and
source-backed spec fields; it does not reduce the shortest happy-path test's size.
Its benefit is reusable timed faults, transmission-count checks, preserved failed
reports, source/byte evidence and CLI outcomes. Code size is not evidence of a
human productivity improvement, and no human time comparison was measured.

The canonical consumer example is intentionally initially failing. Do not treat
its first failed pytest execution as a package failure or fix it by changing the
expected reading. The correction belongs to consumer configuration. This does
not repair the separate unresolved upstream malformed/device-error behavior.

Reuse command: python tools/consumer_walkthrough.py --output <new-directory>
--wheelhouse artifacts/wheelhouse, after README's wheel/cache steps. Existing
directories are rejected so prior failures remain available.
