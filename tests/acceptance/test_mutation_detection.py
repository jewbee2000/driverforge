from driverforge import ProtocolSpec, asset, reference_cases, run_campaign
from driverforge.mutations import MUTATIONS


def test_all_six_mutations_rejected_for_intended_case():
    assert len(MUTATIONS) == 6
    for name, (candidate, case_id) in MUTATIONS.items():
        profile = "thermoblock" if name == "swallowed_device_error" else "pressurebrick"
        case = next(c for c in reference_cases(profile) if c["id"] == case_id)
        result = run_campaign(candidate, ProtocolSpec.load(asset(profile + ".json")), [case])
        assert result.exit_code == 1, name
        assert result.cases[0].state == "fail"
        if name == "blind_write_retry":
            assert result.cases[0].attempts == 2
            assert "transmissions" in result.cases[0].detail
        if name == "unsigned_decode":
            assert result.cases[0].observed == 643.02
        if name == "stale_response_reuse":
            assert result.cases[0].observed == -12.34
