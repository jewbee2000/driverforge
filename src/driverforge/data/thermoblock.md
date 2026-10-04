# thermoblock

fictional project fixture, MIT. No physical measurements.

## identify

request="*IDN?\\n"; response="identity"; unit="none"; scale=1; signed="not_applicable"; range=null; timeout_ms=250; retry=1; side_effect="read"

## read-temperature

request="MEAS:TEMP?\\n"; response="ascii_decimal"; unit="C"; scale=1; signed=true; range=null; timeout_ms=250; retry=1; side_effect="read"

## set-voltage

request="SOUR:VOLT {volts:.3f}\\n"; response="OK"; unit="V"; scale=0.001; signed=false; range=[0, 5]; timeout_ms=250; retry=0; side_effect="write"

## disable-output

request="OUTP OFF\\n"; response="OK"; unit="none"; scale=1; signed="not_applicable"; range=null; timeout_ms=250; retry=0; side_effect="write"

## framing

LF requests; LF or CRLF responses; maximum 256 bytes. ERR,<integer>,<message> is an error. Reject extra frames, nonfinite values, unrecognized units, and malformed encodings. Writes require OK. Voltage resolution is 0.001 V.

## lifecycle

Fictional reads retry once within 500 ms; uncertain writes are never replayed. Cancellation discards pending response and closes; close is idempotent. sampled_at is unknown; received_at is fake host receipt time.
