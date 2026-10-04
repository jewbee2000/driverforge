import copy

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
