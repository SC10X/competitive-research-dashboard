import http.server
import os
import sys
import urllib.request
import urllib.error

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')
API_BACKEND = "http://127.0.0.1:8000"


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith('/api/'):
            self._proxy_to_backend()
            return

        path = self.path.split('?')[0]
        file_path = os.path.join(DIR, path.lstrip('/'))

        if os.path.exists(file_path) and os.path.isfile(file_path):
            return super().do_GET()
        else:
            self.path = '/index.html'
            return super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self._proxy_to_backend()
            return
        self.send_error(405, "Method Not Allowed")

    def do_PUT(self):
        if self.path.startswith('/api/'):
            self._proxy_to_backend()
            return
        self.send_error(405, "Method Not Allowed")

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self._proxy_to_backend()
            return
        self.send_error(405, "Method Not Allowed")

    def do_OPTIONS(self):
        if self.path.startswith('/api/'):
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()
            return
        self.send_error(405, "Method Not Allowed")

    def _proxy_to_backend(self):
        target_url = API_BACKEND + self.path
        try:
            # Read request body if present
            body = None
            content_length = self.headers.get('Content-Length')
            if content_length:
                body = self.rfile.read(int(content_length))

            req = urllib.request.Request(
                target_url,
                data=body,
                method=self.command,
                headers={
                    'Content-Type': self.headers.get('Content-Type', 'application/json'),
                    'Accept': self.headers.get('Accept', '*/*'),
                }
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.status)
                # Forward relevant headers
                for key, value in response.headers.items():
                    if key.lower() in ('content-type', 'content-length', 'cache-control'):
                        self.send_header(key, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"success": false, "error": "Proxy error: {str(e)}"}}'.encode())


if __name__ == '__main__':
    print(f"Serving static files from {DIR} on port {PORT}")
    print(f"Proxying /api/* requests to {API_BACKEND}")
    http.server.HTTPServer(('0.0.0.0', PORT), SPAHandler).serve_forever()
