import hashlib
import json
from pathlib import Path

from driverforge import asset


def test_inventory_is_frozen_and_independent():
    frozen = json.loads(Path("evaluation/frozen.json").read_text())
    raw = Path("evaluation/cases.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == frozen["sha256"]
    assert asset("cases.json").read_bytes() == raw
    cases = json.loads(raw)["cases"]
    assert len(cases) >= 20 and len({c["id"] for c in cases}) == len(cases)
    assert all("expected" in c and "error" in c and c["requirement"] for c in cases)
    ambiguity_raw = Path("evaluation/ambiguities.json").read_bytes()
    assert hashlib.sha256(ambiguity_raw).hexdigest() == frozen["ambiguities_sha256"]
    assert len(json.loads(ambiguity_raw)) >= 10
