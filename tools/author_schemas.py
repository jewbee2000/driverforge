"""Version 1 public campaign/result schema; authoring tool, not runtime."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src/driverforge/schemas"
fault = {
    "type": "object",
    "required": ["kind", "onset"],
    "additionalProperties": False,
    "properties": {
        "kind": {"enum": ["timeout", "fragment", "malformed", "device_error", "late", "cancel"]},
        "onset": {"type": "integer", "minimum": 1},
        "data_hex": {"type": "string", "pattern": "^(?:[0-9a-fA-F]{2})*$"},
        "chunks_hex": {
            "type": "array",
            "maxItems": 256,
            "items": {"type": "string", "pattern": "^(?:[0-9a-fA-F]{2})*$"},
        },
        "delay_ms": {"type": "integer", "minimum": 0, "maximum": 10000},
    },
}
case = {
    "type": "object",
    "required": ["id", "operation", "request_hex", "response_hex", "expected", "error"],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "profile": {"type": "string"},
        "operation": {"type": "string", "minLength": 1},
        "request_hex": {"type": "string", "pattern": "^(?:[0-9a-fA-F]{2})*$", "maxLength": 512},
        "response_hex": {
            "type": ["string", "null"],
            "pattern": "^(?:[0-9a-fA-F]{2})*$",
            "maxLength": 2048,
        },
        "expected": {"type": ["number", "string", "boolean", "null"]},
        "error": {"type": ["string", "null"]},
        "args": {"type": "array", "maxItems": 1, "items": {"type": "number"}},
        "requirement": {"type": "string", "pattern": "^DF-(?:0[1-9]|1[0-9]|2[0-2])$"},
        "faults": {"type": "array", "maxItems": 16, "items": fault},
        "attempts": {"type": "integer", "minimum": 0, "maximum": 100},
        "elapsed_ms": {"type": "integer", "minimum": 0},
        "delay_ms": {"type": "integer", "minimum": 0, "maximum": 10000},
        "after": {"const": "Closed"},
    },
}
campaign = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["schema_version", "profile", "cases"],
    "additionalProperties": False,
    "properties": {
        "schema_version": {"const": 1},
        "profile": {"type": "string"},
        "cases": {"type": "array", "minItems": 1, "maxItems": 100, "items": case},
    },
}
case_result = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "id",
        "operation",
        "requirement",
        "state",
        "expected",
        "observed",
        "detail",
        "transcript",
        "source",
        "interpreted_fields",
        "attempts",
        "elapsed_ms",
    ],
    "properties": {key: {} for key in ["expected", "observed", "source", "interpreted_fields"]},
}
case_result["properties"].update(
    {key: {"type": "string"} for key in ["id", "operation", "requirement", "detail"]}
)
case_result["properties"].update(
    state={"enum": ["pass", "fail", "inconclusive", "not_applicable"]},
    transcript={"type": "array"},
    attempts={"type": "integer", "minimum": 0},
    elapsed_ms={"type": "integer", "minimum": 0},
)
result = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "oracle_version", "complete", "cases", "exit_code"],
    "properties": {
        "schema_version": {"const": 1},
        "oracle_version": {"type": "string"},
        "complete": {"type": "boolean"},
        "cases": {"type": "array", "maxItems": 100, "items": case_result},
        "exit_code": {"enum": [0, 1, 2]},
    },
}
for name, schema in [("campaign", campaign), ("result", result)]:
    (ROOT / f"{name}-v1.json").write_text(
        json.dumps(schema, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
