"""Author explicit synthetic contracts and versioned JSON schemas."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["request", "response", "unit", "scale", "signed", "range", "timeout_ms", "retry", "side_effect"]
PROFILES = {
    "thermoblock": {
        "identify": ["*IDN?\\n", "identity", "none", 1, "not_applicable", None, 250, 1, "read"],
        "read_temperature": ["MEAS:TEMP?\\n", "ascii_decimal", "C", 1, True, None, 250, 1, "read"],
        "set_voltage": ["SOUR:VOLT {volts:.3f}\\n", "OK", "V", 0.001, False, [0, 5], 250, 0, "write"],
        "disable_output": ["OUTP OFF\\n", "OK", "none", 1, "not_applicable", None, 250, 0, "write"],
    },
    "pressurebrick": {
        "read_temperature": ["0300000001", "0302{register}", "C", 0.01, True, [-327.68, 327.67], 250, 1, "read"],
        "read_pressure": ["0300010001", "0302{register}", "kPa", 0.1, False, [0, 6553.5], 250, 1, "read"],
        "set_voltage": ["060010{register}", "echo", "V", 0.001, False, [0, 5], 250, 0, "write"],
    },
    "agilent34410a": {
        "voltage_dc": ["MEAS:VOLT:DC? DEF,DEF\\n", "finite_scalar", "V", 1, True, None, 250, 0, "trigger_measurement"],
        "current_dc": ["MEAS:CURR:DC? DEF,DEF\\n", "finite_scalar", "A", 1, True, None, 250, 0, "trigger_measurement"],
        "resistance": ["MEAS:RES? DEF,DEF\\n", "finite_scalar", "ohm", 1, False, None, 250, 0, "trigger_measurement"],
    },
}


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


for profile, commands in PROFILES.items():
    label = "fictional project fixture, MIT" if profile != "agilent34410a" else "independently authored synthetic integration contract, MIT"
    manual = f"# {profile}\n\n{label}. No physical measurements.\n\n"
    if profile == "agilent34410a":
        manual += ("Unchanged PyMeasure 0.16.0 Agilent34410A, commit 597e0c6760288f6fe1c5a677e9d53a2b7a033566.\n"
                   "Commands/units: https://pymeasure.readthedocs.io/en/stable/api/instruments/agilent/agilent34410A.html\n"
                   "Manufacturer syntax: https://www.keysight.com/us/en/assets/9018-61141/programming-guides/9018-61141.pdf\n"
                   "250 ms is this test fixture's deadline, not a manufacturer performance guarantee.\n"
                   "MEAS commands trigger acquisition/configuration; no automatic retry assumed.\n"
                   "Async cancellation and upstream framing checks are unsupported. Fault bytes are synthetic.\n\n")
    operations = {}
    for name, values in commands.items():
        passage = "; ".join(f"{field}={json.dumps(value)}" for field, value in zip(FIELDS, values))
        anchor = f"manuals/{profile}.md#{name.replace('_', '-')}"
        source = {"anchor": anchor, "passage": passage}
        operations[name] = {"source": source, "fields": {field: {"value": value, "sources": [source]} for field, value in zip(FIELDS, values)}}
        manual += f"## {name.replace('_', '-')}\n\n{passage}\n\n"
    if profile == "thermoblock":
        manual += "## framing\n\nLF requests; LF or CRLF responses; maximum 256 bytes. ERR,<integer>,<message> is an error. Reject extra frames, nonfinite values, unrecognized units, and malformed encodings. Writes require OK. Voltage resolution is 0.001 V.\n"
    if profile == "pressurebrick":
        manual += "## encoding\n\nBig-endian 16-bit PDU only. FB2E means -12.34 C. 1.250 V writes 06001004E2 and requires exact echo. 8302 means IllegalAddress. Voltage resolution is 0.001 V. No CRC or TCP framing.\n"
    manual += "\n## lifecycle\n\nFictional reads retry once within 500 ms; uncertain writes are never replayed. Cancellation discards pending response and closes; close is idempotent. sampled_at is unknown; received_at is fake host receipt time.\n"
    for path in (ROOT / "manuals" / f"{profile}.md", ROOT / "src/driverforge/data" / f"{profile}.md"):
        path.write_text(manual, encoding="utf-8", newline="\n")
    for path in (ROOT / "examples/specs" / f"{profile}.json", ROOT / "src/driverforge/data" / f"{profile}.json"):
        dump(path, dict(schema_version=1, protocol_version="1.0", profile=profile, operations=operations))

source = {"type": "object", "required": ["anchor", "passage"], "additionalProperties": False,
          "properties": {"anchor": {"type": "string", "minLength": 1}, "passage": {"type": "string", "minLength": 1}}}
evidence = {"type": "object", "additionalProperties": False, "properties": {
    "value": {}, "values": {"type": "array", "minItems": 2}, "status": {"enum": ["unresolved"]},
    "sources": {"type": "array", "items": source}}}
spec_schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
               "required": ["schema_version", "protocol_version", "profile", "operations"], "additionalProperties": False,
               "properties": {"schema_version": {"const": 1}, "protocol_version": {"const": "1.0"},
                   "profile": {"enum": list(PROFILES)}, "operations": {"type": "object", "minProperties": 1, "maxProperties": 16,
                       "additionalProperties": {"type": "object", "required": ["source", "fields"], "additionalProperties": False,
                           "properties": {"source": source, "fields": {"type": "object", "additionalProperties": False,
                                                                      "properties": dict.fromkeys(FIELDS, evidence)}}}}}}
dump(ROOT / "src/driverforge/schemas/spec-v1.json", spec_schema)
