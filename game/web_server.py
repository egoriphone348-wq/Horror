#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-сервер для «Подвал Безумия 3D».
Отдаёт game3d.html как основную страницу.
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 5000))
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(GAME_DIR, "game3d.html")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # тишина в логах

    def do_GET(self):
        if self.path in ('/', '/?', ''):
            try:
                with open(HTML_FILE, 'rb') as f:
                    body = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(body)
            except FileNotFoundError:
                self.send_error(404, "game3d.html not found")
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()


if __name__ == '__main__':
    print(f"Подвал Безумия 3D · http://0.0.0.0:{PORT}", flush=True)
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
