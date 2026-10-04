"""Installable pytest fixture; consumers need no internal imports."""
from collections.abc import Callable

import pytest

from .transport import FaultTransport


@pytest.fixture
def driverforge_transport() -> Callable[..., FaultTransport]:
    """Factory for a new deterministic transport per test/case."""
    return FaultTransport
