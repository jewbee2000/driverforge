"""Execute requirement-specific checks and retain exact release evidence."""

import hashlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    register = json.loads((ROOT / "requirements.json").read_text())
    git = ["git", "-c", f"safe.directory={ROOT.as_posix()}"]
    commit = subprocess.run(
        [*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            [*git, "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout
    )
    input_hashes = {
        str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "examples/specs").glob("*.json"))
    }
    rows = []
    logs = ROOT / "evidence/checks"
    logs.mkdir(exist_ok=True)
    for req in register["requirements"]:
        id = req["id"]
        reason = None
        state = "pass"
        if id == "DF-10":
            state = "not_applicable"
            reason = "untrusted execution disabled; Docker daemon unavailable; sandbox egress/write/CPU tests not run"
        if id == "DF-18":
            state = "deferred"
            reason = "optional generation not enabled; no API budget; no live model campaign run"
        command = [sys.executable, "-m", "pytest", req["planned_test"], "-q"]
        result = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, timeout=30, check=False
        )
        log = logs / f"{id}.txt"
        log.write_text(result.stdout + result.stderr, encoding="utf-8", newline="\n")
        if result.returncode != 0:
            state = "fail"
        row = {
            "requirement": id,
            "priority": req["priority"],
            "state": state,
            "reason": reason,
            "command": ["python", "-m", "pytest", req["planned_test"], "-q"],
            "executed_interpreter": sys.executable,
            "exit_code": result.returncode,
            "source_commit": commit,
            "source_dirty": dirty,
            "lock_sha256": sha(ROOT / "requirements.lock"),
            "oracle_version": json.loads((ROOT / "evaluation/frozen.json").read_text())[
                "oracle_version"
            ],
            "oracle_sha256": sha(ROOT / "evaluation/cases.json"),
            "test_sha256": sha(ROOT / req["planned_test"]),
            "input_hashes": input_hashes,
            "log": str(log.relative_to(ROOT)),
            "log_sha256": sha(log),
        }
        rows.append(row)
        print(f"{id}: {state} (exit {result.returncode})", flush=True)
    extra_commands = [
        ["-m", "ruff", "check", "src", "tests", "tools", "examples"],
        ["-m", "ruff", "format", "--check", "src", "tests", "tools", "examples"],
        ["-m", "mypy"],
        ["-m", "pytest", "-q"],
        ["-m", "pip", "check"],
    ]
    checks = []
    for index, args in enumerate(extra_commands):
        result = subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        log = logs / f"release-{index}.txt"
        log.write_text(result.stdout + result.stderr, encoding="utf-8", newline="\n")
        checks.append(
            {
                "command": ["python", *args],
                "exit_code": result.returncode,
                "log": str(log.relative_to(ROOT)),
                "log_sha256": sha(log),
            }
        )
        assert result.returncode == 0, result.stdout + result.stderr
    all_must = all(
        r["state"] in ("pass", "not_applicable") for r in rows if r["priority"] == "must"
    )
    record = {
        "schema_version": 1,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "requirements": rows,
        "checks": checks,
        "all_applicable_must_pass": all_must,
        "known_failed_upstream_cases": ["malformed", "device-error"],
        "physical_validation": False,
        "practitioner_validation": False,
        "live_model_evaluation": False,
    }
    (ROOT / "evidence/requirements-evidence.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    assert all_must


if __name__ == "__main__":
    main()
