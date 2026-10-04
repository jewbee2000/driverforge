"""Public fault campaigns with independent caller-supplied expectations."""

import json
import math
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator

from .driver import Measurement, PressureBrick, ThermoBlock
from .errors import InvalidInput, UnsupportedOperation
from .spec import ProtocolSpec, asset, load_json
from .transport import Fault, FaultTransport

Factory = Callable[[FaultTransport], Any]
MAX_CASES = 100


@dataclass
class CaseResult:
    id: str
    operation: str
    requirement: str
    state: str
    expected: Any
    observed: Any
    detail: str
    transcript: list[dict[str, Any]]
    source: dict[str, str]
    interpreted_fields: dict[str, Any]
    attempts: int
    elapsed_ms: int


@dataclass
class CampaignResult:
    cases: list[CaseResult] = field(default_factory=list)
    schema_version: int = 1
    oracle_version: str = "caller-defined"
    complete: bool = True

    @property
    def exit_code(self) -> int:
        if (
            not self.complete
            or not self.cases
            or any(c.state == "inconclusive" for c in self.cases)
        ):
            return 2
        if any(c.state == "fail" for c in self.cases):
            return 1
        return 0

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "exit_code": self.exit_code}


def reference_cases(profile: str) -> list[dict[str, Any]]:
    data = load_json(asset("cases.json"))
    return [c for c in data["cases"] if c["profile"] == profile]


def factory_for(profile: str) -> Factory:
    if profile == "thermoblock":
        return ThermoBlock
    if profile == "pressurebrick":
        return PressureBrick
    if profile == "agilent34410a":
        from .pymeasure_adapter import agilent34410a

        return agilent34410a
    raise UnsupportedOperation(profile)


def validate_cases(cases: list[dict[str, Any]]) -> None:
    try:
        encoded = json.dumps(cases, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise InvalidInput("campaign contains non-JSON or nonfinite data") from exc
    if len(encoded) > 65536:
        raise InvalidInput("campaign exceeds 64 KiB")
    schema = json.loads(files("driverforge").joinpath("schemas", "campaign-v1.json").read_text())
    errors = list(
        Draft202012Validator(schema).iter_errors(
            {"schema_version": 1, "profile": "api", "cases": cases}
        )
    )
    if errors:
        raise InvalidInput("campaign schema: " + errors[0].message)
    if not cases or len(cases) > MAX_CASES:
        raise InvalidInput("campaign needs 1..100 cases")
    ids = []
    for case in cases:
        ids.append(case["id"])
        if not isinstance(case["id"], str) or not isinstance(case["operation"], str):
            raise InvalidInput("case id and operation must be strings")
        bytes.fromhex(case["request_hex"])
        if case.get("response_hex") is not None:
            bytes.fromhex(case["response_hex"])
        if len(case.get("faults", [])) > 16:
            raise InvalidInput("too many faults")
        if case.get("attempts", 1) < 0 or case.get("delay_ms", 0) < 0:
            raise InvalidInput("negative limits")
    if len(ids) != len(set(ids)):
        raise InvalidInput("duplicate case IDs")


def run_campaign(
    factory: Factory,
    spec: ProtocolSpec,
    cases: list[dict[str, Any]],
    *,
    oracle_version: str = "caller-defined",
    wall_limit: float = 10,
) -> CampaignResult:
    """Run reviewed local driver callables. This API does not sandbox Python.

    The CLI accepts only built-in reviewed candidates and uses a killable worker.
    API callers are responsible for bounding their own trusted driver execution.
    """
    validate_cases(cases)
    result = CampaignResult(oracle_version=oracle_version)
    started = time.monotonic()
    ambiguities = spec.ambiguities()
    canonical = ProtocolSpec.load(asset(spec.profile + ".json"))
    for case in cases:
        op = case["operation"]
        command = spec.document["operations"].get(op)
        if command is None:
            source = {"anchor": "unsupported", "passage": "Operation absent from contract"}
            fields = {}
        else:
            source, fields = command["source"], command["fields"]
        expected = case.get("error") or case.get("expected")
        if time.monotonic() - started > wall_limit:
            result.complete = False
            result.cases.append(
                CaseResult(
                    case["id"],
                    op,
                    case.get("requirement", "DF-19"),
                    "inconclusive",
                    expected,
                    None,
                    "campaign wall limit exceeded",
                    [],
                    source,
                    {},
                    0,
                    0,
                )
            )
            break
        canonical_command = canonical.document["operations"].get(op)
        incompatible = (
            command is not None
            and canonical_command is not None
            and any(
                command["fields"].get(name, {}).get("value") != evidence["value"]
                for name, evidence in canonical_command["fields"].items()
            )
        )
        if command is None or incompatible or any(a.operation == op for a in ambiguities):
            result.cases.append(
                CaseResult(
                    case["id"],
                    op,
                    case.get("requirement", "DF-01"),
                    "inconclusive",
                    expected,
                    None,
                    "unsupported or unresolved contract",
                    [],
                    source,
                    {},
                    0,
                    0,
                )
            )
            continue
        req = bytes.fromhex(case["request_hex"])
        response = None if case.get("response_hex") is None else bytes.fromhex(case["response_hex"])
        faults = tuple(
            Fault(
                operation=op,
                expected_outcome=str(expected),
                **{**f, "chunks_hex": tuple(f.get("chunks_hex", ()))},
            )
            for f in case.get("faults", [])
        )
        transport = FaultTransport({op: (req, response)}, faults, delay_ms=case.get("delay_ms", 0))
        observed: Any = None
        outcome = None
        state = "pass"
        detail = "contract satisfied"
        driver: Any = None
        crashed = False
        try:
            driver = factory(transport)
            attribute = getattr(driver, op)
            value = attribute(*case.get("args", [])) if callable(attribute) else attribute
            observed = value.value if isinstance(value, Measurement) else value
            if isinstance(observed, float) and not math.isfinite(observed):
                observed = str(observed)
            if isinstance(value, Measurement) and (
                value.sampled_at is not None
                or value.unit != fields["unit"]["value"]
                or value.quality != "simulated"
            ):
                state, detail = "fail", "measurement metadata violates source contract"
        except Exception as exc:  # noqa: BLE001 -- driver boundary preserves failed execution
            outcome = type(exc).__name__
            observed = outcome
            detail = str(exc)
            crashed = outcome not in {
                "ParseError",
                "DeadlineExceeded",
                "UnknownWriteOutcome",
                "DeviceError",
                "IllegalAddress",
                "Cancelled",
                "Closed",
                "ValueError",
            }
        if outcome != case.get("error") or (outcome is None and observed != case.get("expected")):
            state, detail = "fail", f"expected {expected!r}; observed {observed!r}"
        if type(case.get("expected")) in (int, float) and type(observed) not in (int, float):
            state, detail = "fail", "numeric contract requires a finite scalar"
        attempts = transport.counts.get(op, 0)
        if "attempts" in case and attempts != case["attempts"]:
            state, detail = (
                "fail",
                f"expected {case['attempts']} transmissions; observed {attempts}",
            )
        if "elapsed_ms" in case and transport.clock.milliseconds != case["elapsed_ms"]:
            state, detail = "fail", "fake-clock budget differs"
        if case.get("after") == "Closed":
            try:
                driver.read_temperature()
                state, detail = "fail", "cancelled transport reused a stale response"
            except Exception as exc:  # noqa: BLE001 -- lifecycle assertion records actual exception
                if type(exc).__name__ != "Closed":
                    state, detail = "fail", "cancel did not close transport"
        if crashed:
            state, detail = "inconclusive", f"driver execution failed: {outcome}"
        transport.close()
        result.cases.append(
            CaseResult(
                case["id"],
                op,
                case.get("requirement", "DF-19"),
                state,
                expected,
                observed,
                detail,
                transport.transcript,
                source,
                {name: evidence.get("value") for name, evidence in fields.items()},
                attempts,
                transport.clock.milliseconds,
            )
        )
    return result
