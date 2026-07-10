#!/usr/bin/env python3
"""Static file server + API reverse proxy for the competitive research dashboard.

- Serves the built frontend from ./dist
- Proxies any path starting with /api/ to the backend at http://127.0.0.1:8000
- SPA fallback: unknown non-API paths serve index.html
"""
import http.server
import os
import socketserver
import urllib.request
import urllib.error
from urllib.parse import urlparse

BACKEND = "http://127.0.0.1:8000"
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

PROXY_METHODS = ("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def _proxy(self):
        target = BACKEND + self.path
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else None
        headers = {
            "Content-Type": self.headers.get("Content-Type", ""),
            "Accept": self.headers.get("Accept", "*/*"),
        }
        req = urllib.request.Request(target, data=body, method=self.command, headers=headers)
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            payload = resp.read()
            self.send_response(resp.status)
            for key, val in resp.headers.items():
                kl = key.lower()
                if kl in ("transfer-encoding", "connection", "content-length"):
                    continue
                self.send_header(key, val)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if payload:
                self.wfile.write(payload)
        except urllib.error.HTTPError as e:
            payload = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if payload:
                self.wfile.write(payload)
        except Exception as e:  # noqa: BLE001
            msg = str(e).encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        # SPA fallback for client-side routes
        path = self.translate_path(self.path)
        if not os.path.exists(path) or os.path.isdir(path):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        return self.send_error(404)

    def do_PUT(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        return self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        return self.send_error(404)

    def do_PATCH(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        return self.send_error(404)

    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        return self.send_error(404)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    os.chdir(DIST_DIR)
    with ThreadingHTTPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"Serving {DIST_DIR} + proxy /api -> {BACKEND} on 0.0.0.0:{port}")
        httpd.serve_forever()
