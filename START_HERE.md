# Start here

DriverForge now has a local deterministic release candidate. Begin with README.md
for installation and the offline demo; evidence/requirements-evidence.json maps
executed checks to every requirement. The documents below govern further work.
Generated-code execution and live models stay disabled.

## Read in order

1. [Prioritized requirements and rationale](docs/REQUIREMENTS.md), then [Implementation plan](IMPLEMENTATION_PLAN.md) — scope, milestones, feasibility, and release gate.
2. [Specification](docs/SPEC.md) and [acceptance plan](docs/ACCEPTANCE.md) — concrete behavior and independent evidence.
3. [Agent workflow](docs/AGENT_WORKFLOW.md) — development, evaluation, isolation, and provenance.
4. [Tasks](TASKS.md) — current progress.
5. [Blog brief](docs/BLOG_BRIEF.md) — eventual article and honest claims.

## Suggested first agent message

Implement DriverForge in this repository using START_HERE.md, docs/REQUIREMENTS.md, docs/SPEC.md, docs/ACCEPTANCE.md, and IMPLEMENTATION_PLAN.md. Begin with the M0 existing-tool comparison and usefulness gate. Prefer a compatible integration if it meets the requirements; do not build a duplicate framework. Then continue through applicable Must requirements and the independent consumer walkthrough for the deterministic offline release without waiting for routine design approvals. Make sensible choices inside the stated scope and record them. Establish independent acceptance checks before product code, keep the oracle separate, and retain failed cases. Commit coherent milestones locally and update TASKS.md and evidence/progress.md. Verify outputs from a fresh environment. Do not push, deploy, publish, buy hardware, or spend on model APIs. Do not invent benchmark or physical results. The optional live-model experiment can remain explicitly unrun if no budget or credential is available. Finish by updating the first-person draft with actual evidence and reporting what remains for publication.

## Environment setup

Use a repo-local virtual environment and lock stable, compatible dependencies during M0. Python 3.12 is the preferred starting point, subject to the CAD stack's supported versions. No paid service is needed for the initial release. Install into the project, not global Python. Prefer uv if available; a standard virtual environment and pinned requirements are an acceptable fallback. Record actual versions rather than copying an unverified lockfile.

The current preparation environment had Python 3.12.14 through the Codex runtime, Git, and Ruby available. The website bundle check passed, but rendering was blocked by a Jekyll runtime load error. uv, gh, and CMake were not found on the shell PATH. Docker's CLI existed but its daemon was unavailable. These are observations, not required changes to Walter's computer. The implementation session may have a different environment; check it before installing tools. Dependency downloads need network access. Generated-code experiments require real isolation; Docker is one option once operational, not a prerequisite for all deterministic modules.

## Publication boundary

Walter authorized project publication on 2026-10-04. The public repository is https://github.com/jewbee2000/driverforge, with origin pointing to its HTTPS Git URL. This authorization supersedes the original no-push instruction for the project repository. It does not authorize publication of the article or pushing the separate website checkout. See evidence/progress.md for the actual push and remote verification.

The matching unpublished Jekyll draft lives in the separate website-drafts checkout supplied with this package. Its normal build must not publish the draft. See that checkout's PORTFOLIO_HANDOFF.md before integrating the article.
