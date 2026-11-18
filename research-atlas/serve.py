"""Serve the local atlas and refresh generated evidence when research inputs change."""

import argparse
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent


def source_signature():
    files = [SITE / "topics.json", SITE / "build.py"]
    for pattern in ("*.md", "*.py", "*.c", "results/*.csv", "results/four_bit/*"):
        files.extend(path for path in ROOT.glob(pattern) if path.is_file())
    return tuple((p, p.stat().st_mtime_ns, p.stat().st_size) for p in sorted(files))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8764)
    args = parser.parse_args()
    lock = threading.Lock()
    last_built = None

    def refresh():
        nonlocal last_built
        with lock:
            signature = source_signature()
            if signature != last_built:
                subprocess.run(["uv", "run", "--script", str(SITE / "build.py")], cwd=ROOT, check=True)
                last_built = signature

    class AtlasHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(SITE / "dist"), **kwargs)

        def end_headers(self):
            self.send_header("Cache-Control", "no-cache")
            super().end_headers()

        def send_head(self):
            try:
                refresh()
            except (OSError, subprocess.CalledProcessError):
                self.send_error(503, "Atlas rebuild failed. Check the server log and refresh after fixing the input.")
                return None
            return super().send_head()

    refresh()
    with ThreadingHTTPServer(("127.0.0.1", args.port), AtlasHandler) as server:
        print(f"Difference Atlas is available at http://127.0.0.1:{server.server_port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
