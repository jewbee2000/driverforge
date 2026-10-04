import hashlib
import inspect
import json
from pathlib import Path

from pymeasure.instruments.agilent import Agilent34410A

from driverforge import ProtocolSpec, asset, run_campaign
from driverforge.pymeasure_adapter import PyMeasureFaultAdapter, agilent34410a


def test_unchanged_public_driver_three_operations_and_faults():
    source = Path(inspect.getsourcefile(Agilent34410A))
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    cases = json.loads(Path("examples/agilent_campaign.json").read_text())["cases"]
    result = run_campaign(agilent34410a, ProtocolSpec.load(asset("agilent34410a.json")), cases)
    assert result.exit_code == 1  # actual upstream contract failures stay failures
    by_id = {c.id: c for c in result.cases}
    for case in ("voltage_dc", "current_dc", "resistance", "timeout", "fragment", "late"):
        assert by_id[case].state == "pass", by_id[case]
        assert by_id[case].transcript[0]["event"] == "send"
    assert by_id["malformed"].state == "fail"
    assert by_id["device-error"].state == "fail"
    assert by_id["malformed"].observed == "garbage"
    assert by_id["fragment"].transcript[2]["data_hex"] == "312e"
    assert by_id["timeout"].elapsed_ms == 250 and by_id["timeout"].attempts == 1
    assert source.read_bytes() and hashlib.sha256(source.read_bytes()).hexdigest() == before
    pinned = json.loads(Path("evidence/upstream.json").read_text())
    assert before == pinned["installed_sha256"] == pinned["remote_sha256"]
    assert "async_cancellation" in PyMeasureFaultAdapter.unsupported_capabilities
