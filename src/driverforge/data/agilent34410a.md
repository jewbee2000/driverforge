# agilent34410a

independently authored synthetic integration contract, MIT. No physical measurements.

Unchanged PyMeasure 0.16.0 Agilent34410A, commit 597e0c6760288f6fe1c5a677e9d53a2b7a033566.
Commands/units: https://pymeasure.readthedocs.io/en/stable/api/instruments/agilent/agilent34410A.html
Manufacturer syntax: https://www.keysight.com/us/en/assets/9018-61141/programming-guides/9018-61141.pdf
250 ms is this test fixture's deadline, not a manufacturer performance guarantee.
MEAS commands trigger acquisition/configuration; no automatic retry assumed.
Async cancellation and upstream framing checks are unsupported. Fault bytes are synthetic.

## voltage-dc

request="MEAS:VOLT:DC? DEF,DEF\\n"; response="finite_scalar"; unit="V"; scale=1; signed=true; range=null; timeout_ms=250; retry=0; side_effect="trigger_measurement"

## current-dc

request="MEAS:CURR:DC? DEF,DEF\\n"; response="finite_scalar"; unit="A"; scale=1; signed=true; range=null; timeout_ms=250; retry=0; side_effect="trigger_measurement"

## resistance

request="MEAS:RES? DEF,DEF\\n"; response="finite_scalar"; unit="ohm"; scale=1; signed=false; range=null; timeout_ms=250; retry=0; side_effect="trigger_measurement"


## lifecycle

Fictional reads retry once within 500 ms; uncertain writes are never replayed. Cancellation discards pending response and closes; close is idempotent. sampled_at is unknown; received_at is fake host receipt time.
