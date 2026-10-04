"""Versioned explicit specifications; ambiguities block dependent execution."""
import json
import math
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .errors import InvalidInput, ResourceLimit

MAX_INPUT_BYTES = 65536
FIELDS = ("request", "response", "unit", "scale", "signed", "range", "timeout_ms", "retry", "side_effect")


def asset(name: str) -> Path:
    return Path(str(files("driverforge").joinpath("data", name)))


def load_json(path: Path, max_bytes: int = MAX_INPUT_BYTES) -> Any:
    with path.open("rb") as stream:
        raw = stream.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ResourceLimit(f"input exceeds {max_bytes} bytes")
    try:
        return json.loads(raw, parse_constant=lambda value: reject_constant(value))
    except (ValueError, UnicodeDecodeError) as exc:
        raise InvalidInput("invalid UTF-8 JSON") from exc


def reject_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON number {value}")


@dataclass(frozen=True)
class Ambiguity:
    operation: str
    field: str
    reason: str
    sources: list[dict[str, str]]
    outcome: str = "inconclusive"


@dataclass(frozen=True)
class ProtocolSpec:
    document: dict[str, Any]

    @classmethod
    def load(cls, path: Path) -> "ProtocolSpec":
        return cls.from_dict(load_json(path))

    @classmethod
    def from_dict(cls, document: Any) -> "ProtocolSpec":
        schema = json.loads(files("driverforge").joinpath("schemas", "spec-v1.json").read_text())
        errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda e: str(e.path))
        if errors:
            raise InvalidInput("spec schema: " + errors[0].message)
        return cls(document)

    @property
    def profile(self) -> str:
        return str(self.document["profile"])

    def ambiguities(self) -> list[Ambiguity]:
        result = []
        for operation, command in self.document["operations"].items():
            fields = command["fields"]
            for name in FIELDS:
                entry = fields.get(name, {})
                sources = entry.get("sources") or [command["source"]]
                reason = ""
                if "values" in entry:
                    reason = "contradictory source values"
                elif "value" not in entry or entry.get("status") == "unresolved":
                    reason = "missing or unresolved critical field"
                elif not entry.get("sources"):
                    reason = "missing field source anchors"
                elif not self._valid_field(name, entry["value"]):
                    reason = "invalid critical field value"
                if reason:
                    result.append(Ambiguity(operation, name, reason, sources))
            effect = fields.get("side_effect", {}).get("value")
            retries = fields.get("retry", {}).get("value")
            if effect != "read" and isinstance(retries, int) and retries > 0:
                result.append(Ambiguity(operation, "retry", "side-effecting operation cannot auto-retry",
                                        fields["retry"].get("sources") or [command["source"]]))
        return result

    @staticmethod
    def _valid_field(name: str, value: Any) -> bool:
        if name in {"unit", "request", "response"}:
            return isinstance(value, str) and bool(value)
        if name == "scale":
            return type(value) in (int, float) and math.isfinite(value) and value > 0
        if name == "signed":
            return type(value) is bool or value == "not_applicable"
        if name == "range":
            return value is None or (isinstance(value, list) and len(value) == 2 and
                all(type(v) in (int, float) and math.isfinite(v) for v in value) and value[0] <= value[1])
        if name == "timeout_ms":
            return type(value) is int and 0 < value <= 500
        if name == "retry":
            return type(value) is int and 0 <= value <= 1
        return value in ("read", "write", "trigger_measurement")

    def require_resolved(self) -> None:
        if self.ambiguities():
            raise InvalidInput("unresolved spec; see structured ambiguities")
