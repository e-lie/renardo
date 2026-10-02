#!/usr/bin/env python3
"""Smoke test of an installed Renardo Tauri bundle, from the outside.

Usage: bundle_smoke.py <path to the installed renardo executable>

Launches the app, finds the uvicorn server it spawned, checks /health, the
served front page and the 127.0.0.1 bind, then closes the app and checks that
no server process (python, scsynth, sclang) is left. Requires psutil."""

import subprocess
import sys
import time
import urllib.request

import psutil

STARTUP_TIMEOUT = 90
SHUTDOWN_TIMEOUT = 20
AUDIO_NAMES = ("scsynth", "sclang")


def log(msg):
    print(f"smoke: {msg}", flush=True)


def fail(msg):
    log(f"FAIL {msg}")
    sys.exit(1)


def find_server(app):
    """The uvicorn process in the app's process tree, with its port."""
    try:
        procs = app.children(recursive=True)
    except psutil.NoSuchProcess:
        return None, None
    for proc in procs:
        try:
            cmd = proc.cmdline()
        except psutil.Error:
            continue
        if "uvicorn" in cmd and "--port" in cmd:
            return proc, int(cmd[cmd.index("--port") + 1])
    return None, None


def get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as r:
        return r.status, r.read().decode("utf-8", "replace")


def listening_ips(server):
    """Addresses the server listens on; falls back to lsof where psutil is denied (macOS)."""
    try:
        ips = [c.laddr.ip for c in server.net_connections(kind="inet") if c.status == psutil.CONN_LISTEN]
    except psutil.AccessDenied:
        out = subprocess.run(
            ["lsof", "-nP", "-a", "-p", str(server.pid), "-iTCP", "-sTCP:LISTEN", "-Fn"],
            capture_output=True, text=True,
        ).stdout
        ips = [line[1:].rsplit(":", 1)[0] for line in out.splitlines() if line.startswith("n")]
    if not ips:
        fail("server is not listening")
    return ips


def wait_healthy(app):
    deadline = time.time() + STARTUP_TIMEOUT
    while time.time() < deadline:
        if not app.is_running():
            fail("app exited during startup")
        server, port = find_server(app)
        if port:
            try:
                if get(port, "/health")[0] == 200:
                    return server, port
            except OSError:
                pass
        time.sleep(0.5)
    fail("server did not answer /health in time")


def close_app(app):
    """Ask the app to close like a user would, so it runs its shutdown."""
    if sys.platform == "win32":
        # without /F, taskkill posts WM_CLOSE to the app window
        subprocess.run(["taskkill", "/PID", str(app.pid)], capture_output=True)
    else:
        app.terminate()


def main():
    exe = sys.argv[1]
    log(f"launching {exe}")
    app = psutil.Process(subprocess.Popen([exe]).pid)

    server, port = wait_healthy(app)
    log(f"server healthy on port {port}")
    tree = [server] + server.children(recursive=True)

    status, body = get(port, "/")
    if status != 200 or "<html" not in body.lower():
        fail("front page not served")
    log("front page served")

    for ip in listening_ips(server):
        if ip != "127.0.0.1":
            fail(f"server bound on {ip}, expected 127.0.0.1")
    log("bound on 127.0.0.1 only")

    close_app(app)
    try:
        app.wait(SHUTDOWN_TIMEOUT)
    except psutil.TimeoutExpired:
        fail("app did not exit after close")

    time.sleep(1)
    alive = []
    for proc in tree:
        try:
            if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                alive.append(f"{proc.name()} ({proc.pid})")
        except psutil.NoSuchProcess:
            pass
    for proc in psutil.process_iter(["name"]):
        if (proc.info["name"] or "").lower().split(".")[0] in AUDIO_NAMES:
            alive.append(f"{proc.info['name']} ({proc.pid})")
    if alive:
        fail("processes left after close: " + ", ".join(alive))
    log("no process left after close")
    log("OK")


if __name__ == "__main__":
    main()
