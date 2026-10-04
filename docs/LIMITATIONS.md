# Known limitations and dispositions

The local deterministic test kit's applicable Must checks pass. This establishes
software behavior on Windows 11 / Python 3.12.2 and the recorded synthetic inputs.
It is not physical validation, a safety/calibration claim, an exhaustive protocol
compliance claim, practitioner adoption, or a live model success rate.

- Unchanged PyMeasure 0.16.0 Agilent34410A returns text/list values on synthetic
  malformed/device-error input; normal check returns exit 1. Those failures are
  retained and unresolved. The kit does not rewrite or claim to repair upstream.
- The one existing-driver adapter models LF string I/O. Upstream async cancellation,
  strict framing validation and automatic retry are explicitly unsupported.
  Fragment assembly is tested at the transport/adapter boundary.
- Reference profiles have fixed reviewed semantics. The consumer can configure
  expected readings and fault schedules; changing fixed reference scaling or
  retry policy yields inconclusive checks. No arbitrary protocol generator exists.
- Cancellation is a deterministic scheduled event, not a real asynchronous
  instrument session. A late response is modeled and discarded; no physical
  serial drain implementation is claimed.
- DF-10: not applicable because untrusted generated-code execution is disabled.
  Docker's daemon was unavailable. Host workers are trusted, killable processes;
  they are not credential/network/file isolation.
- DF-18: deferred. No manual extraction, model generation, repair campaign or paid
  API was run. Replay uses hand-authored checked-in references and explicit defects.
- DF-17: implemented, with unchanged/terminator/scale/attempt diff checks.
- Resource figures describe fresh Windows workers; exclude the supervisor process
  and OS caches. Baseline, core and upstream workloads differ; no universal
  performance comparison or human productivity speedup is justified.
- Dependency downloads need network access. The offline proof uses a Python
  socket audit denial after installation; it is not an OS firewall.
- No automatic discovery, real instrument writes, PDF extraction, full Modbus
  TCP/RTU, every-vendor support, enterprise platform or replacement HAL (DF-W01–05).
- Code and article remain local/unpublished. Hosted URL verification, editorial
  approval, actual publication date and publication require later authorization.
