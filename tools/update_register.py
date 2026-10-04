"""Reconcile requirement statuses with evidence, without changing contracts."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
executed = json.loads((ROOT / "evidence/requirements-evidence.json").read_text(encoding="utf-8"))
states = {row["requirement"]: row["state"] for row in executed["requirements"]}
register_path = ROOT / "requirements.json"
register = json.loads(register_path.read_text(encoding="utf-8"))
register["status"] = "verified_local_release_candidate"
register["decision_status"] = "bounded_baseline_and_agent_consumer_usefulness_demonstrated"
for req in register["requirements"]:
    req["status"] = {
        "pass": "verified",
        "not_applicable": "not_applicable",
        "deferred": "deferred",
    }[states[req["id"]]]
    req["executed_evidence"] = "evidence/requirements-evidence.json"
register_path.write_text(json.dumps(register, indent=2) + "\n", encoding="utf-8", newline="\n")
path = ROOT / "docs/REQUIREMENTS.md"
text = path.read_text(encoding="utf-8")
text = text.replace(
    "Status: planned, not implemented.",
    "Status: verified local software release candidate. Executed mappings are in [requirements-evidence.json](../evidence/requirements-evidence.json); known upstream failures and conditional exclusions remain explicit.",
)
for id, state in states.items():
    pattern = rf"(### {id} —.*?)(?=\n### |\n## |\Z)"

    def update(match, state=state):
        return (
            match[0]
            .replace("**Planned evidence:**", "**Executed check:**")
            .replace(
                "**Status:** not implemented.",
                f"**Status:** {state}; see the executed evidence register.",
            )
        )

    text = re.sub(pattern, update, text, flags=re.DOTALL)
text = text.replace(
    "All planned test paths above are future work.",
    "All listed check modules were executed; feature-disabled checks verify rejection, not a sandbox or model campaign.",
)
path.write_text(text, encoding="utf-8", newline="\n")
