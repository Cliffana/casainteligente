"""Simple development server for the generated static site."""

import http.server
import socketserver
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUTPUT), **kwargs)

    def log_message(self, format, *args):
        print(f"  [{self.address_string()}] {args[0]} {args[1]} {args[2]}")

def serve():
    if not OUTPUT.exists() or not list(OUTPUT.iterdir()):
        print("[WARN] Output directory is empty. Run build.py first:")
        print("   python scripts/build.py")
        return

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n[SERVER] Servidor a correr em: {url}")
        print("   CTRL+C para parar\n")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Servidor parado.")

if __name__ == "__main__":
    serve()
