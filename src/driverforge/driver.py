"""Hand-authored fictional reference drivers; independent of evaluator vectors."""
import math
import re
from dataclasses import dataclass
from decimal import Decimal

from .errors import (DeadlineExceeded, DeviceError, IllegalAddress, ParseError,
                     UnknownWriteOutcome, UnsupportedOperation)
from .transport import FaultTransport


@dataclass(frozen=True)
class Measurement:
    value: float
    unit: str
    sampled_at: float | None
    received_at: float
    quality: str = "simulated"


def voltage_counts(volts: float) -> int:
    if not math.isfinite(volts) or not 0 <= volts <= 5:
        raise ValueError("voltage must be finite and in 0..5 V")
    counts = Decimal(str(volts)) * 1000
    if counts != counts.to_integral_value():
        raise ValueError("voltage resolution is 0.001 V")
    return int(counts)


class ReferenceDriver:
    capabilities: frozenset[str] = frozenset()

    def __init__(self, transport: FaultTransport) -> None:
        self.transport = transport

    def _request(self, operation: str, request: bytes, write: bool = False) -> bytes:
        for attempt in range(1 if write else 2):
            try:
                return self.transport.exchange(operation, request)
            except DeadlineExceeded as exc:
                if write:
                    raise UnknownWriteOutcome("transmitted write timed out; do not replay") from exc
                if attempt == 1:
                    raise
        raise AssertionError("unreachable")

    def _measurement(self, value: float, unit: str) -> Measurement:
        return Measurement(value, unit, None, self.transport.clock.milliseconds / 1000)

    def close(self) -> None:
        self.transport.close()

    def cancel(self) -> None:
        self.transport.cancel()

    def unsupported(self, operation: str) -> None:
        raise UnsupportedOperation(operation)


class ThermoBlock(ReferenceDriver):
    """Fictional ASCII fixture. Methods match its declared capability set."""
    capabilities = frozenset({"identify", "read_temperature", "set_voltage", "disable_output"})

    def _line(self, operation: str, request: bytes, write: bool = False) -> str:
        raw = self._request(operation, request, write)
        if len(raw) > 256 or not raw.endswith(b"\n") or raw.count(b"\n") != 1:
            raise ParseError("exactly one terminated frame required")
        body = raw[:-1]
        if body.endswith(b"\r"):
            body = body[:-1]
        try:
            text = body.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ParseError("response is not ASCII") from exc
        if "\r" in text:
            raise ParseError("embedded carriage return")
        if text.startswith("ERR,"):
            if re.fullmatch(r"ERR,-?\d+,[^,\r\n]+", text) is None:
                raise ParseError("malformed error response")
            raise DeviceError(text)
        return text

    def identify(self) -> str:
        text = self._line("identify", b"*IDN?\n")
        if re.fullmatch(r"[A-Z0-9-]+,[A-Z0-9-]+,[0-9]+,[0-9.]+", text) is None:
            raise ParseError("malformed identification")
        return text

    def read_temperature(self) -> Measurement:
        text = self._line("read_temperature", b"MEAS:TEMP?\n")
        if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text) is None:
            raise ParseError("finite Celsius decimal required")
        value = float(text)
        if not math.isfinite(value):
            raise ParseError("nonfinite temperature")
        return self._measurement(value, "C")

    def set_voltage(self, volts: float) -> None:
        counts = voltage_counts(volts)
        request = f"SOUR:VOLT {counts / 1000:.3f}\n".encode("ascii")
        if self._line("set_voltage", request, True) != "OK":
            raise ParseError("write acknowledgment must be OK")

    def disable_output(self) -> None:
        if self._line("disable_output", b"OUTP OFF\n", True) != "OK":
            raise ParseError("write acknowledgment must be OK")


class PressureBrick(ReferenceDriver):
    """Fictional big-endian register PDU fixture; no TCP/RTU framing."""
    capabilities = frozenset({"read_temperature", "read_pressure", "set_voltage"})

    def _register(self, operation: str, address: int, signed: bool) -> int:
        request = b"\x03" + address.to_bytes(2, "big") + b"\x00\x01"
        raw = self._request(operation, request)
        if len(raw) == 2 and raw[0] == 0x83:
            if raw[1] == 2:
                raise IllegalAddress("exception 0x83 0x02")
            raise DeviceError(f"register exception {raw[1]}")
        if len(raw) != 4 or raw[:2] != b"\x03\x02":
            raise ParseError("single-register response required")
        return int.from_bytes(raw[2:], "big", signed=signed)

    def read_temperature(self) -> Measurement:
        return self._measurement(self._register("read_temperature", 0, True) / 100, "C")

    def read_pressure(self) -> Measurement:
        return self._measurement(self._register("read_pressure", 1, False) / 10, "kPa")

    def set_voltage(self, volts: float) -> None:
        request = b"\x06\x00\x10" + voltage_counts(volts).to_bytes(2, "big")
        raw = self._request("set_voltage", request, True)
        if len(raw) == 2 and raw[0] == 0x86:
            raise DeviceError(f"write exception {raw[1]}")
        if raw != request:
            raise ParseError("write echo differs")
