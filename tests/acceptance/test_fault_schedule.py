import pytest

from driverforge import Cancelled, DeadlineExceeded, Fault, FaultTransport, InvalidInput


@pytest.mark.parametrize(
    "fault,expected,error",
    [
        (Fault("timeout", "read", expected_outcome="DeadlineExceeded"), None, DeadlineExceeded),
        (
            Fault("fragment", "read", chunks_hex=("31", "0a"), delay_ms=2, expected_outcome="1\\n"),
            b"1\n",
            None,
        ),
        (Fault("malformed", "read", data_hex="ff", expected_outcome="ParseError"), b"\xff", None),
        (
            Fault("device_error", "read", data_hex="8302", expected_outcome="IllegalAddress"),
            b"\x83\x02",
            None,
        ),
        (
            Fault("late", "read", data_hex="31", delay_ms=251, expected_outcome="DeadlineExceeded"),
            None,
            DeadlineExceeded,
        ),
        (Fault("cancel", "read", delay_ms=10, expected_outcome="Cancelled"), None, Cancelled),
    ],
)
def test_all_faults_are_declarative_and_repeatable(fault, expected, error):
    transcripts = []
    for _ in range(2):
        transport = FaultTransport({"read": (b"q", b"1\n")}, (fault,))
        if error:
            with pytest.raises(error):
                transport.exchange("read", b"q")
        else:
            assert transport.exchange("read", b"q") == expected
        transcripts.append(transport.transcript)
        event = next(e for e in transport.transcript if e["event"] == "fault")
        assert event["onset"] == 1 and event["expected_outcome"] == fault.expected_outcome
    assert transcripts[0] == transcripts[1]


def test_fault_onset_and_ambiguous_schedule():
    transport = FaultTransport({"read": (b"q", b"1")}, (Fault("timeout", "read", onset=2),))
    assert transport.exchange("read", b"q") == b"1"
    with pytest.raises(DeadlineExceeded):
        transport.exchange("read", b"q")
    with pytest.raises(InvalidInput):
        FaultTransport({"read": (b"q", b"1")}, (Fault("timeout", "read"), Fault("cancel", "read")))
