"""Verify README's installation from a clean local checkout and new environment."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", required=True, type=Path)
    parser.add_argument("--wheelhouse", required=True, type=Path)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    if checkout.exists():
        raise RuntimeError("use a new checkout directory")
    command_log = []
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)

    def run(command, cwd, expected=0):
        started = time.perf_counter()
        result = subprocess.run(
            command, cwd=cwd, env=env, capture_output=True, text=True, timeout=180, check=False
        )
        command_log.append(
            {
                "command": [str(c) for c in command],
                "exit_code": result.returncode,
                "elapsed_seconds": time.perf_counter() - started,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.returncode != expected:
            (ROOT / "evidence/fresh-install-failed.json").write_text(
                json.dumps(command_log, indent=2)
            )
            raise RuntimeError(result.stdout + result.stderr)
        return result

    run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT.as_posix()}",
            "clone",
            "--no-hardlinks",
            str(ROOT),
            str(checkout),
        ],
        ROOT,
    )
    git = ["git", "-c", f"safe.directory={checkout.as_posix()}"]
    commit = run([*git, "rev-parse", "HEAD"], checkout).stdout.strip()
    dirty = bool(run([*git, "status", "--porcelain"], checkout).stdout)
    assert not dirty
    run([sys.executable, "-m", "venv", str(checkout / ".venv")], checkout)
    python = str(checkout / ".venv/Scripts/python.exe")
    run(
        [
            python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            str(args.wheelhouse.resolve()),
            "-r",
            "requirements.lock",
        ],
        checkout,
    )
    run(
        [
            python,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            str(args.wheelhouse.resolve()),
            "--no-build-isolation",
            "-e",
            ".[pymeasure]",
        ],
        checkout,
    )
    run([python, "-m", "pip", "check"], checkout)
    run([python, "-m", "ruff", "check", "src", "tests", "tools", "examples"], checkout)
    run([python, "-m", "ruff", "format", "--check", "src", "tests", "tools", "examples"], checkout)
    run([python, "-m", "mypy"], checkout)
    # Bootstrap only: the evidence-about-this-run check cannot read its own future
    # record. A subsequent clean checkout runs the entire suite without exclusion.
    test_args = ["-q"]
    if not (checkout / "evidence/fresh-install.json").exists():
        test_args += ["-k", "not test_recorded_fresh_checkout_commands"]
    tests = run([python, "-m", "pytest", *test_args], checkout)
    demo = run(
        [python, "-m", "driverforge", "demo", "--offline", "--output", "artifacts/demo"], checkout
    )
    run(
        [
            python,
            "-m",
            "driverforge",
            "diff",
            "artifacts/demo/conformance.json",
            "artifacts/demo/conformance.json",
        ],
        checkout,
    )
    assert not run([*git, "status", "--porcelain"], checkout).stdout
    record = {
        "source_commit": commit,
        "checkout_dirty": dirty,
        "source_install": True,
        "wheel_install": True,
        "wheel_evidence": "evidence/consumer/walkthrough.json",
        "test_exit_code": tests.returncode,
        "demo_exit_code": demo.returncode,
        "test_command": command_log[-4]["command"],
        "lock_sha256": hashlib.sha256((checkout / "requirements.lock").read_bytes()).hexdigest(),
        "oracle_sha256": hashlib.sha256(
            (checkout / "evaluation/cases.json").read_bytes()
        ).hexdigest(),
        "demo_manifest_sha256": hashlib.sha256(
            (checkout / "artifacts/demo/manifest.json").read_bytes()
        ).hexdigest(),
        "commands": command_log,
    }
    (ROOT / "evidence/fresh-install.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({k: v for k, v in record.items() if k != "commands"}, indent=2))


if __name__ == "__main__":
    main()
