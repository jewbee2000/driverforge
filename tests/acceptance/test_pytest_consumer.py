from pathlib import Path

import pytest

from driverforge import FaultTransport


def test_installed_fixture_public_factory(driverforge_transport):
    assert isinstance(driverforge_transport({}), FaultTransport)


@pytest.mark.parametrize(
    "name", ["examples/consumer/test_meter.py", "examples/consumer/consumer.json"]
)
def test_consumer_uses_only_public_api(name):
    text = Path(name).read_text()
    assert "src/driverforge" not in text and "_request" not in text
