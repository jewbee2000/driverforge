# Acceptance and evidence plan

Status: executed. The release suite has 94 passing tests, lint/format/type checks,
and fresh-install/consumer evidence. See [requirements-evidence.json](../evidence/requirements-evidence.json)
for commands, outcomes and hashes. DF-10 is not applicable with untrusted execution
disabled; DF-18 is deferred. The design below governs future changes.

## Required layers

1. M0 baseline comparison establishes the useful contribution and selects existing libraries.
2. Independent contract checks cover units, boundary equality, missing/invalid data, and lifecycle behavior.
3. Integration checks exercise externally supplied inputs or a consumer package through public interfaces.
4. Known defects and negative cases verify that the oracle catches the intended errors.
5. End-to-end checks verify CLI outcomes, reports, export integrity, installation, resource bounds, and local data handling.

Do not compute expected values with implementation helpers. Keep a separate oracle commit before optional generation or repair experiments. Test counts are coverage inventories, not quality scores.

## Release evidence

Every applicable Must requirement needs executed evidence, not a planned test path. Record command, environment/lockfile hash, input hash, source commit and dirty state, oracle hash, requirement ID, exit code, artifact hash, and outcome. A required failure or inconclusive result blocks a successful release check. Conditional requirements may be not applicable only with the disabled feature and reason documented. Explicitly record deferred Should/Could items and all exclusions.

Run meaningful lint, type, property, integration, mutation, and fresh-install checks appropriate to the implementation. Add CI only after its commands work locally. Separate implementation verification, simulation evidence, physical measurement, practitioner feedback, and live model evaluation. A bundled demo or an agent walkthrough is not proof of industry adoption.
