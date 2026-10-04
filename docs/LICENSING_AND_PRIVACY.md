# Local data and licensing

DriverForge code, hand-authored fictional manuals, synthetic case data,
independently authored integration contracts, and consumer examples are MIT under
LICENSE. No employer IP, device logs, actual measurements, or autobiographical
data were used. Manufacturer manuals are linked, not copied or shipped.

The unchanged Agilent34410A implementation is installed from PyMeasure 0.16.0
(MIT, Copyright 2013–2026 PyMeasure Developers); its license stays with that
distribution. Commit and byte identity are recorded in evidence/upstream.json.
No source copied from upstream is presented as original project code.

All installed runtime/development packages are pinned in requirements.lock.
evidence/licenses.json records actual distribution metadata and bundled license
file paths, including transitive dependencies. Their own licenses apply. Wheels
remain local ignored artifacts; when redistributing them later, include their
licenses and third-party notices. No new service or paid runtime is required.

Installation/download commands use PyPI and a read-only GitHub source download
for provenance. After installation, demo/check/test workflows make no network
requests, read no model credentials, perform no telemetry, and do no physical I/O.
Reports, transcripts and hashes are written under the selected local output
directory. CLI output paths containing parent traversal, symlinks or junctions
are rejected. Source statements are data; input cannot choose executable Python.

The offline acceptance run removes credentials from the process environment and
denies Python socket audit events, including in the CLI worker. This verifies
this Python workflow's offline behavior; it is not a hostile-code sandbox or an
operating-system firewall. Docker's daemon is unavailable. Untrusted generated
code execution is disabled and its forbidden-write/egress isolation checks are
not applicable until a real isolation boundary is implemented and verified.
