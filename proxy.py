#!/usr/bin/env python3
"""CORS proxy for WorkOS — sits between the browser and the Netflix Model Gateway."""

import http.server
import urllib.request
import json
import ssl

# Use certifi CA bundle if available, otherwise fall back to unverified for local dev
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE

UPSTREAM = "http://localhost:9123"
SLACK_API = "https://slack.com/api"
PORT = 8090

class CORSProxy(http.server.BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, x-netflix-copilot-project-id")
        self.send_header("Access-Control-Max-Age", "86400")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def _proxy_request(self, url, method="GET", body=None, headers=None):
        """Shared proxy logic for both GET and POST."""
        req = urllib.request.Request(url, data=body if body else None, method=method)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, context=SSL_CTX) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_response(502)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _resolve_url_and_headers(self, method="GET", body=None):
        """Route /slack/* to Slack API, everything else to AI gateway."""
        fwd = {}
        if self.path.startswith("/slack/"):
            url = SLACK_API + self.path[6:]  # strip "/slack"
            auth = self.headers.get("Authorization")
            if auth:
                fwd["Authorization"] = auth
        else:
            url = UPSTREAM + self.path
            fwd["Content-Type"] = "application/json"
            for h in ("x-netflix-copilot-project-id", "Authorization"):
                val = self.headers.get(h)
                if val:
                    fwd[h] = val
        return url, fwd

    def do_GET(self):
        url, fwd = self._resolve_url_and_headers("GET")
        self._proxy_request(url, method="GET", headers=fwd)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        url, fwd = self._resolve_url_and_headers("POST", body)
        if "Content-Type" not in fwd:
            fwd["Content-Type"] = "application/json"
        self._proxy_request(url, method="POST", body=body, headers=fwd)

    def log_message(self, fmt, *args):
        print(f"[proxy] {fmt % args}")

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), CORSProxy)
    print(f"CORS proxy running on http://localhost:{PORT}")
    print(f"Forwarding to {UPSTREAM}")
    print(f"Set WorkOS gateway base URL to: http://localhost:{PORT}/mtlsproxy:mgp/proxy/workos")
    server.serve_forever()
