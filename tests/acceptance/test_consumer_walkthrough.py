import hashlib
import json
from pathlib import Path


def test_executed_clean_consumer_failure_and_correction():
    root = Path("evidence/consumer")
    walkthrough = json.loads((root / "walkthrough.json").read_text())
    assert "agent-executed" in walkthrough["label"] and walkthrough["non_default_reading"] == 2.5
    commands = walkthrough["commands"]
    pytest_runs = [c for c in commands if "pytest" in c["command"]]
    assert [c["exit_code"] for c in pytest_runs] == [1, 0]
    failed = json.loads((root / "failed/conformance.json").read_text())
    corrected = json.loads((root / "corrected/conformance.json").read_text())
    assert failed["exit_code"] == 1 and failed["cases"][0]["observed"] == 2500.0
    assert corrected["exit_code"] == 0 and corrected["cases"][0]["observed"] == 2.5
    assert failed["cases"][0]["transcript"] == corrected["cases"][0]["transcript"]
    assert walkthrough["setup_seconds"] > 0 and walkthrough["python_lines"] > 0
    for name in ("failed", "corrected"):
        manifest = json.loads((root / name / "manifest.json").read_text())
        for artifact, expected in manifest["artifact_sha256"].items():
            assert hashlib.sha256((root / name / artifact).read_bytes()).hexdigest() == expected
