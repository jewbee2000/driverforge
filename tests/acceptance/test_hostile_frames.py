import json
from pathlib import Path

import pytest

from driverforge import ProtocolSpec, asset, factory_for, run_campaign

# Frozen evaluator fixture. No production codec computes expected values.
CASES = json.loads(Path("evaluation/cases.json").read_text())["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_independent_contract_case(case):
    profile = case["profile"]
    result = run_campaign(factory_for(profile), ProtocolSpec.load(asset(profile + ".json")), [case])
    assert result.exit_code == 0, result.to_dict()
