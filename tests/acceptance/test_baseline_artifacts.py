import json
from pathlib import Path


def test_baseline_executed_on_same_operations():
    data = json.loads(Path("evidence/baseline.json").read_text())
    assert data["pymeasure"] == "0.16.0" and data["pyvisa_sim"] == "0.7.1"
    for tool in ("expected_protocol", "pyvisa-sim"):
        assert {
            r["operation"] for r in data["results"] if r["tool"] == tool and "operation" in r
        } == {"voltage_dc", "current_dc", "resistance"}
    assert "small compatible fault kit" in Path("docs/BASELINE.md").read_text()
