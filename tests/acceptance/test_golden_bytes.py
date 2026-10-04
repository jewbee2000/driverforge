"""Independent expectations written before the driver implementation."""
from driverforge import FaultTransport, PressureBrick, ThermoBlock


def test_signed_register():
    wire = FaultTransport({"read_temperature": (bytes.fromhex("0300000001"), bytes.fromhex("0302fb2e"))})
    value = PressureBrick(wire).read_temperature()
    assert value.value == -12.34
    assert value.unit == "C" and value.sampled_at is None


def test_voltage_scaling_and_pressure():
    wire = FaultTransport({"set_voltage": (bytes.fromhex("06001004e2"), bytes.fromhex("06001004e2")),
                           "read_pressure": (bytes.fromhex("0300010001"), bytes.fromhex("0302007b"))})
    driver = PressureBrick(wire)
    driver.set_voltage(1.250)
    assert driver.read_pressure().value == 12.3
    assert wire.transcript[0]["data_hex"] == "06001004e2"


def test_ascii_vector():
    wire = FaultTransport({"set_voltage": (b"SOUR:VOLT 1.250\n", b"OK\n")})
    ThermoBlock(wire).set_voltage(1.250)
    assert wire.transcript[0]["data_hex"] == "534f55523a564f4c5420312e3235300a"
