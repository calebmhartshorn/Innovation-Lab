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

# Loads items from a file called inventory.json
if os.path.exists('inventory.json'):
    with open('inventory.json', 'r') as f:
        inventory = json.load(f)
    print("Loaded Inventory")
else:
    print("Error: 'inventory.json' file not found.")
    inventory = {}

scanned_barcodes = {}

def run_barcode_scanner():
    #Will be redundant
    decode_barcode_from_webcam()

def add_quantity(barcode):
    barcode_int = int(barcode)
    scanned_date = datetime.now().strftime("%Y-%m-%d")

    if barcode_int in inventory:
        item = inventory[barcode_int]
        if 'scans' not in item:
            item['scans'] = []

        if scanned_date not in item['scans']:
            item['scans'].append(scanned_date)
            print(f"Added new scan for barcode {barcode} on {scanned_date}")
            print(f"Name: {item['name']}")
            print(f"Size: {item['size']} {item['size_units']}")
        else:
            print(f"Scan already exists for barcode {barcode} on {scanned_date}")

        with open('inventory.json', 'w') as f:
            json.dump(inventory, f, indent=2)
    else:
        print(f"Barcode {barcode} not found in the inventory.")

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

            # 15 times seems good for how quick it scans
            if barcode in scanned_barcodes:
                scanned_barcodes[barcode] += 1
            else:
                scanned_barcodes[barcode] = 1

            if scanned_barcodes[barcode] == 15:
                time.sleep(1)  # Wait for 1 second
                scanned_barcodes[barcode] = 1

                # Checks if the barcode is in the inventory dictionary
                if int(barcode) in inventory:
                    add_quantity(barcode)
                else:
                    print(f"Barcode {barcode} not found in the inventory.")

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
        print("Received")
        try:
            if self.path == '/inventory':
                print("Received request for inventory data")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                inventory_data = json.dumps(list(inventory.values())).encode()
                print(inventory_data)
                print(f"Sending inventory data: {inventory_data}")
                self.wfile.write(inventory_data)
            elif self.path == '/':
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
                inventory = {int(barcode): item for barcode, item in updated_inventory.items()}
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Inventory updated successfully')
            else:
                self.send_error(404, 'Endpoint not found')
        except Exception as e:
            print(f"Error in do_POST: {e}")
            self.send_error(500, str(e))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Serving at port {PORT}")
    http_server_thread = threading.Thread(target=httpd.serve_forever)
    barcode_scanner_thread = threading.Thread(target=run_barcode_scanner)
    http_server_thread.start()
    barcode_scanner_thread.start()

    http_server_thread.join()
    barcode_scanner_thread.join()
