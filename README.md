# DriverForge

A local fault-testing extension for instrument drivers, with exact wire transcripts,
source-linked verdicts, and an installable pytest fixture. It integrates the existing
PyMeasure adapter seam. [The baseline comparison](docs/BASELINE.md) explains its scope.

**Software release candidate.** Source and milestone history are hosted at
[jewbee2000/driverforge](https://github.com/jewbee2000/driverforge). Two fictional reference drivers
pass 39 open conformance cases; all six deliberate defects are rejected. The unchanged
public Agilent34410A driver passes its three normal operations, timeout, fragmentation
and late-response cases. Synthetic malformed/device-error responses fail the explicit
numeric consumer contract; those failures remain visible. Physical validation and
practitioner adoption have not been demonstrated.

## Install and demonstrate

Verified on Windows 11 with Python 3.12.2. Python 3.12 is the supported version.
From a fresh checkout, in PowerShell:

~~~powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock
.venv\Scripts\python.exe -m pip install --no-build-isolation -e ".[pymeasure]"
.venv\Scripts\python.exe -m driverforge demo --offline --output artifacts/demo
~~~

With the venv active:

~~~text
python -m driverforge demo --offline --output artifacts/demo
~~~

Open artifacts/demo/report.html. Inspect failures/unsigned_decode/report.html:
FB2E became 643.02 C instead of -12.34 C. The good driver interprets it as signed.
Reports preserve both outcomes and an unresolved source ambiguity. This is
deterministic **REPLAY** using reviewed checked-in candidates, without a key or
hardware. Dependency installation uses the network; subsequent execution is local.

~~~powershell
.venv\Scripts\python.exe -m driverforge check pressurebrick --spec examples/specs/pressurebrick.json --output artifacts/check
.venv\Scripts\python.exe -m driverforge check agilent34410a --spec examples/specs/agilent34410a.json --output artifacts/agilent
.venv\Scripts\python.exe -m driverforge diff artifacts/demo/conformance.json artifacts/demo/conformance.json
~~~

The first check exits 0, the upstream check exits 1 for its actual contract
violations, and the unchanged diff exits 0. Invalid, unsupported, incomplete and
crashed checks exit 2. Generated Python paths are rejected. A worker timeout
cannot become a passing report.

## Use from pytest

The fixture loads automatically when installed. With plugin autoload disabled,
use -p driverforge.pytest_plugin.

~~~python
from driverforge import PressureBrick

def test_negative_temperature(driverforge_transport):
    wire = driverforge_transport({
        "read_temperature": (
            bytes.fromhex("0300000001"),
            bytes.fromhex("0302fb2e"),
        )
    })
    assert PressureBrick(wire).read_temperature().value == -12.34
~~~

For an existing driver, import agilent34410a from driverforge.pymeasure_adapter
and inject the transport. run_campaign accepts explicit cases and emits verdicts.
Add --campaign file.json to check non-default readings and faults without package
edits. See [public API and schemas](docs/PUBLIC_API.md), the
[integration spec](examples/specs/agilent34410a.json), and [consumer example](examples/consumer).

## Verify and reproduce the consumer walkthrough

GitHub Actions runs the Windows/Python 3.12.2 checks on pull requests and pushes to
main. The workflow can also be started manually from the Actions tab. Each run
retains JUnit results, test output artifacts, demo reports and the wheel when built
for 14 days. Action revisions are pinned to commits. Check the actual run status
at [Actions](https://github.com/jewbee2000/driverforge/actions); local checks alone
do not establish a successful hosted run.

~~~powershell
.venv\Scripts\python.exe -m ruff check src tests tools examples
.venv\Scripts\python.exe -m ruff format --check src tests tools examples
.venv\Scripts\python.exe -m mypy
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m build --wheel --no-isolation
.venv\Scripts\python.exe -m pip download -r requirements.lock --dest artifacts/wheelhouse
Copy-Item dist/driverforge-0.1.0-py3-none-any.whl artifacts/wheelhouse/
.venv\Scripts\python.exe tools/consumer_walkthrough.py --output artifacts/new-consumer --wheelhouse artifacts/wheelhouse
~~~

Use a new output directory each time. The script creates a separate venv and
installs the wheel with --no-index. It tests a 2.500 V response with an intentionally
wrong consumer calibration factor, retains exit 1 and the report, changes only
that configuration to factor 1, then obtains exit 0. Upstream and package sources
stay unchanged. [Executed consumer evidence](evidence/consumer/walkthrough.json)
records commands, setup duration and code/config size. This is an agent-executed
adoption example, not independent practitioner feedback.

## Evidence and limits

[Requirement evidence](evidence/requirements-evidence.json),
[milestone commands](evidence/progress.md), [performance](evidence/performance.json),
and [decisions](docs/DECISIONS.md) describe actual checks and scope. The open oracle
was committed before production code. Its literal expectations use no production codec.

Limits: 64 KiB inputs, 100 cases, 16 operations, 16 faults/case, 256 response bytes,
4 MiB reports, 10-second trusted CLI worker. Reference reads have at most two
250 ms attempts; uncertain writes transmit once. Receipt time is simulated host
time; physical sampling time is unknown.

Reference profiles are fictional fixed contracts; the register example covers
PDUs only. This release has one pinned synchronous PyMeasure integration and no
physical I/O, arbitrary PDF extraction, universal SCPI/Modbus coverage, model
generation or hostile-code execution. Docker's daemon was unavailable, so
generated-code isolation is disabled. Upstream validation failures remain unresolved.
Only Windows/Python 3.12 was verified. [Licensing and privacy](docs/LICENSING_AND_PRIVACY.md)
cover fixtures and dependencies. The [blog draft](docs/BLOG_DRAFT.md) stays
unpublished; the separate website checkout has not been pushed or deployed.
[Next steps](docs/NEXT_STEPS.md) prioritize repeatable checks and practitioner validation.
