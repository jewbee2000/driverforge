# Preserved development failures

2026-10-04: Before product implementation, `pytest tests/acceptance/test_golden_bytes.py -q`
failed at collection with ModuleNotFoundError: driverforge. The independent golden
assertions were authored first. They were not weakened after implementation.

The first baseline run passed a ResourceManager object to VISAAdapter's
visa_library parameter. PyVISA raised AttributeError: ResourceManager has no
attribute rsplit. Correction: supply the YAML@sim library string per the adapter
signature. This is a setup error, not an upstream driver defect.

First integrated acceptance run: 60 passed, one failed because the annotation
check incorrectly referenced `signature.empty` instead of `Signature.empty`.
Corrected the test's introspection API; expected capabilities and annotations
remain unchanged. An initial type pass also caught tuple inference, an optional
response assignment, and an untyped escaping lambda; repaired explicit typing.

Final documentation audit: a Windows helper used the default cp1252 codec to read
UTF-8 task/requirement text. The status reconciliation corrupted punctuation and
failed to match the requirement headings; the final task-count probe exposed a
UnicodeDecodeError. Restored the original UTF-8 contracts from the pre-update
commit, fixed the helper's explicit encoding, and reapplied only executed status
updates. Verified all 22 headings/statuses and an uncorrupted completed task list.
No wire vectors, expected results, driver behavior or acceptance criteria changed.
