import copy
import json
import subprocess
import sys

import pytest
from jsonschema import Draft202012Validator

from driverforge import (
    InvalidInput,
    ProtocolSpec,
    asset,
    factory_for,
    reference_cases,
    run_campaign,
)


def test_states_versions_and_crashed_driver():
    spec = ProtocolSpec.load(asset("pressurebrick.json"))
    case = reference_cases("pressurebrick")[0]

    def crashed(_):
        raise RuntimeError("driver constructor failed")

    result = run_campaign(crashed, spec, [case])
    assert result.exit_code == 2 and result.cases[0].state == "inconclusive"
    good = run_campaign(factory_for("pressurebrick"), spec, [case]).to_dict()
    schema = json.loads((asset("cases.json").parents[1] / "schemas/result-v1.json").read_text())
    Draft202012Validator(schema).validate(good)
    bad = copy.deepcopy(case)
    bad["expected"] = -999
    assert run_campaign(factory_for("pressurebrick"), spec, [bad]).exit_code == 1
    with pytest.raises(InvalidInput):
        run_campaign(factory_for("pressurebrick"), spec, [])


@pytest.mark.parametrize(
    "mode,expected",
    [("good", 0), ("bad", 1), ("unknown_version", 2), ("unsupported", 2), ("unresolved", 2)],
)
def test_cli_exit_contract(tmp_path, mode, expected):
    doc = json.loads(asset("pressurebrick.json").read_text())
    driver = "unsigned_decode" if mode == "bad" else "pressurebrick"
    if mode == "unknown_version":
        doc["schema_version"] = 42
    if mode == "unsupported":
        candidate = tmp_path / "untrusted.py"
        candidate.write_text("raise RuntimeError('must not execute')")
        driver = str(candidate)
    if mode == "unresolved":
        del doc["operations"]["read_temperature"]["fields"]["signed"]
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(doc))
    command = [
        sys.executable,
        "-m",
        "driverforge",
        "check",
        driver,
        "--spec",
        str(spec),
        "--output",
        str(tmp_path / "out"),
    ]
    run = subprocess.run(command, capture_output=True, text=True, check=False, timeout=15)
    assert run.returncode == expected, run.stdout + run.stderr
    report = json.loads((tmp_path / "out/conformance.json").read_text())
    assert report["exit_code"] == expected
    assert all(
        c["state"] in {"pass", "fail", "inconclusive", "not_applicable"} for c in report["cases"]
    )


def test_changed_fixed_reference_contract_is_inconclusive():
    doc = json.loads(asset("pressurebrick.json").read_text())
    doc["operations"]["read_temperature"]["fields"]["scale"]["value"] = 0.1
    result = run_campaign(
        factory_for("pressurebrick"),
        ProtocolSpec.from_dict(doc),
        [reference_cases("pressurebrick")[0]],
    )
    assert result.exit_code == 2
