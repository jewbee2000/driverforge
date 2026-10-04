import json
from pathlib import Path

from driverforge import asset


def test_lockfile_assets_and_documented_install():
    assert asset("requirements.lock").read_bytes() == Path("requirements.lock").read_bytes()
    assert "pip install -r requirements.lock" in Path("README.md").read_text()
    assert "python -m driverforge demo --offline" in Path("README.md").read_text()


def test_recorded_fresh_checkout_commands():
    record = json.loads(Path("evidence/fresh-install.json").read_text())
    assert record["wheel_install"] and record["source_install"]
    assert record["test_exit_code"] == 0
    assert record["demo_exit_code"] == 0
    assert record["source_commit"] and record["checkout_dirty"] is False
