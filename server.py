#!/usr/bin/env python3
"""Static server for Klineto: clean paths, security headers, custom 404."""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent / "site"
HOST = "0.0.0.0"


def choose_port(raw: str | None) -> int:
    text = (raw or "").strip()
    if text.isdigit() and int(text) >= 1024:
        return int(text)
    # Amvera defaults PORT to 80, and the container cannot bind it.
    if text:
        return 8080
    return 43127


PORT = choose_port(os.environ.get("PORT"))

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
    try:
        httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as exc:
        print(f"Klineto failed to bind {HOST}:{PORT}: {exc}", flush=True)
        raise
    print(f"Klineto: http://{HOST}:{PORT}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановлено")
    finally:
        httpd.server_close()


def demo():
    assert choose_port(None) == 43127
    assert choose_port("") == 43127
    assert choose_port("80") == 8080
    assert choose_port("8080") == 8080
    assert choose_port("43127") == 43127


if __name__ == "__main__":
    main()
