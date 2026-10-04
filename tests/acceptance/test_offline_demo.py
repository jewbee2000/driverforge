import json
import os
import subprocess
import sys


def test_demo_without_credentials_and_with_python_socket_egress_denied(tmp_path):
    guard = tmp_path / "guard"
    guard.mkdir()
    # Audit denial covers Python socket creation/connect/lookup, inherited by worker.
    # This is a local offline verification boundary, not generated-code isolation.
    (guard / "sitecustomize.py").write_text(
        "import sys\n"
        "def deny(event,args):\n"
        "    if event.startswith('socket.'):\n"
        "        raise PermissionError('offline egress disabled')\n"
        "sys.addaudithook(deny)\n"
    )
    env = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "COMSPEC", "PATHEXT"}
    }
    env["PYTHONPATH"] = str(guard)
    probe = subprocess.run(
        [sys.executable, "-c", "import socket; socket.create_connection(('example.com',80))"],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert probe.returncode != 0 and "offline egress disabled" in probe.stderr
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "driverforge",
            "demo",
            "--offline",
            "--output",
            str(tmp_path / "demo"),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    data = json.loads((tmp_path / "demo/manifest.json").read_text())
    assert data["mode"] == "REPLAY" and data["live_model_evaluation"] is False
