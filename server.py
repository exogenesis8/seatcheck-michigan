#!/usr/bin/env python3
"""Local server for SeatCheck Michigan: serves the app and runs the research agent.

    .venv/bin/python server.py          # then open http://localhost:8766

Needs Anthropic credentials (ANTHROPIC_API_KEY, or a profile from `ant auth login`) for the agent.
Everything else in the app works without them.
"""
import json
import os
import sys
import traceback
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8766"))


def load_env_file():
    """Read KEY=value lines from .env next to this file (without overriding real env vars)."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if v and not v.startswith("paste-"):
                os.environ.setdefault(k.strip(), v)


load_env_file()


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            return self._json({"agent": True})
        if self.path.split("/")[1].startswith(".") or self.path.endswith(".py"):
            return self.send_error(404)  # don't serve the venv, config, or source
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/research":
            return self.send_error(404)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            fields = json.loads(self.rfile.read(min(length, 100_000)) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self.send_error(400, "Bad JSON")

        # Stream progress as newline-delimited JSON.
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        def emit(obj):
            self.wfile.write((json.dumps(obj) + "\n").encode())
            self.wfile.flush()

        try:
            import anthropic
            from agent import research
            emit({"type": "status", "text": "Starting research…"})
            emit({"type": "result", "findings": research(fields, emit)})
        except BrokenPipeError:
            pass
        except Exception as e:  # report every failure to the page in plain words
            msg = str(e)
            try:
                import anthropic
                if isinstance(e, anthropic.AuthenticationError) or "api_key" in msg.lower() or "credentials" in msg.lower():
                    msg = "No valid Anthropic API key. Set ANTHROPIC_API_KEY and restart the server."
                elif isinstance(e, anthropic.RateLimitError):
                    msg = "Rate limited by the Anthropic API. Wait a minute and try again."
                elif isinstance(e, anthropic.APIConnectionError):
                    msg = "Couldn't reach the Anthropic API. Check the internet connection."
            except ImportError:
                msg = "The anthropic package isn't installed. Run: .venv/bin/pip install anthropic"
            traceback.print_exc()
            try:
                emit({"type": "error", "text": msg})
            except BrokenPipeError:
                pass

    def _json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=str(ROOT)))
    print(f"SeatCheck Michigan running at http://localhost:{PORT}")
    server.serve_forever()
