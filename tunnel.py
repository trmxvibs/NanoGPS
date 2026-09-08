import subprocess
import shutil
import re
import time
from colors import Colors

class TunnelManager:
    @staticmethod
    def start_tunnel(port):
        print(f"\n{Colors.YELLOW}[?] Select Tunneling / Access Provider:{Colors.RESET}")
        print(f" [1] Cloudflare (cloudflared)")
        print(f" [2] Serveo.net (SSH-based)")
        print(f" [3] Localhost.run (SSH-based)")
        print(f" [4] Localhost Direct Only")
        
        choice = input(f"\n{Colors.GREEN}tunnel > {Colors.RESET}").strip()
        
        # Localhost link is now compulsory for any choice
        print(f"\n{Colors.GREEN}{Colors.BOLD}[>>>] LOCALHOST URL: http://localhost:{port} [<<<]{Colors.RESET}")
        
        if choice == '2':
            return TunnelManager.start_serveo(port)
        elif choice == '3':
            return TunnelManager.start_localhost_run(port)
        elif choice == '4':
            print(f"{Colors.GREY}(Using Localhost direct access only){Colors.RESET}\n")
            return None
        else:
            return TunnelManager.start_cloudflare(port)

    @staticmethod
    def start_cloudflare(port):
        print(f"{Colors.CYAN}[*] Starting Cloudflare Tunnel...{Colors.RESET}")
        if shutil.which("cloudflared"):
            proc = subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            start_time = time.time()
            while time.time() - start_time < 15:
                line = proc.stderr.readline().decode('utf-8', errors='ignore')
                if not line and proc.poll() is not None:
                    break
                if "trycloudflare.com" in line:
                    match = re.search(r"(?P<url>https?://[^\s]+trycloudflare\.com)", line)
                    if match:
                        print(f"{Colors.GREEN}{Colors.BOLD}[>>>] CLOUDFLARE LINK: {match.group('url')} [<<<]{Colors.RESET}\n")
                        return proc
        else:
            print(f"{Colors.RED}[!] 'cloudflared' not found. Localhost is still active.{Colors.RESET}")
        return None

    @staticmethod
    def start_serveo(port):
        print(f"{Colors.CYAN}[*] Starting Serveo.net Tunnel (SSH)...{Colors.RESET}")
        try:
            proc = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{port}", "serveo.net"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            start_time = time.time()
            while time.time() - start_time < 8:
                line = proc.stdout.readline().decode('utf-8', errors='ignore') or proc.stderr.readline().decode('utf-8', errors='ignore')
                if "serveo.net" in line:
                    match = re.search(r"(?P<url>https?://[^\s]+)", line)
                    if match:
                        print(f"{Colors.GREEN}{Colors.BOLD}[>>>] SERVEO LINK: {match.group('url')} [<<<]{Colors.RESET}\n")
                        return proc
                time.sleep(0.5)
            print(f"{Colors.GREY}(Serveo background process started){Colors.RESET}\n")
            return proc
        except Exception as e:
            print(f"{Colors.RED}[!] Serveo failed: {e}{Colors.RESET}")
            return None

    @staticmethod
    def start_localhost_run(port):
        print(f"{Colors.CYAN}[*] Starting Localhost.run Tunnel (SSH)...{Colors.RESET}")
        try:
            proc = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{port}", "localhost.run"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            start_time = time.time()
            while time.time() - start_time < 8:
                line = proc.stdout.readline().decode('utf-8', errors='ignore') or proc.stderr.readline().decode('utf-8', errors='ignore')
                if "lhr.life" in line or "localhost.run" in line:
                    match = re.search(r"(?P<url>https?://[^\s]+)", line)
                    if match:
                        print(f"{Colors.GREEN}{Colors.BOLD}[>>>] LOCALHOST.RUN LINK: {match.group('url')} [<<<]{Colors.RESET}\n")
                        return proc
                time.sleep(0.5)
            print(f"{Colors.GREY}(Localhost.run background process started){Colors.RESET}\n")
            return proc
        except Exception as e:
            print(f"{Colors.RED}[!] Localhost.run failed: {e}{Colors.RESET}")
            return None