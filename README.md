# DriverForge

Instrument drivers whose behavior can be checked against the wire protocol.

**Status: planned; implementation has not started.** This repository contains the requirements, execution plan, acceptance design, and blog draft for an agent-assisted engineering project. It does not yet contain working application code or benchmark results.

Start with [START_HERE.md](START_HERE.md). The [implementation plan](IMPLEMENTATION_PLAN.md) defines the build and [specification](docs/SPEC.md) defines what must be proven.

The intended demonstration: A temperature module reports a negative temperature. A generated driver mistakenly decodes the signed register as unsigned. The independent byte-level suite rejects it; a corrected driver passes. An ambiguous write command is rejected rather than guessed.

The final release must run offline without hardware or a model key. Live AI evaluations and physical validation, where applicable, are separate and explicitly labeled.
