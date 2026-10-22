#!/usr/bin/env python3
"""Static server for Klineto: clean paths, security headers, custom 404."""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent / "site"
HOST = "0.0.0.0"
# Amvera sets PORT to containerPort (default 80). Local run stays on 43127.
PORT = int(os.environ.get("PORT", "43127"))

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
}


def resolve_path(url_path: str) -> Path | None:
    raw = unquote(urlparse(url_path).path)
    if "\x00" in raw:
        return None
    if raw.startswith("/"):
        raw = raw[1:]
    if raw.endswith("/"):
        raw = raw[:-1]
    candidate = (ROOT / raw).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return None
    if candidate.is_dir():
        index = candidate / "index.html"
        if index.is_file():
            return index
        return None
    if candidate.is_file():
        return candidate
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "KlinetoStatic/1.0"

    def do_GET(self):
        self._serve(write_body=True)

    def do_HEAD(self):
        self._serve(write_body=False)

    def do_POST(self):
        self._method_not_allowed()

    def _security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")

    def _serve(self, write_body: bool):
        target = resolve_path(self.path)
        if target is None:
            self._send_404(write_body)
            return
        data = target.read_bytes()
        content_type = CONTENT_TYPES.get(target.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        if write_body:
            self.wfile.write(data)

    def _send_404(self, write_body: bool):
        page = ROOT / "404.html"
        data = page.read_bytes() if page.is_file() else "Страница не найдена".encode("utf-8")
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        if write_body:
            self.wfile.write(data)

    def _method_not_allowed(self):
        body = "Метод не поддерживается".encode("utf-8")
        self.send_response(405)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Allow", "GET, HEAD")
        self._security_headers()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Klineto: http://127.0.0.1:{PORT}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановлено")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
