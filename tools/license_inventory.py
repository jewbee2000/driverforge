"""Record installed pinned dependency licensing from distribution metadata."""

import importlib.metadata
import json
from pathlib import Path

rows = []
for line in Path("requirements.lock").read_text(encoding="utf-8-sig").splitlines():
    name, version = line.split("==")
    dist = importlib.metadata.distribution(name)
    metadata = dist.metadata
    license_files = [
        str(p)
        for p in dist.files or ()
        if "license" in str(p).lower() or "copying" in str(p).lower()
    ]
    declared = metadata.get("License-Expression") or "; ".join(
        c.removeprefix("License :: ")
        for c in metadata.get_all("Classifier", [])
        if c.startswith("License :: ")
    )
    if not declared:
        declared = metadata.get("License", "not declared in metadata")
    rows.append(
        {
            "name": name,
            "version": version,
            "declared_license": declared,
            "license_files": license_files,
        }
    )
Path("evidence/licenses.json").write_text(
    json.dumps(rows, indent=2) + "\n", encoding="utf-8", newline="\n"
)
print(f"Recorded {len(rows)} pinned distributions")
