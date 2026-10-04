"""Escaped local evidence reports; inputs are data, never executable content."""

import hashlib
import html
import inspect
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .campaign import CampaignResult, Factory
from .errors import InvalidInput, ResourceLimit
from .spec import ProtocolSpec, asset


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def dump(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n"


def safe_output(path: Path) -> Path:
    if ".." in path.parts:
        raise InvalidInput("output traversal is forbidden")
    absolute = path.absolute()
    for part in (absolute, *absolute.parents):
        if part.is_symlink() or part.is_junction():
            raise InvalidInput("output links/junctions are forbidden")
    absolute.mkdir(parents=True, exist_ok=True)
    return absolute


def render_html(result: dict[str, Any], title: str, extras: dict[str, Any] | None = None) -> str:
    def escape(value: Any) -> str:
        return html.escape(str(value), quote=True)

    rows = []
    for case in result["cases"]:
        trace = "\n".join(
            f"{e['at_ms']:>3} ms {e['event']:<12} {e['data_hex']}" for e in case["transcript"]
        )
        rows.append(
            f"<article class='{escape(case['state'])}'><h2>{escape(case['id'])} · {escape(case['state'])}</h2>"
            f"<p>{escape(case['operation'])} · {escape(case['requirement'])}</p>"
            f"<p><b>Expected:</b> {escape(case['expected'])} <b>Observed:</b> {escape(case['observed'])}</p>"
            f"<p>{escape(case['detail'])}</p><details><summary>Source → interpretation → wire</summary>"
            f"<p>{escape(case['source']['anchor'])}</p><blockquote>{escape(case['source']['passage'])}</blockquote>"
            f"<pre>{escape(dump(case['interpreted_fields']))}</pre><pre>{escape(trace)}</pre></details></article>"
        )
    return (
        "<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
        "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; style-src 'unsafe-inline'\">"
        f"<title>{escape(title)}</title><style>body{{font:16px system-ui;background:#f5f6f9;color:#17223a;max-width:1000px;margin:32px auto;padding:0 16px}}"
        "article{background:white;padding:16px;margin:16px 0;border-left:6px solid #14775e;border-radius:8px}"
        ".fail{border-color:#bf3645}.inconclusive{border-color:#ad750e}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef1f7;padding:12px}"
        "h1{font-size:32px}h2{font-size:20px}blockquote{margin:0;padding:12px;background:#eef1f7}</style>"
        f"<h1>{escape(title)}</h1><p>REPLAY · synthetic traffic · no hardware or live model evaluation</p>"
        f"<p>Exit {escape(result['exit_code'])} · Complete {escape(result['complete'])} · {len(result['cases'])} cases</p>"
        + "".join(rows)
        + f"<h2>Run context and preserved attempts</h2><pre>{escape(dump(extras or {}))}</pre></html>"
    )


def source_context() -> dict[str, Any]:
    root = Path.cwd()
    command = ["git", "-c", f"safe.directory={root.as_posix()}"]
    try:
        commit = subprocess.run(
            [*command, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=2, check=False
        )
        dirty = subprocess.run(
            [*command, "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        diff = subprocess.run(
            [*command, "diff", "--no-ext-diff", "--binary", "HEAD"],
            capture_output=True,
            timeout=2,
            check=False,
        )
        return {
            "commit": commit.stdout.strip() if commit.returncode == 0 else "unavailable",
            "dirty": bool(dirty.stdout),
            "dirty_diff_sha256": digest(diff.stdout)
            if dirty.stdout and diff.returncode == 0
            else None,
            "git_available": commit.returncode == 0,
        }
    except (OSError, subprocess.TimeoutExpired):
        return {
            "commit": "unavailable",
            "dirty": None,
            "dirty_diff_sha256": None,
            "git_available": False,
        }


def write_report(
    output: Path,
    result: CampaignResult,
    spec: ProtocolSpec,
    factory: Factory,
    *,
    command: list[str],
    extras: dict[str, Any] | None = None,
    campaign_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output = safe_output(output)
    candidate = inspect.getsourcefile(factory)
    candidate_raw = Path(candidate).read_bytes() if candidate else b"source unavailable"
    documents = {
        "spec.json": dump(spec.document),
        "candidate.py": candidate_raw.decode("utf-8"),
        "conformance.json": dump(result.to_dict()),
        "report.html": render_html(result.to_dict(), "DriverForge conformance", extras),
        "context.json": dump(extras or {}),
        "campaign.json": dump(
            campaign_input or {"schema_version": 1, "profile": spec.profile, "cases": []}
        ),
    }
    if sum(len(v.encode()) for v in documents.values()) > 4 * 1024 * 1024:
        raise ResourceLimit("report exceeds 4 MiB")
    hashes = {}
    for name, content in documents.items():
        target = output / name
        if target.is_symlink() or target.is_junction():
            raise InvalidInput("artifact link forbidden")
        target.write_text(content, encoding="utf-8", newline="\n")
        hashes[name] = digest(target.read_bytes())
    source_hashes = {
        name: digest(asset(name).read_bytes())
        for name in (
            "cases.json",
            "thermoblock.md",
            "pressurebrick.md",
            "agilent34410a.md",
            "requirements.lock",
            "thermoblock.json",
            "pressurebrick.json",
            "agilent34410a.json",
            "agilent_cases.json",
        )
    }
    package = Path(__file__).parent
    package_hashes = {p.name: digest(p.read_bytes()) for p in sorted(package.glob("*.py"))}
    package_hashes.update(
        {
            f"schemas/{p.name}": digest(p.read_bytes())
            for p in sorted((package / "schemas").glob("*.json"))
        }
    )
    manifest = {
        "schema_version": 1,
        "mode": "REPLAY",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "command": command,
        "exit_code": result.exit_code,
        "source": source_context(),
        "candidate_sha256": digest(candidate_raw),
        "input_sha256": hashes["spec.json"],
        "campaign_sha256": hashes["campaign.json"],
        "oracle_version": result.oracle_version,
        "oracle_sha256": source_hashes["cases.json"],
        "environment_lock_sha256": source_hashes["requirements.lock"],
        "evaluator_sha256": digest(Path(__file__).with_name("campaign.py").read_bytes()),
        "python": sys.version,
        "platform": platform.platform(),
        "package_version": version("driverforge"),
        "source_hashes": source_hashes,
        "package_hashes": package_hashes,
        "package_sha256": digest(dump(package_hashes).encode()),
        "artifact_sha256": hashes,
        "untrusted_execution": "disabled: isolation unavailable",
        "physical_validation": False,
        "live_model_evaluation": False,
    }
    manifest_path = output / "manifest.json"
    if manifest_path.is_symlink() or manifest_path.is_junction():
        raise InvalidInput("manifest link forbidden")
    manifest_path.write_text(dump(manifest), encoding="utf-8", newline="\n")
    return manifest


def compare_reports(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare by stable case + operation + requirement; include exact wire differences."""
    schema = json.loads(files("driverforge").joinpath("schemas", "result-v1.json").read_text())
    for data in (before, after):
        errors = list(Draft202012Validator(schema).iter_errors(data))
        if errors:
            raise InvalidInput("result schema: " + errors[0].message)

    def keyed(data: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
        return {(c["id"], c["operation"], c["requirement"]): c for c in data["cases"]}

    a, b = keyed(before), keyed(after)
    changes = []
    for field in ("complete", "exit_code", "oracle_version"):
        if before[field] != after[field]:
            changes.append(
                {
                    "scope": "report",
                    "case": None,
                    "operation": None,
                    "requirement": None,
                    "field": field,
                    "before": before[field],
                    "after": after[field],
                }
            )
    for key in sorted(a.keys() | b.keys()):
        old, new = a.get(key), b.get(key)
        for field in (
            "state",
            "expected",
            "observed",
            "detail",
            "attempts",
            "elapsed_ms",
            "source",
            "interpreted_fields",
            "transcript",
        ):
            left = old.get(field) if old else None
            right = new.get(field) if new else None
            if left != right:
                changes.append(
                    {
                        "case": key[0],
                        "operation": key[1],
                        "requirement": key[2],
                        "field": field,
                        "before": left,
                        "after": right,
                    }
                )
    return changes
