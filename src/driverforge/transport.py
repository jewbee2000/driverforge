"""Deterministic, in-memory scheduled transport. No physical I/O."""
from dataclasses import dataclass, field
from typing import Any

from .errors import Cancelled, Closed, DeadlineExceeded, InvalidInput, ParseError


@dataclass
class FakeClock:
    milliseconds: int = 0

    def advance(self, milliseconds: int) -> None:
        if milliseconds < 0:
            raise InvalidInput("negative clock advance")
        self.milliseconds += milliseconds


@dataclass(frozen=True)
class Fault:
    kind: str
    operation: str
    onset: int = 1
    expected_outcome: str = "unspecified"
    data_hex: str = ""
    chunks_hex: tuple[str, ...] = ()
    delay_ms: int = 0

    def __post_init__(self) -> None:
        if self.kind not in {"timeout", "fragment", "malformed", "device_error", "late", "cancel"}:
            raise InvalidInput("unknown fault kind")
        if self.onset < 1 or self.delay_ms < 0 or len(self.chunks_hex) > 256:
            raise InvalidInput("invalid fault onset/delay/chunks")
        for value in (self.data_hex, *self.chunks_hex):
            try:
                bytes.fromhex(value)
            except ValueError as exc:
                raise InvalidInput("fault bytes must be hex") from exc
        if self.kind in {"malformed", "device_error", "late"} and not self.data_hex:
            raise InvalidInput("fault requires response bytes")
        if self.kind == "fragment" and not self.chunks_hex:
            raise InvalidInput("fragment requires chunks")


@dataclass
class FaultTransport:
    dialogues: dict[str, tuple[bytes, bytes | None]]
    faults: tuple[Fault, ...] = ()
    clock: FakeClock = field(default_factory=FakeClock)
    delay_ms: int = 0
    transcript: list[dict[str, Any]] = field(default_factory=list, init=False)
    counts: dict[str, int] = field(default_factory=dict, init=False)
    closed: bool = field(default=False, init=False)
    pending_late: bytes | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        if len(self.faults) > 16 or self.delay_ms < 0:
            raise InvalidInput("schedule limit exceeded")
        keys = [(f.operation, f.onset) for f in self.faults]
        if len(set(keys)) != len(keys):
            raise InvalidInput("two faults affect the same operation occurrence")
        if any(f.operation not in self.dialogues for f in self.faults):
            raise InvalidInput("fault operation lacks a dialogue")

    def record(self, event: str, operation: str, data: bytes = b"", **extra: Any) -> None:
        self.transcript.append(dict(event=event, operation=operation, data_hex=data.hex(),
                                    at_ms=self.clock.milliseconds, **extra))

    def discard(self, operation: str) -> None:
        if self.pending_late is not None:
            self.record("discard_late", operation, self.pending_late)
            self.pending_late = None

    def exchange(self, operation: str, request: bytes, timeout_ms: int = 250) -> bytes:
        if self.closed:
            raise Closed("transport is closed")
        if not 0 < timeout_ms <= 500:
            raise InvalidInput("deadline must be in 1..500 ms")
        self.discard(operation)
        self.counts[operation] = self.counts.get(operation, 0) + 1
        self.record("send", operation, request, attempt=self.counts[operation])
        if operation not in self.dialogues:
            raise InvalidInput("operation has no dialogue")
        expected, response = self.dialogues[operation]
        if request != expected:
            raise ParseError(f"request differs: expected {expected.hex()}, got {request.hex()}")
        fault = next((f for f in self.faults if f.operation == operation and
                      f.onset == self.counts[operation]), None)
        delay = self.delay_ms
        chunks: tuple[bytes, ...] = (response,) if response is not None else ()
        if fault is not None:
            self.record("fault", operation, kind=fault.kind, onset=fault.onset,
                        expected_outcome=fault.expected_outcome)
            delay = fault.delay_ms
            if fault.kind == "cancel":
                self.clock.advance(min(delay, timeout_ms))
                self.pending_late = response
                self.discard(operation)
                self.close()
                raise Cancelled("pending exchange cancelled; transport closed")
            if fault.kind == "timeout":
                chunks = ()
            elif fault.kind == "late":
                self.pending_late = bytes.fromhex(fault.data_hex)
                chunks = ()
            elif fault.kind == "fragment":
                chunks = tuple(bytes.fromhex(chunk) for chunk in fault.chunks_hex)
            else:
                chunks = (bytes.fromhex(fault.data_hex),)
        total = b""
        remaining = timeout_ms
        if not chunks:
            self.clock.advance(remaining)
            self.record("timeout", operation)
            raise DeadlineExceeded("response deadline exceeded")
        for chunk in chunks:
            if delay > remaining:
                self.clock.advance(remaining)
                self.pending_late = chunk
                self.record("timeout", operation)
                raise DeadlineExceeded("response deadline exceeded")
            self.clock.advance(delay)
            remaining -= delay
            self.record("receive", operation, chunk)
            total += chunk
            if len(total) > 256:
                raise ParseError("response exceeds 256 bytes")
        return total

    def cancel(self) -> None:
        self.discard("cancel")
        self.close()

    def close(self) -> None:
        if not self.closed:
            self.discard("close")
            self.closed = True
            self.record("close", "close")
