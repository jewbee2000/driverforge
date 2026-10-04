"""Synthetic cases for unchanged PyMeasure public driver. Literal expectations."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cases = []
for op, request, response, value in [
    ("voltage_dc", b"MEAS:VOLT:DC? DEF,DEF\n", b"1.250\n", 1.25),
    ("current_dc", b"MEAS:CURR:DC? DEF,DEF\n", b"0.012\n", 0.012),
    ("resistance", b"MEAS:RES? DEF,DEF\n", b"1000\n", 1000.0),
]:
    cases.append(
        {
            "id": op,
            "operation": op,
            "request_hex": request.hex(),
            "response_hex": response.hex(),
            "expected": value,
            "error": None,
            "attempts": 1,
            "requirement": "DF-14",
        }
    )
for name, fault, value, error in [
    ("timeout", {"kind": "timeout", "onset": 1}, None, "DeadlineExceeded"),
    (
        "fragment",
        {"kind": "fragment", "onset": 1, "chunks_hex": ["312e", "3235300a"], "delay_ms": 1},
        1.25,
        None,
    ),
    (
        "malformed",
        {"kind": "malformed", "onset": 1, "data_hex": "676172626167650a"},
        None,
        "ParseError",
    ),
    (
        "device-error",
        {
            "kind": "device_error",
            "onset": 1,
            "data_hex": "2d3130312c496e76616c6964206368617261637465720a",
        },
        None,
        "DeviceError",
    ),
    (
        "late",
        {"kind": "late", "onset": 1, "data_hex": "312e3235300a", "delay_ms": 251},
        None,
        "DeadlineExceeded",
    ),
]:
    cases.append(
        {
            "id": name,
            "operation": "voltage_dc",
            "request_hex": "4d4541533a564f4c543a44433f204445462c4445460a",
            "response_hex": "312e3235300a",
            "expected": value,
            "error": error,
            "faults": [fault],
            "attempts": 1,
            "requirement": "DF-14",
        }
    )
for path in ("examples/agilent_campaign.json", "src/driverforge/data/agilent_cases.json"):
    (ROOT / path).write_text(
        json.dumps({"schema_version": 1, "profile": "agilent34410a", "cases": cases}, indent=2)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
