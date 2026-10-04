"""Measure a trusted workload in a fresh process; Windows peak working set."""

import argparse
import ctypes
import json
import runpy
import sys
import time
from ctypes import wintypes
from pathlib import Path


def peak_memory():
    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    if not psapi.GetProcessMemoryInfo(
        kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return counters.PeakWorkingSetSize


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workload", choices=["baseline", "core", "upstream"])
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    code = 0
    try:
        if args.workload == "baseline":
            runpy.run_path("examples/baseline/run_baseline.py", run_name="__main__")
        else:
            sys.argv = ["driverforge", "--worker"]
            if args.workload == "core":
                sys.argv += ["demo", "--offline", "--output", str(args.output)]
            else:
                sys.argv += [
                    "check",
                    "agilent34410a",
                    "--spec",
                    "examples/specs/agilent34410a.json",
                    "--output",
                    str(args.output),
                ]
            runpy.run_module("driverforge", run_name="__main__")
    except SystemExit as exc:
        code = exc.code
    measured = {
        "workload": args.workload,
        "elapsed_seconds": time.perf_counter() - started,
        "peak_working_set_bytes": peak_memory(),
        "exit_code": code,
        "measurement": "fresh trusted worker; excludes parent supervisor",
    }
    args.result.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(measured))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
