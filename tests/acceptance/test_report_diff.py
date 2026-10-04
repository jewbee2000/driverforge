import copy
import json
import subprocess
import sys

import pytest

from driverforge import ProtocolSpec, asset, factory_for, reference_cases, run_campaign
from driverforge.report import compare_reports


def test_terminator_scale_and_attempt_changes_are_specific():
    report = run_campaign(
        factory_for("pressurebrick"),
        ProtocolSpec.load(asset("pressurebrick.json")),
        [reference_cases("pressurebrick")[0]],
    ).to_dict()
    assert compare_reports(report, copy.deepcopy(report)) == []
    after = copy.deepcopy(report)
    after["cases"][0]["transcript"][0]["data_hex"] += "0a"
    after["cases"][0]["interpreted_fields"]["scale"] = 0.1
    after["cases"][0]["attempts"] = 2
    changes = compare_reports(report, after)
    assert {c["field"] for c in changes} == {"transcript", "interpreted_fields", "attempts"}
    assert all(
        c["operation"] == "read_temperature" and c["requirement"] == "DF-03" for c in changes
    )
    assert (
        next(c for c in changes if c["field"] == "transcript")["after"][0]["data_hex"]
        == "03000000010a"
    )


def report_fixture():
    return run_campaign(
        factory_for("pressurebrick"),
        ProtocolSpec.load(asset("pressurebrick.json")),
        [reference_cases("pressurebrick")[0]],
    ).to_dict()


def test_report_completion_and_oracle_changes_are_visible():
    before = report_fixture()
    after = copy.deepcopy(before)
    after.update(complete=False, exit_code=2, oracle_version="revised-contract")
    changes = compare_reports(before, after)
    assert {change["field"] for change in changes} == {
        "complete",
        "exit_code",
        "oracle_version",
    }
    assert all(change["scope"] == "report" for change in changes)


@pytest.mark.parametrize(
    "field,value",
    [
        ("expected", -99),
        ("elapsed_ms", 251),
        ("source", {"anchor": "revised-manual", "passage": "Updated evidence"}),
        ("detail", "Updated diagnosis"),
    ],
)
def test_case_contract_and_evidence_changes_are_visible(field, value):
    before = report_fixture()
    after = copy.deepcopy(before)
    after["cases"][0][field] = value
    changes = compare_reports(before, after)
    assert len(changes) == 1
    assert changes[0]["field"] == field
    assert changes[0]["before"] == before["cases"][0][field]
    assert changes[0]["after"] == value


def test_cli_reports_metadata_only_difference(tmp_path):
    before = report_fixture()
    after = copy.deepcopy(before)
    after["oracle_version"] = "new-oracle"
    for name, report in (("before", before), ("after", after)):
        (tmp_path / f"{name}.json").write_text(json.dumps(report), encoding="utf-8")
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "driverforge",
            "diff",
            str(tmp_path / "before.json"),
            str(tmp_path / "after.json"),
            "--output",
            str(tmp_path / "diff"),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    assert run.returncode == 1, run.stdout + run.stderr
    assert json.loads(run.stdout)["changes"][0]["field"] == "oracle_version"
