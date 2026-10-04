# pressurebrick

fictional project fixture, MIT. No physical measurements.

## read-temperature

request="0300000001"; response="0302{register}"; unit="C"; scale=0.01; signed=true; range=[-327.68, 327.67]; timeout_ms=250; retry=1; side_effect="read"

## read-pressure

request="0300010001"; response="0302{register}"; unit="kPa"; scale=0.1; signed=false; range=[0, 6553.5]; timeout_ms=250; retry=1; side_effect="read"

## set-voltage

request="060010{register}"; response="echo"; unit="V"; scale=0.001; signed=false; range=[0, 5]; timeout_ms=250; retry=0; side_effect="write"

## encoding

Big-endian 16-bit PDU only. FB2E means -12.34 C. 1.250 V writes 06001004E2 and requires exact echo. 8302 means IllegalAddress. Voltage resolution is 0.001 V. No CRC or TCP framing.

## lifecycle

Fictional reads retry once within 500 ms; uncertain writes are never replayed. Cancellation discards pending response and closes; close is idempotent. sampled_at is unknown; received_at is fake host receipt time.
