import json
import subprocess
import sys

import pytest

from driverforge import (
    InvalidInput,
    ProtocolSpec,
    ResourceLimit,
    asset,
    factory_for,
    reference_cases,
    run_campaign,
)
from driverforge.spec import load_json


def test_recorded_performance_within_frozen_limits():
    from pathlib import Path

    data = json.loads(Path("evidence/performance.json").read_text())
    assert data["within_limits"] is True and len(data["runs"]) == 9
    assert all(
        r["elapsed_seconds"] < data["target_seconds"]
        and r["peak_working_set_bytes"] < data["target_memory_bytes"]
        for r in data["runs"]
    )


def test_oversize_inputs_case_and_wall_limits(tmp_path):
    large = tmp_path / "large.json"
    large.write_bytes(b" " * 65537)
    with pytest.raises(ResourceLimit):
        load_json(large)
    spec = ProtocolSpec.load(asset("pressurebrick.json"))
    with pytest.raises(InvalidInput):
        run_campaign(factory_for("pressurebrick"), spec, reference_cases("pressurebrick") * 6)
    result = run_campaign(
        factory_for("pressurebrick"), spec, reference_cases("pressurebrick"), wall_limit=-1
    )
    assert result.exit_code == 2 and result.complete is False
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "driverforge",
            "--wall-seconds",
            "0.001",
            "demo",
            "--offline",
            "--output",
            str(tmp_path / "deadline"),
        ],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert run.returncode == 2
    data = json.loads((tmp_path / "deadline/conformance.json").read_text())
    assert data["complete"] is False and "wall limit" in data["cases"][0]["detail"]
