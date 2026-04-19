"""
One-click launcher for AuthentiCheck web UI.
Works on Windows, macOS, and Linux.
Kills any existing instance on port 5000 before starting.
"""
import os
import sys
import signal
import socket
import subprocess
import platform
import time
import webbrowser
from pathlib import Path

PORT = 5000
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}"


def kill_port(port: int):
    system = platform.system()
    try:
        if system == "Windows":
            result = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid],
                                   capture_output=True)
                    print(f"Killed existing process (PID {pid}) on port {port}")
        else:
            result = subprocess.run(
                ["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True
            )
            pids = result.stdout.strip().splitlines()
            for pid in pids:
                os.kill(int(pid), signal.SIGTERM)
                print(f"Killed existing process (PID {pid}) on port {port}")
    except Exception as e:
        print(f"Note: could not kill existing process — {e}")


def wait_for_server(host: str, port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def main():
    print("=" * 48)
    print("  AuthentiCheck — One-Click Launcher")
    print("=" * 48)

    # Change to project root so relative paths work
    os.chdir(Path(__file__).parent)

    # Kill any process already using the port
    kill_port(PORT)
    time.sleep(0.5)

    # Launch Flask app
    python = sys.executable
    app_path = Path("app.py")
    if not app_path.exists():
        print("Error: app.py not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Starting server on {URL} ...")
    proc = subprocess.Popen(
        [python, str(app_path)],
        env={**os.environ, "FLASK_ENV": "production"},
    )

    # Wait for server to be ready, then open browser
    if wait_for_server(HOST, PORT):
        print(f"Server ready — opening {URL}")
        webbrowser.open(URL)
    else:
        print("Warning: server did not respond in time. Try opening manually:")
        print(f"  {URL}")

    print("\nPress Ctrl+C to stop the server.\n")
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        proc.terminate()
        proc.wait()
        print("Done.")


if __name__ == "__main__":
    main()
