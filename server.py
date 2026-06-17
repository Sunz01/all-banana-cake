#!/usr/bin/env python3
"""Simple HTTP server with admin API for banana cake inventory + image gallery"""
import json
import os
import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DATA_FILE = "data.json"
IMAGES_DIR = "images"

def load_data():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {"inventory": [], "admin_password": "banana123", "gallery": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/inventory":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = load_data()
            public_data = {
                "inventory": data.get("inventory", []),
                "gallery": data.get("gallery", [])
            }
            self.wfile.write(json.dumps(public_data).encode())
            return
        super().do_GET()
    
    def do_POST(self):
        if self.path == "/api/update":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            stored = load_data()
            
            # Check password
            if data.get("password") != stored.get("admin_password"):
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"Invalid password"}')
                return
            
            # Update inventory
            if "inventory" in data:
                stored["inventory"] = data["inventory"]
            
            # Update gallery
            if "gallery" in data:
                # Handle new images (base64)
                for img in data["gallery"]:
                    if img.get("data") and img.get("name"):
                        # Decode and save image
                        img_data = base64.b64decode(img["data"])
                        filename = f"{img['name']}"
                        with open(f"{IMAGES_DIR}/{filename}", "wb") as f:
                            f.write(img_data)
                stored["gallery"] = data["gallery"]
            
            save_data(stored)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"success":true}')
            return
        super().do_GET()

port = int(os.environ.get("PORT", 8080))
os.makedirs(IMAGES_DIR, exist_ok=True)
server = HTTPServer(("0.0.0.0", port), Handler)
print(f"Server running on http://0.0.0.0:{port}")
server.serve_forever()