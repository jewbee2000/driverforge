# Decisions and reference limits

2026-10-04, M0. Use Python 3.12.2 on Windows 11, a repository-local venv,
and pip as uv is absent. Docker CLI 28.0.4 has no reachable daemon. Untrusted
generated-code execution and live generation are disabled. Checked-in, reviewed
reference drivers and deliberate mutation classes are trusted software fixtures.
A subprocess for bounded trusted checks is not an isolation boundary.

Integrate PyMeasure instead of replacing its instrument abstraction. Select
Agilent34410A from PyMeasure 0.16.0, tag/commit
597e0c6760288f6fe1c5a677e9d53a2b7a033566 (MIT), unchanged. Three operations:
voltage_dc, current_dc, resistance. Manufacturer MEASure commands are linked in
the independently authored integration contract; manufacturer manuals are not
redistributed. All simulated readings are synthetic, not measured.

Freeze limits before implementation: 64 KiB per JSON input; 16 spec operations;
100 campaign cases; 16 scheduled faults per case; 256 response bytes; 250 ms
per exchange; reference reads have at most two attempts / 500 ms fake time;
reference writes have one attempt. CLI trusted worker wall limit 10 seconds,
report budget 4 MiB, target full core demo under 10 seconds and 256 MiB peak
process memory on i9-11900H (16 logical CPUs), 64 GiB RAM, Windows 11 Home
10.0.26300. Measure imported PyMeasure separately; its import costs are relevant.
No CAD workload exists in this project; the generic CAD worker clause is inapplicable.

The oracle uses literal wire vectors and expected outcomes, separate from driver
code. Golden calculations: FB2E = 64302; 64302 - 65536 = -1234; * 0.01 = -12.34 C.
1.250 V * 1000 = 1250 = 04E2. 007B = 123; * 0.1 = 12.3 kPa.
Evaluation is public/open, not a held-out suite or evidence of practitioner adoption.
