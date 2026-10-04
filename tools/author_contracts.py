"""One-time fixture authoring. Literal expected values; no production imports/codecs.

This is an open evaluation suite, not a held-out dataset. Changing it requires a
new oracle revision and invalidates earlier comparisons.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


cases = []


def case(id, profile, op, req, response, expected=None, error=None, **extra):
    cases.append(
        dict(
            id=id,
            profile=profile,
            operation=op,
            request_hex=req,
            response_hex=response,
            expected=expected,
            error=error,
            requirement=extra.pop("requirement", "DF-04"),
            **extra,
        )
    )


# Hand calculated seeds: 0xFB2E = 64302; 64302 - 65536 = -1234.
# 1.250 V * 1000 = 1250 = 0x04E2. 0x007B * 0.1 = 12.3 kPa.
case(
    "signed",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "0302fb2e",
    -12.34,
    requirement="DF-03",
)
case(
    "pressure",
    "pressurebrick",
    "read_pressure",
    "0300010001",
    "0302007b",
    12.3,
    requirement="DF-03",
)
case(
    "voltage",
    "pressurebrick",
    "set_voltage",
    "06001004e2",
    "06001004e2",
    args=[1.25],
    requirement="DF-03",
)
case(
    "zero",
    "pressurebrick",
    "set_voltage",
    "0600100000",
    "0600100000",
    args=[0.0],
    requirement="DF-03",
)
case(
    "upper",
    "pressurebrick",
    "set_voltage",
    "0600101388",
    "0600101388",
    args=[5.0],
    requirement="DF-03",
)
case(
    "illegal-address",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "8302",
    error="IllegalAddress",
)
case(
    "pdu-truncated", "pressurebrick", "read_temperature", "0300000001", "0302fb", error="ParseError"
)
case(
    "pdu-trailing",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "0302fb2e00",
    error="ParseError",
)
case(
    "pdu-bytecount",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "0301fb2e",
    error="ParseError",
)
case(
    "pdu-function",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "0402fb2e",
    error="ParseError",
)
case(
    "bad-echo",
    "pressurebrick",
    "set_voltage",
    "06001004e2",
    "06001004e3",
    error="ParseError",
    args=[1.25],
)
case(
    "write-timeout",
    "pressurebrick",
    "set_voltage",
    "06001004e2",
    None,
    error="UnknownWriteOutcome",
    args=[1.25],
    attempts=1,
    requirement="DF-05",
)
case(
    "read-retry",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "0302fb2e",
    -12.34,
    faults=[{"kind": "timeout", "onset": 1}],
    attempts=2,
    elapsed_ms=250,
    requirement="DF-05",
)
case(
    "read-budget",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    None,
    error="DeadlineExceeded",
    attempts=2,
    elapsed_ms=500,
    requirement="DF-05",
)
case(
    "late-after-timeout",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "03020064",
    1.0,
    faults=[{"kind": "late", "onset": 1, "data_hex": "0302fb2e", "delay_ms": 251}],
    attempts=2,
    elapsed_ms=250,
    requirement="DF-06",
)
case(
    "cancel",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "0302fb2e",
    error="Cancelled",
    faults=[{"kind": "cancel", "onset": 1, "delay_ms": 10}],
    attempts=1,
    after="Closed",
    requirement="DF-06",
)
case(
    "fragment",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "0302fb2e",
    -12.34,
    faults=[{"kind": "fragment", "onset": 1, "chunks_hex": ["03", "02fb", "2e"], "delay_ms": 1}],
    requirement="DF-15",
)
case(
    "deadline-equal",
    "pressurebrick",
    "read_temperature",
    "0300000001",
    "0302fb2e",
    -12.34,
    delay_ms=250,
    elapsed_ms=250,
    requirement="DF-05",
)
case(
    "identify",
    "thermoblock",
    "identify",
    "2a49444e3f0a",
    "57414c542c544845524d4f424c4f434b2d54312c303030312c312e300a",
    "WALT,THERMOBLOCK-T1,0001,1.0",
    requirement="DF-02",
)
case(
    "ascii-temperature",
    "thermoblock",
    "read_temperature",
    "4d4541533a54454d503f0a",
    "2d31322e33340a",
    -12.34,
    requirement="DF-03",
)
case("crlf", "thermoblock", "read_temperature", "4d4541533a54454d503f0a", "312e30300d0a", 1.0)
case(
    "ascii-voltage",
    "thermoblock",
    "set_voltage",
    "534f55523a564f4c5420312e3235300a",
    "4f4b0a",
    args=[1.25],
    requirement="DF-03",
)
case(
    "disable", "thermoblock", "disable_output", "4f555450204f46460a", "4f4b0a", requirement="DF-02"
)
for name, response in [
    ("nan", "NaN\n"),
    ("infinity", "inf\n"),
    ("units", "1.0 F\n"),
    ("no-terminator", "1.0"),
    ("extra-frame", "1.0\n2.0\n"),
    ("malformed", "garbage\n"),
    ("whitespace", " 1.0\n"),
]:
    case(
        name,
        "thermoblock",
        "read_temperature",
        "4d4541533a54454d503f0a",
        response.encode().hex(),
        error="ParseError",
    )
case(
    "encoding",
    "thermoblock",
    "read_temperature",
    "4d4541533a54454d503f0a",
    "ff0a",
    error="ParseError",
)
case(
    "overlong",
    "thermoblock",
    "read_temperature",
    "4d4541533a54454d503f0a",
    "31" * 256 + "0a",
    error="ParseError",
)
case(
    "device-error",
    "thermoblock",
    "read_temperature",
    "4d4541533a54454d503f0a",
    "4552522c322c4661756c740a",
    error="DeviceError",
)
for profile in ("thermoblock", "pressurebrick"):
    for name, arg in [("negative", -0.001), ("above", 5.001), ("precision", 1.2345)]:
        case(
            profile + "-" + name,
            profile,
            "set_voltage",
            "",
            None,
            error="ValueError",
            args=[arg],
            attempts=0,
        )
manifest = {
    "schema_version": 1,
    "oracle_version": "1.0.0",
    "label": "synthetic open evaluation",
    "cases": cases,
}
write("evaluation/cases.json", manifest)
write("src/driverforge/data/cases.json", manifest)
ambiguities = [
    {"id": "missing-" + f, "field": f, "action": "missing", "expected": "inconclusive"}
    for f in ["unit", "scale", "signed", "range", "retry", "side_effect", "timeout_ms", "request"]
]
ambiguities += [
    {
        "id": "conflicting-scale",
        "field": "scale",
        "action": "contradictory",
        "expected": "inconclusive",
    },
    {"id": "missing-anchor", "field": "unit", "action": "anchor", "expected": "inconclusive"},
    {"id": "write-retry", "field": "retry", "action": "write_retry", "expected": "inconclusive"},
]
write("evaluation/ambiguities.json", ambiguities)
write(
    "evaluation/frozen.json",
    {
        "oracle_version": "1.0.0",
        "sha256": hashlib.sha256((ROOT / "evaluation/cases.json").read_bytes()).hexdigest(),
        "ambiguities_sha256": hashlib.sha256(
            (ROOT / "evaluation/ambiguities.json").read_bytes()
        ).hexdigest(),
    },
)
