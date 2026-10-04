"""Three actual process measurements per supported workload; no extrapolation."""

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path


def main():
    target = Path("artifacts/benchmark")
    target.mkdir(parents=True, exist_ok=True)
    runs = []
    for workload in ("baseline", "core", "upstream"):
        for trial in range(3):
            result = target / f"{workload}-{trial}.json"
            run = subprocess.run(
                [
                    sys.executable,
                    "tools/measure_workload.py",
                    workload,
                    "--result",
                    str(result),
                    "--output",
                    str(target / f"{workload}-{trial}"),
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            assert run.returncode == (1 if workload == "upstream" else 0), run.stderr
            measured = json.loads(result.read_text())
            measured["trial"] = trial + 1
            runs.append(measured)
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "cpu": "Intel Core i9-11900H @ 2.50 GHz, 16 logical CPUs",
        "ram": "64 GiB installed",
        "lock_sha256": hashlib.sha256(Path("requirements.lock").read_bytes()).hexdigest(),
        "target_seconds": 10,
        "target_memory_bytes": 256 * 1024 * 1024,
        "runs": runs,
        "comparison_limit": "core demo runs 39 cases plus six mutations; upstream eight; baseline thirteen scenarios; workloads are not equivalent speed benchmarks",
    }
    report["within_limits"] = all(
        r["elapsed_seconds"] < 10 and r["peak_working_set_bytes"] < 256 * 1024 * 1024 for r in runs
    )
    Path("evidence/performance.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(report, indent=2))
    assert report["within_limits"]


if __name__ == "__main__":
    main()
