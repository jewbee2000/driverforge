"""Six deliberate reviewed defects retained as trusted negative fixtures."""

from .driver import Measurement, PressureBrick, ThermoBlock
from .errors import DeadlineExceeded, DeviceError, UnknownWriteOutcome


class UnsignedDecode(PressureBrick):
    def _register(self, operation: str, address: int, signed: bool) -> int:
        return super()._register(operation, address, False)


class VoltageFactor1000(PressureBrick):
    def set_voltage(self, volts: float) -> None:
        request = b"\x06\x00\x10" + int(volts).to_bytes(2, "big")
        self._request("set_voltage", request, True)


class SwappedBytes(PressureBrick):
    def _register(self, operation: str, address: int, signed: bool) -> int:
        raw = self._request(operation, b"\x03" + address.to_bytes(2, "big") + b"\x00\x01")
        return int.from_bytes(raw[2:], "little", signed=signed)


class BlindWriteRetry(PressureBrick):
    def _request(self, operation: str, request: bytes, write: bool = False) -> bytes:
        try:
            return super()._request(operation, request, write)
        except UnknownWriteOutcome:
            return super()._request(operation, request, write)


class SwallowedDeviceError(ThermoBlock):
    def _line(self, operation: str, request: bytes, write: bool = False) -> str:
        try:
            return super()._line(operation, request, write)
        except DeviceError:
            return "0"


class StaleResponseReuse(PressureBrick):
    def read_temperature(self) -> Measurement:
        try:
            raw = self.transport.exchange("read_temperature", b"\x03\x00\x00\x00\x01")
        except DeadlineExceeded:
            pending = self.transport.pending_late
            if pending is None:
                return super().read_temperature()
            raw = pending
        return self._measurement(int.from_bytes(raw[2:], "big", signed=True) / 100, "C")


MUTATIONS = {
    "unsigned_decode": (UnsignedDecode, "signed"),
    "voltage_factor_1000": (VoltageFactor1000, "voltage"),
    "swapped_bytes": (SwappedBytes, "signed"),
    "blind_write_retry": (BlindWriteRetry, "write-timeout"),
    "swallowed_device_error": (SwallowedDeviceError, "device-error"),
    "stale_response_reuse": (StaleResponseReuse, "late-after-timeout"),
}
