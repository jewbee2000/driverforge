"""Agent-executed cold-start adoption using a wheel and a separate directory."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--output", type=Path, required=True)
    args.add_argument("--wheelhouse", type=Path, required=True)
    options = args.parse_args()
    output = options.output.resolve()
    if output.exists():
        raise RuntimeError("use a new consumer directory; existing files preserved")
    output.mkdir(parents=True)
    started = time.perf_counter()
    commands = []
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    def run(command, expected=0):
        start = time.perf_counter()
        result = subprocess.run(
            command, cwd=output, env=env, capture_output=True, text=True, timeout=180, check=False
        )
        commands.append(
            {
                "command": [str(c) for c in command],
                "exit_code": result.returncode,
                "elapsed_seconds": time.perf_counter() - start,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.returncode != expected:
            (output / "partial.json").write_text(json.dumps(commands, indent=2))
            raise RuntimeError(
                f"unexpected exit {result.returncode}: {result.stderr} {result.stdout}"
            )
        return result

    run([sys.executable, "-m", "venv", str(output / ".venv")])
    python = output / ".venv/Scripts/python.exe"
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            str(options.wheelhouse.resolve()),
            "-r",
            str(ROOT / "requirements.lock"),
        ]
    )
    wheel = next(options.wheelhouse.glob("driverforge-0.1.0-*.whl"))
    run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel.resolve())])
    for name in ("test_meter.py", "consumer.json"):
        shutil.copy2(ROOT / "examples/consumer" / name, output / name)
    probe = run([str(python), "-c", "import driverforge; print(driverforge.__file__)"])
    assert str(output / ".venv") in probe.stdout
    source = output / "test_meter.py"
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    run(
        [str(python), "-m", "pytest", "-p", "driverforge.pytest_plugin", "test_meter.py", "-q"],
        expected=1,
    )
    config = json.loads((output / "consumer.json").read_text())
    config["calibration_factor"] = 1
    config["run_name"] = "corrected"
    (output / "consumer.json").write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    run([str(python), "-m", "pytest", "-p", "driverforge.pytest_plugin", "test_meter.py", "-q"])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
    result = {
        "label": "agent-executed, no practitioner feedback",
        "commands": commands,
        "setup_seconds": time.perf_counter() - started,
        "non_default_reading": 2.5,
        "python_lines": len(source.read_text().splitlines()),
        "configuration_lines": len((output / "consumer.json").read_text().splitlines()),
        "source_sha256": original_hash,
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
    }
    (output / "walkthrough.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({k: v for k, v in result.items() if k != "commands"}, indent=2))


if __name__ == "__main__":
    main()
