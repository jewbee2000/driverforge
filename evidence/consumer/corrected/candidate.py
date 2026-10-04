"""Standalone consumer example: only documented DriverForge/PyMeasure APIs."""
import json
from pathlib import Path

from driverforge import ProtocolSpec, asset, run_campaign
from driverforge.pymeasure_adapter import agilent34410a
from driverforge.report import write_report


def test_calibrated_voltage(driverforge_transport):
    config = json.loads(Path("consumer.json").read_text())
    case = config["case"]
    assert driverforge_transport({}).clock.milliseconds == 0

    class ConsumerMeter:
        def __init__(self, transport):
            self.upstream = agilent34410a(transport)

        @property
        def voltage_dc(self):
            return self.upstream.voltage_dc * config["calibration_factor"]

    spec = ProtocolSpec.load(asset("agilent34410a.json"))
    result = run_campaign(ConsumerMeter, spec, [case], oracle_version="consumer-1.0")
    write_report(Path("reports") / config["run_name"], result, spec, ConsumerMeter,
                 command=["python", "-m", "pytest", "test_meter.py", "-q"],
                 extras={"consumer_configuration": config},
                 campaign_input={"schema_version": 1, "profile": "agilent34410a", "cases": [case]})
    assert result.exit_code == 0, result.to_dict()
