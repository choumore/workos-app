#!/usr/bin/env python3
"""CORS proxy for WorkOS — sits between the browser and the Netflix Model Gateway."""

import http.server
import urllib.request
import json
import ssl
import subprocess
import time
import re

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
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"
GCAL_KEYCHAIN_SERVICE = "google-workspace-mcp-oauth"
GCAL_KEYCHAIN_ACCOUNT = "main-account"
GCAL_REFRESH_URL = "https://google-workspace-extension.geminicli.com/refreshToken"
PORT = 8090

# In-memory token cache — never written to Keychain (MCP wrapper owns that)
_gcal_token_cache = {"access_token": None, "expires_at": 0, "refresh_token": None}

def read_gcal_token():
    """Read Google Calendar token from macOS Keychain (stored by MCP wrapper)."""
    global _gcal_token_cache
    # Return cached token if still valid (with 5-min buffer)
    if _gcal_token_cache["access_token"] and _gcal_token_cache["expires_at"] > time.time() + 300:
        return _gcal_token_cache["access_token"]
    # Read from Keychain
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", GCAL_KEYCHAIN_SERVICE, "-a", GCAL_KEYCHAIN_ACCOUNT, "-w"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0 or not result.stdout.strip():
            print(f"[proxy] Keychain read: no entry found")
            return None
        creds = json.loads(result.stdout.strip())
        token = creds.get("token", {})
        _gcal_token_cache["access_token"] = token.get("accessToken")
        _gcal_token_cache["refresh_token"] = token.get("refreshToken")
        _gcal_token_cache["expires_at"] = (token.get("expiresAt") or 0) / 1000  # ms → sec
    except subprocess.TimeoutExpired:
        print("[proxy] Keychain read timed out")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[proxy] Keychain parse failed: {e}")
        return None
    if not _gcal_token_cache["access_token"]:
        return None
    # Refresh if expired or expiring soon
    if _gcal_token_cache["expires_at"] < time.time() + 300 and _gcal_token_cache["refresh_token"]:
        try:
            refresh_gcal_token()
        except Exception as e:
            print(f"[proxy] Token refresh failed: {e}")
    return _gcal_token_cache["access_token"]

def refresh_gcal_token():
    """Refresh token via MCP wrapper's cloud function."""
    global _gcal_token_cache
    if not _gcal_token_cache["refresh_token"]:
        return
    body = json.dumps({"refresh_token": _gcal_token_cache["refresh_token"]}).encode()
    req = urllib.request.Request(GCAL_REFRESH_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as resp:
        data = json.loads(resp.read())
    new_token = data.get("access_token")
    if new_token:
        _gcal_token_cache["access_token"] = new_token
        _gcal_token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)
        print("[proxy] Token refreshed successfully")

class CORSProxy(http.server.BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, x-netflix-copilot-project-id")
        self.send_header("Access-Control-Max-Age", "86400")

    def _gcal_cors_headers(self):
        """Restricted CORS for calendar routes — only allow real localhost origins."""
        origin = self.headers.get("Origin", "")
        if re.match(r'^http://localhost(:\d+)?$', origin):
            self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        if self.path.startswith("/gcal/"):
            self._gcal_cors_headers()
        else:
            self._cors_headers()
        self.end_headers()

    def _proxy_request(self, url, method="GET", body=None, headers=None, use_gcal_cors=False):
        """Shared proxy logic for both GET and POST."""
        req = urllib.request.Request(url, data=body if body else None, method=method)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as resp:
                data = resp.read()
                self.send_response(resp.status)
                if use_gcal_cors:
                    self._gcal_cors_headers()
                else:
                    self._cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            # Invalidate token cache on 401 from Google Calendar API
            if use_gcal_cors and e.code == 401:
                _gcal_token_cache["access_token"] = None
                _gcal_token_cache["expires_at"] = 0
                print("[proxy] Google Calendar returned 401 — token cache cleared")
            self.send_response(e.code)
            if use_gcal_cors:
                self._gcal_cors_headers()
            else:
                self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_response(502)
            if use_gcal_cors:
                self._gcal_cors_headers()
            else:
                self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _resolve_url_and_headers(self, method="GET", body=None):
        """Route /slack/* to Slack API, /gcal/* to Google Calendar API, else AI gateway."""
        fwd = {}
        use_gcal_cors = False
        if self.path.startswith("/gcal/"):
            url = GOOGLE_CALENDAR_API + self.path[5:]  # strip "/gcal"
            token = read_gcal_token()
            if token:
                fwd["Authorization"] = f"Bearer {token}"
            use_gcal_cors = True
        elif self.path.startswith("/slack/"):
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
        return url, fwd, use_gcal_cors

    def do_GET(self):
        # Dedicated /gcal/status endpoint
        if self.path == "/gcal/status":
            token = read_gcal_token()
            self.send_response(200)
            self._gcal_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"connected": token is not None}).encode())
            return
        url, fwd, use_gcal_cors = self._resolve_url_and_headers("GET")
        self._proxy_request(url, method="GET", headers=fwd, use_gcal_cors=use_gcal_cors)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        url, fwd, use_gcal_cors = self._resolve_url_and_headers("POST", body)
        if "Content-Type" not in fwd:
            fwd["Content-Type"] = "application/json"
        self._proxy_request(url, method="POST", body=body, headers=fwd, use_gcal_cors=use_gcal_cors)

    def log_message(self, fmt, *args):
        print(f"[proxy] {fmt % args}")

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), CORSProxy)
    print(f"CORS proxy running on http://localhost:{PORT}")
    print(f"Forwarding to {UPSTREAM}")
    print(f"Google Calendar proxy: /gcal/* → {GOOGLE_CALENDAR_API}")
    print(f"Set WorkOS gateway base URL to: http://localhost:{PORT}/mtlsproxy:mgp/proxy/workos")
    server.serve_forever()
