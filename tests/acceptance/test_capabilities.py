from inspect import Signature, signature

import pytest

from driverforge import FaultTransport, PressureBrick, ThermoBlock, UnsupportedOperation


def test_supported_api_annotations_and_explicit_unsupported():
    for cls, capabilities in [(ThermoBlock, {"identify", "read_temperature", "set_voltage", "disable_output"}),
                              (PressureBrick, {"read_temperature", "read_pressure", "set_voltage"})]:
        driver = cls(FaultTransport({}))
        assert cls.capabilities == capabilities
        for method in capabilities:
            assert signature(getattr(cls, method)).return_annotation is not Signature.empty
        with pytest.raises(UnsupportedOperation):
            driver.unsupported("arbitrary_operation")
    assert not hasattr(PressureBrick, "identify")
    assert not hasattr(ThermoBlock, "read_pressure")
