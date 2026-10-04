import hashlib
import json
import subprocess
import sys

from driverforge import asset


def test_actual_artifact_hashes_and_source_trace(tmp_path):
    output = tmp_path / "demo"
    run = subprocess.run(
        [sys.executable, "-m", "driverforge", "demo", "--offline", "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    manifest = json.loads((output / "manifest.json").read_text())
    for name, expected in manifest["artifact_sha256"].items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == expected
    assert manifest["candidate_sha256"] == manifest["artifact_sha256"]["candidate.py"]
    assert manifest["oracle_sha256"] == hashlib.sha256(asset("cases.json").read_bytes()).hexdigest()
    assert (
        manifest["environment_lock_sha256"]
        == hashlib.sha256(asset("requirements.lock").read_bytes()).hexdigest()
    )
    assert manifest["command"] and manifest["evaluator_sha256"] and manifest["oracle_version"]
    assert "dirty" in manifest["source"] and "commit" in manifest["source"]
    assert "dirty_diff_sha256" in manifest["source"]
    assert manifest["package_hashes"]["transport.py"] and manifest["package_sha256"]
    report = json.loads((output / "conformance.json").read_text())
    assert all(c["source"]["passage"] and c["interpreted_fields"] for c in report["cases"])
    context = json.loads((output / "context.json").read_text())
    assert context["ambiguities"][0]["outcome"] == "inconclusive"
    rejected = json.loads((output / "failures/unsigned_decode/conformance.json").read_text())
    assert rejected["exit_code"] == 1 and rejected["cases"][0]["observed"] == 643.02
