import copy
import json
from pathlib import Path

import pytest

from driverforge import InvalidInput, ProtocolSpec, asset

AMBIGUITIES = json.loads(Path("evaluation/ambiguities.json").read_text())


@pytest.mark.parametrize("case", AMBIGUITIES, ids=lambda c: c["id"])
def test_missing_and_conflicting_source(case):
    doc = copy.deepcopy(json.loads(asset("pressurebrick.json").read_text()))
    op = "set_voltage" if case["action"] == "write_retry" else "read_temperature"
    fields = doc["operations"][op]["fields"]
    if case["action"] == "missing":
        del fields[case["field"]]
    elif case["action"] == "contradictory":
        fields["scale"]["values"] = [0.01, 1.0]
    elif case["action"] == "anchor":
        fields["unit"]["sources"] = []
    else:
        fields["retry"]["value"] = 1
    spec = ProtocolSpec.from_dict(doc)
    problems = spec.ambiguities()
    assert any(a.field == case["field"] and a.operation == op for a in problems)
    assert all(a.sources and a.sources[0]["anchor"] and a.outcome == case["expected"] for a in problems)
    with pytest.raises(InvalidInput):
        spec.require_resolved()


def test_unknown_version():
    doc = json.loads(asset("thermoblock.json").read_text())
    doc["schema_version"] = 99
    with pytest.raises(InvalidInput):
        ProtocolSpec.from_dict(doc)


def test_reviewed_specs_are_resolved():
    for profile in ("pressurebrick", "thermoblock", "agilent34410a"):
        assert ProtocolSpec.load(asset(profile + ".json")).ambiguities() == []
