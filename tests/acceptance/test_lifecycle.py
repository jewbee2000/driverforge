import pytest

from driverforge import Cancelled, Closed, Fault, FaultTransport, PressureBrick


def test_close_and_cancel_prevent_late_reuse():
    transport = FaultTransport({"read_temperature": (bytes.fromhex("0300000001"), bytes.fromhex("0302fb2e"))},
                               (Fault("cancel", "read_temperature", delay_ms=1),))
    driver = PressureBrick(transport)
    with pytest.raises(Cancelled):
        driver.read_temperature()
    with pytest.raises(Closed):
        driver.read_temperature()
    driver.close()
    driver.close()
    assert transport.counts["read_temperature"] == 1
    assert [e["event"] for e in transport.transcript].count("close") == 1
    assert any(e["event"] == "discard_late" for e in transport.transcript)
