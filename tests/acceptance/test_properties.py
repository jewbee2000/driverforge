import struct

from hypothesis import given, settings
from hypothesis import strategies as st

from driverforge import FaultTransport, PressureBrick


@given(st.integers(-32768, 32767))
@settings(max_examples=100, derandomize=True)
def test_signed_register_domain(counts):
    # Independent oracle uses struct's network-endian signed pack.
    response = b"\x03\x02" + struct.pack(">h", counts)
    wire = FaultTransport({"read_temperature": (bytes.fromhex("0300000001"), response)})
    measurement = PressureBrick(wire).read_temperature()
    assert measurement.value == counts * 0.01 or abs(measurement.value - counts * 0.01) < 1e-12
    assert measurement.sampled_at is None and measurement.received_at == 0.0


@given(st.integers(0, 5000))
@settings(max_examples=100, derandomize=True)
def test_voltage_domain(counts):
    expected = b"\x06\x00\x10" + struct.pack(">H", counts)
    wire = FaultTransport({"set_voltage": (expected, expected)})
    PressureBrick(wire).set_voltage(counts / 1000)
    assert wire.transcript[0]["data_hex"] == expected.hex()
