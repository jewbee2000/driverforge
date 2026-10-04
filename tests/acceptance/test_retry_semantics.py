import pytest

from driverforge import DeadlineExceeded, Fault, FaultTransport, PressureBrick, UnknownWriteOutcome


def test_two_reads_and_one_uncertain_write():
    wire = FaultTransport({"read_temperature": (bytes.fromhex("0300000001"), None)})
    with pytest.raises(DeadlineExceeded):
        PressureBrick(wire).read_temperature()
    assert wire.counts == {"read_temperature": 2}
    assert wire.clock.milliseconds == 500
    wire = FaultTransport({"set_voltage": (bytes.fromhex("06001004e2"), None)})
    with pytest.raises(UnknownWriteOutcome):
        PressureBrick(wire).set_voltage(1.25)
    assert wire.counts == {"set_voltage": 1} and wire.clock.milliseconds == 250


def test_retry_discards_late_bytes_before_second_request():
    wire = FaultTransport(
        {"read_temperature": (bytes.fromhex("0300000001"), bytes.fromhex("03020064"))},
        (Fault("late", "read_temperature", data_hex="0302fb2e", delay_ms=251),),
    )
    assert PressureBrick(wire).read_temperature().value == 1.0
    events = [e["event"] for e in wire.transcript]
    assert events == ["send", "fault", "timeout", "discard_late", "send", "receive"]
    assert wire.clock.milliseconds == 250
