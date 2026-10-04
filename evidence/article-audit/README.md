# Publication audit, 2026-10-04

This is follow-up review for Walter's portfolio article, after the original
implementation and hosted CI. It must not be counted as first-pass performance.
The starting commit was 0583650745cc552fa6f2b3300bbf3db34e37f552.

The audit reran the existing 94 tests successfully, then found a concrete omission
in `compare_reports`: it ignored report completeness, exit code and oracle version,
plus case expectations, source evidence, diagnosis and elapsed fake time. A CLI diff
could therefore return 0 even when the oracle version changed. Six new regression
cases failed before repair; their output is retained in `diff-before.txt`. The
comparator now includes those fields and reports global changes with `scope: report`.

The final recorded local suite passes 100 tests, with the known PyMeasure SCPI
FutureWarning. Lint, formatting, strict source typing, dependency consistency,
wheel construction and the offline demo also pass. The demo still passes the same
39 reference cases and rejects all six deliberate mutants. The unchanged Agilent
check still exits 1: six cases pass and its two synthetic consumer-contract
violations remain failed. `checks.json` records commands, expected/actual exits,
source fingerprints and log hashes; `junit.xml` records the full suite.

No oracle values, driver semantics, upstream code or original experiment evidence
were changed. Documentation cleanup removed a stray CAD environment reference and
the stale assertion that the already implemented CLI was only planned. Physical
validation, live generation, hostile-code isolation and practitioner adoption
remain unverified. Original 94-test hosted run evidence remains under `../ci/`;
new audit-commit hosted results should be checked at the repository Actions page.
