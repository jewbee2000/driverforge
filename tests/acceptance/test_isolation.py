import subprocess
import sys


def test_untrusted_generated_code_disabled(tmp_path):
    candidate = tmp_path / "candidate.py"
    sentinel = tmp_path / "forbidden.txt"
    candidate.write_text(
        f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('escaped')\n"
    )
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "driverforge",
            "check",
            str(candidate),
            "--spec",
            "examples/specs/pressurebrick.json",
            "--output",
            str(tmp_path / "result"),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    assert run.returncode == 2 and not sentinel.exists()
    assert "unsupported candidate" in run.stdout
