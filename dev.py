#!/usr/bin/env python3
"""Start the FastAPI app, then the Angular dev server.

Usage (from the repo root, with the project virtualenv active):

    python dev.py
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
API_URL = "http://127.0.0.1:8000"
READY_TEXT = "Application startup complete."


def stop(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGINT)
    except ProcessLookupError:
        return


def wait_for_exit(process: subprocess.Popen[str], timeout: float = 5) -> int:
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return process.wait()


def forward_until_ready(process: subprocess.Popen[str], ready: threading.Event) -> None:
    assert process.stdout is not None
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        if READY_TEXT in line:
            ready.set()


def wait_until_ready(process: subprocess.Popen[str], ready: threading.Event, timeout: float = 30) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ready.is_set():
            return True
        if process.poll() is not None:
            return False
        time.sleep(0.1)
    return ready.is_set()


def main() -> int:
    print(f"Starting API on {API_URL}", flush=True)
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
        cwd=ROOT,
        start_new_session=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    ready = threading.Event()
    reader = threading.Thread(target=forward_until_ready, args=(backend, ready), daemon=True)
    reader.start()

    if not wait_until_ready(backend, ready):
        stop(backend)
        code = wait_for_exit(backend)
        reader.join(timeout=2)
        print("API did not start, so the Angular app was not started.", file=sys.stderr)
        return code

    print("Starting Angular app on http://localhost:4200", flush=True)
    try:
        frontend = subprocess.Popen(
            ["npm", "run", "start"],
            cwd=WEB,
            start_new_session=True,
        )
    except FileNotFoundError:
        stop(backend)
        wait_for_exit(backend)
        print("npm was not found on PATH.", file=sys.stderr)
        return 1

    processes = (backend, frontend)

    def shutdown(_signum: int, _frame: object) -> None:
        for process in processes:
            stop(process)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    exit_code = 0
    try:
        while True:
            for process in processes:
                code = process.poll()
                if code is not None:
                    exit_code = code
                    return exit_code
            time.sleep(0.25)
    finally:
        shutdown(signal.SIGTERM, None)
        for process in processes:
            wait_for_exit(process)


if __name__ == "__main__":
    raise SystemExit(main())
