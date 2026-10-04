# Proposed next steps

The applicable deterministic Must requirements are complete. These are follow-up
proposals, not retroactive changes to the completed acceptance gate.

1. **Automate regression checks.** Start with the verified Windows/Python 3.12
   environment and pinned lock. Run lint, formatting, types, all 94 tests, wheel
   build and the offline demo. Preserve reports when a run fails. A green hosted
   run should reproduce the declared outcomes; add other platforms only after
   verifying them, rather than implying portability from local results.
2. **Test usefulness with a practitioner and a second driver.** Ask an instrument
   developer to install the wheel in their own project and diagnose a seeded
   fault using only the documentation. Record setup time, confusing steps and
   changes required. Add one licensed existing driver through its established
   adapter seam. Keep expected values independent and retain failed examples.
   Success means repeatable adoption and a useful diagnosis without package edits.
3. **Clarify the existing integration contract.** The retained malformed and
   device-error failures demonstrate a synthetic numeric consumer mismatch, not
   a proven instrument or upstream defect. Separate wire responses from error
   queue behavior using the manufacturer contract and PyMeasure behavior. Add
   justified checks without deleting the original failures or weakening their
   expectations; propose an upstream fix only if an actual defect is established.
4. **Validate available hardware later.** If access is arranged, begin with one
   read-only operation and compare actual bytes and units with the replay. Label
   those measurements separately from synthetic fixtures. No purchase is needed
   for the current release, and hardware access remains unarranged.

Keep model generation deferred. Before executing any generated candidate, establish
and test a real file/network/credential isolation boundary; before paid evaluation,
obtain an explicit API budget. Neither is required for the current test kit.

The blog stays a draft. Practitioner evidence and contract clarification can improve
it before a separately authorized publication; source availability alone does not
establish hardware validation or practitioner adoption.
