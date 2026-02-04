import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving frontend at http://localhost:{PORT}")
        print(f"Open your browser to http://localhost:{PORT}")
        httpd.serve_forever()
except OSError:
    print(f"Port {PORT} is busy. Try closing other python processes.")
