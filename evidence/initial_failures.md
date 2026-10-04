# Preserved development failures

2026-10-04: Before product implementation, `pytest tests/acceptance/test_golden_bytes.py -q`
failed at collection with ModuleNotFoundError: driverforge. The independent golden
assertions were authored first. They were not weakened after implementation.

The first baseline run passed a ResourceManager object to VISAAdapter's
visa_library parameter. PyVISA raised AttributeError: ResourceManager has no
attribute rsplit. Correction: supply the YAML@sim library string per the adapter
signature. This is a setup error, not an upstream driver defect.
