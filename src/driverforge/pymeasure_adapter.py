"""Inject the existing PyMeasure adapter seam; leave driver source unchanged."""
from importlib.metadata import version
from typing import Any

from pymeasure.adapters import Adapter
from pymeasure.instruments.agilent import Agilent34410A

from .errors import InvalidInput, UnsupportedOperation
from .transport import FaultTransport


class PyMeasureFaultAdapter(Adapter):  # type: ignore[misc]
    """Simulate an LF connection, without adding parsing/retry logic upstream lacks."""
    unsupported_capabilities = ("async_cancellation", "upstream_framing_validation", "read_retry")

    def __init__(self, transport: FaultTransport) -> None:
        super().__init__()
        self.transport = transport
        self.connection = transport
        self.pending: tuple[str, bytes] | None = None

    def _write(self, command: str, **kwargs: Any) -> None:
        if self.pending is not None:
            raise InvalidInput("read pending; preserve operation ordering")
        raw = (command + "\n").encode("ascii")
        operation = next((name for name, pair in self.transport.dialogues.items() if pair[0] == raw), None)
        if operation is None:
            raise UnsupportedOperation(command)
        self.pending = (operation, raw)

    def _read(self, **kwargs: Any) -> str:
        if self.pending is None:
            raise InvalidInput("read without write")
        operation, raw = self.pending
        self.pending = None
        response = self.transport.exchange(operation, raw)
        # The adapter models configured read termination; it does not upgrade the
        # upstream driver's validation. Raw transcript includes the terminator.
        return response.removesuffix(b"\n").removesuffix(b"\r").decode("ascii")


def agilent34410a(transport: FaultTransport) -> Any:
    """Construct the pinned public driver with an in-memory transport."""
    if version("pymeasure") != "0.16.0":
        raise InvalidInput("integration contract requires PyMeasure 0.16.0")
    return Agilent34410A(PyMeasureFaultAdapter(transport))
