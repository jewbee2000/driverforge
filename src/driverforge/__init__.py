"""DriverForge's public deterministic API."""

from .campaign import CampaignResult, CaseResult, factory_for, reference_cases, run_campaign
from .driver import Measurement, PressureBrick, ThermoBlock
from .errors import (
    Cancelled,
    Closed,
    DeadlineExceeded,
    DeviceError,
    IllegalAddress,
    InvalidInput,
    ParseError,
    ResourceLimit,
    UnknownWriteOutcome,
    UnsupportedOperation,
)
from .spec import Ambiguity, ProtocolSpec, asset
from .transport import FakeClock, Fault, FaultTransport

__all__ = [
    "Ambiguity",
    "CampaignResult",
    "Cancelled",
    "CaseResult",
    "Closed",
    "DeadlineExceeded",
    "DeviceError",
    "FakeClock",
    "Fault",
    "FaultTransport",
    "IllegalAddress",
    "InvalidInput",
    "Measurement",
    "ParseError",
    "PressureBrick",
    "ProtocolSpec",
    "ResourceLimit",
    "ThermoBlock",
    "UnknownWriteOutcome",
    "UnsupportedOperation",
    "asset",
    "factory_for",
    "reference_cases",
    "run_campaign",
]
