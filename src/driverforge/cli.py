"""Scriptable built-in trusted checks. Arbitrary generated Python is disabled."""
import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .campaign import (CampaignResult, CaseResult, factory_for, reference_cases,
                       run_campaign, validate_cases, Factory)
from .errors import InvalidInput
from .mutations import MUTATIONS
from .report import compare_reports, digest, dump, safe_output, write_report
from .spec import ProtocolSpec, asset, load_json


def incomplete(output: Path, detail: str, command: list[str]) -> int:
    output = safe_output(output)
    result = CampaignResult(complete=False, cases=[CaseResult("execution", "execute", "DF-19",
        "inconclusive", None, None, detail, [], {"anchor": "input", "passage": detail}, {}, 0, 0)])
    payload = dump(result.to_dict())
    for name in ("conformance.json", "manifest.json"):
        if (output / name).is_symlink() or (output / name).is_junction():
            raise InvalidInput("artifact link forbidden")
    (output / "conformance.json").write_text(payload, encoding="utf-8", newline="\n")
    (output / "manifest.json").write_text(dump({"schema_version": 1, "exit_code": 2,
        "command": command, "complete": False, "detail": detail,
        "artifact_sha256": {"conformance.json": digest(payload.encode())}}), encoding="utf-8", newline="\n")
    print(dump({"exit_code": 2, "detail": detail}).strip())
    return 2


def load_campaign(path: Path, profile: str) -> list[dict[str, Any]]:
    data = load_json(path)
    if not isinstance(data, dict) or set(data) != {"schema_version", "profile", "cases"}:
        raise InvalidInput("campaign requires schema_version, profile, cases")
    if data["schema_version"] != 1 or data["profile"] != profile:
        raise InvalidInput("unknown campaign version or profile mismatch")
    validate_cases(data["cases"])
    return list(data["cases"])


def check(args: argparse.Namespace, command: list[str]) -> int:
    spec = ProtocolSpec.load(args.spec)
    factory: Factory
    if args.driver in MUTATIONS:
        factory = MUTATIONS[args.driver][0]
        if spec.profile != ("thermoblock" if args.driver == "swallowed_device_error" else "pressurebrick"):
            raise InvalidInput("mutation profile mismatch")
    else:
        if args.driver != spec.profile:
            raise InvalidInput("driver/profile mismatch or unsupported candidate")
        factory = factory_for(spec.profile)
    cases = load_campaign(args.campaign, spec.profile) if args.campaign else (
        load_json(asset("agilent_cases.json"))["cases"] if spec.profile == "agilent34410a" else reference_cases(spec.profile))
    result = run_campaign(factory, spec, cases, oracle_version="1.0.0" if not args.campaign else "caller-defined")
    extras: dict[str, Any] = {"ambiguities": [asdict(a) for a in spec.ambiguities()]}
    if spec.profile == "agilent34410a":
        import inspect
        from pymeasure.instruments.agilent import Agilent34410A
        from .pymeasure_adapter import PyMeasureFaultAdapter
        extras["unsupported_capabilities"] = [dict(capability=c, state="not_applicable",
            reason="outside declared synchronous upstream contract") for c in PyMeasureFaultAdapter.unsupported_capabilities]
        upstream_file = inspect.getsourcefile(Agilent34410A)
        assert upstream_file is not None
        extras["upstream"] = dict(package="pymeasure", version="0.16.0",
            commit="597e0c6760288f6fe1c5a677e9d53a2b7a033566",
            source_sha256=digest(Path(upstream_file).read_bytes()), modified=False)
    write_report(args.output, result, spec, factory, command=command, extras=extras,
                 campaign_input={"schema_version": 1, "profile": spec.profile, "cases": cases})
    print(dump({"exit_code": result.exit_code, "cases": len(result.cases), "output": str(args.output)}).strip())
    return result.exit_code


def demo(args: argparse.Namespace, command: list[str]) -> int:
    if not args.offline:
        raise InvalidInput("only --offline REPLAY is implemented")
    good = CampaignResult(oracle_version="1.0.0")
    for profile in ("thermoblock", "pressurebrick"):
        spec = ProtocolSpec.load(asset(profile + ".json"))
        good.cases.extend(run_campaign(factory_for(profile), spec, reference_cases(profile), oracle_version="1.0.0").cases)
    negatives = {}
    rejected = True
    for name, (factory, case_id) in MUTATIONS.items():
        profile = "thermoblock" if name == "swallowed_device_error" else "pressurebrick"
        cases = [c for c in reference_cases(profile) if c["id"] == case_id]
        spec = ProtocolSpec.load(asset(profile + ".json"))
        bad = run_campaign(factory, spec, cases, oracle_version="1.0.0")
        negatives[name] = bad.to_dict()
        rejected &= bad.exit_code == 1
        write_report(args.output / "failures" / name, bad, spec, factory, command=command,
            campaign_input={"schema_version": 1, "profile": profile, "cases": cases})
    # Explicit missing-source example is preserved, not guessed or generated.
    doc = load_json(asset("pressurebrick.json"))
    del doc["operations"]["read_temperature"]["fields"]["scale"]
    ambiguity = ProtocolSpec.from_dict(doc).ambiguities()
    extras = {"mutations": negatives, "ambiguities": [asdict(a) for a in ambiguity],
              "live_generation": "not run; no authorized model budget", "isolation": "disabled"}
    if not rejected or not ambiguity:
        good.complete = False
    spec = ProtocolSpec.load(asset("pressurebrick.json"))
    write_report(args.output, good, spec, factory_for("pressurebrick"), command=command, extras=extras,
        campaign_input={"schema_version": 1, "profile": "two-fictional-profiles", "cases": load_json(asset("cases.json"))["cases"]})
    print(dump({"exit_code": good.exit_code, "reference_cases": len(good.cases),
                "mutations_rejected": sum(r["exit_code"] == 1 for r in negatives.values()),
                "output": str(args.output)}).strip())
    return good.exit_code


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Deterministic local instrument fault campaigns")
    root.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    root.add_argument("--wall-seconds", type=float, default=10, help="trusted worker limit, 0 < seconds <= 10")
    commands = root.add_subparsers(dest="command", required=True)
    d = commands.add_parser("demo")
    d.add_argument("--offline", action="store_true")
    d.add_argument("--output", type=Path, default=Path("artifacts/demo"))
    c = commands.add_parser("check")
    c.add_argument("driver", help="thermoblock, pressurebrick, agilent34410a, or reviewed mutation name")
    c.add_argument("--spec", required=True, type=Path)
    c.add_argument("--campaign", type=Path)
    c.add_argument("--output", type=Path, default=Path("artifacts/check"))
    diff = commands.add_parser("diff")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    diff.add_argument("--output", type=Path, default=Path("artifacts/diff"))
    return root


def main(argv: list[str] | None = None) -> int:
    tokens = sys.argv[1:] if argv is None else argv
    args = parser().parse_args(tokens)
    command = ["python", "-m", "driverforge", *[t for t in tokens if t != "--worker"]]
    try:
        safe_output(args.output)
        if not 0 < args.wall_seconds <= 10:
            raise InvalidInput("wall limit must be in (0, 10]")
        if not args.worker:
            try:
                completed = subprocess.run([sys.executable, "-m", "driverforge", "--worker", *tokens],
                                           timeout=args.wall_seconds)
                return completed.returncode if completed.returncode in (0, 1, 2) else incomplete(args.output, "worker failed", command)
            except subprocess.TimeoutExpired:
                return incomplete(args.output, "trusted worker wall limit exceeded; incomplete", command)
        if args.command == "check":
            return check(args, command)
        if args.command == "demo":
            return demo(args, command)
        changes = compare_reports(load_json(args.before, 4 * 1024 * 1024), load_json(args.after, 4 * 1024 * 1024))
        print(dump({"schema_version": 1, "changes": changes}).strip())
        return 1 if changes else 0
    except Exception as exc:
        try:
            return incomplete(args.output, f"{type(exc).__name__}: {exc}", command)
        except Exception:
            print(dump({"exit_code": 2, "detail": str(exc)}).strip(), file=sys.stderr)
            return 2
