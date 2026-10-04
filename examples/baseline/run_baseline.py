"""Pinned existing-tool experiment, independent of DriverForge."""
import json
import time
from pathlib import Path

import pyvisa
from pymeasure.adapters import VISAAdapter
from pymeasure.instruments.agilent import Agilent34410A
from pymeasure.test import expected_protocol

OPERATIONS = [
    ("voltage_dc", "MEAS:VOLT:DC? DEF,DEF", "1.250", 1.25),
    ("current_dc", "MEAS:CURR:DC? DEF,DEF", "0.012", 0.012),
    ("resistance", "MEAS:RES? DEF,DEF", "1000", 1000.0),
]


def main():
    started = time.perf_counter()
    results = []
    with expected_protocol(Agilent34410A, [(q, r) for _, q, r, _ in OPERATIONS]) as driver:
        for op, q, r, expected in OPERATIONS:
            actual = getattr(driver, op)
            assert actual == expected
            results.append(dict(tool="expected_protocol", operation=op, request=q,
                                response=r, actual=actual, terminators="excluded"))
    rm = pyvisa.ResourceManager(str(Path(__file__).with_name("agilent.yaml")) + "@sim")
    adapter = VISAAdapter("GPIB::1::INSTR", visa_library=str(Path(__file__).with_name("agilent.yaml")) + "@sim",
                          read_termination="\n", write_termination="\n", timeout=50)
    driver = Agilent34410A(adapter)
    for op, q, r, expected in OPERATIONS:
        actual = getattr(driver, op)
        assert actual == expected
        results.append(dict(tool="pyvisa-sim", operation=op, request=q + "\n",
                            response=r + "\n", actual=actual))
    adapter.close()
    rm.close()
    # A malformed response is already expressible with ordinary protocol pairs.
    with expected_protocol(Agilent34410A, [(OPERATIONS[0][1], "garbage")]) as driver:
        actual = driver.voltage_dc
        assert actual == "garbage"
        results.append(dict(tool="expected_protocol", fault="malformed", actual=actual,
                            observation="upstream returns text; explicit scalar contract rejects it"))
    output = {"pymeasure": "0.16.0", "pyvisa_sim": "0.7.1", "results": results,
              "elapsed_seconds": time.perf_counter() - started}
    Path("evidence/baseline.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
