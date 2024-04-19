import http.server
import socketserver
from http.server import BaseHTTPRequestHandler
import json
import cv2
from pyzbar.pyzbar import decode
import time
import os
import threading
from datetime import datetime

PORT = 8000

if os.path.exists('inventory.json'):
    with open('inventory.json', 'r') as f:
        inventory = json.load(f)
    print("Loaded Inventory")
else:
    print("'inventory.json' file not found. Creating a new one.")
    inventory = {}

scanned_barcodes = {}

def add_quantity(barcode):
    barcode_int = int(barcode)
    scanned_date = datetime.now().strftime("%Y-%m-%d")

    if barcode_int in inventory:
        inventory[barcode_int]['scans'].append(scanned_date)
    else:
        inventory[barcode_int] = {
            "name": "Unknown",
            "generic_name": "Unknown",
            "size": 1,
            "size_units": "Unit",
            "shelf_life": 7,
            "scans": [scanned_date]
        }

    with open('inventory.json', 'w') as f:
        json.dump(inventory, f, indent=2)

    print(f"Barcode {barcode} added/updated in inventory.")

def decode_barcode_from_webcam():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture image")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(gray_frame)

        for obj in decoded_objects:
            barcode = obj.data.decode('utf-8')

            if barcode in scanned_barcodes:
                scanned_barcodes[barcode] += 1
            else:
                scanned_barcodes[barcode] = 1

            if scanned_barcodes[barcode] == 15:
                time.sleep(1)
                scanned_barcodes[barcode] = 1

                add_quantity(barcode)

            cv2.rectangle(frame, (obj.rect.left, obj.rect.top),
                          (obj.rect.left + obj.rect.width, obj.rect.top + obj.rect.height),
                          (0, 255, 0), 2)
            cv2.putText(frame, barcode, (obj.rect.left, obj.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imshow('Barcode Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global inventory
        print("Received GET request")
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/client.js':
                self.send_response(200)
                self.send_header('Content-type', 'text/javascript')
                self.end_headers()
                with open('client.js', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/styles.css':
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                with open('styles.css', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/inventory':
                print("Received request for inventory data")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                inventory_data = json.dumps(inventory).encode()
                print(f"Sending inventory data: {inventory_data}")
                self.wfile.write(inventory_data)
            else:
                super().do_GET()
        except Exception as e:
            print(f"Error in do_GET: {e}")
            self.send_error(500, str(e))

    def do_POST(self):
        try:
            if self.path == '/update-inventory':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                updated_inventory = json.loads(post_data.decode('utf-8'))
                global inventory
                inventory = updated_inventory
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Inventory updated successfully')
            else:
                super().do_POST()
        except Exception as e:
            print(f"Error in do_POST: {e}")
            self.send_error(500, str(e))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Serving at port {PORT}")
    http_server_thread = threading.Thread(target=httpd.serve_forever)
    barcode_scanner_thread = threading.Thread(target=decode_barcode_from_webcam)
    http_server_thread.start()
    barcode_scanner_thread.start()

    barcode_scanner_thread.join()
    httpd.shutdown()
    http_server_thread.join()
