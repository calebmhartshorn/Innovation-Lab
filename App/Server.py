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

# Loads items from a file called items.txt
if os.path.exists('inventory.json'):
    with open('inventory.json', 'r') as f:
        items = json.load(f)
    print("Loaded Ingredients")
else:
    print("Error: 'items.json' file not found.")
    items = {}




scanned_barcodes = {}

def run_barcode_scanner():
    decode_barcode_from_webcam()
import json

def add_quantity(barcode):
    with open('items.json', 'r') as f:
        items = json.load(f)

    barcode_int = int(barcode)
    item_found = False
    item_data = barcodes[barcode_int]
    scanned_date = datetime.now().strftime("%Y-%m-%d")

    for i, item in enumerate(items):
        if int(item['barcode']) == barcode_int:
            item_found = True
            if 'entries' not in item:
                item['entries'] = []

            entry_found = False
            for entry in item['entries']:
                if entry['created_date'] == scanned_date:
                    entry_found = True
                    entry['quantity_amount'] += item_data["quantity_amount"]
                    print(f"Found existing entry for barcode {barcode} on {scanned_date}")
                    print(f"Name: {item['name']}")
                    print(f"New Quantity: {entry['quantity_amount']} {entry['quantity_unit']}")
                    break

            if not entry_found:
                new_entry = {
                    "quantity_amount": item_data["quantity_amount"],
                    "quantity_unit": item_data["quantity_unit"],
                    "expiration_days": item_data["expiration_days"],
                    "created_date": scanned_date
                }
                item['entries'].append(new_entry)
                print(f"Added new entry for barcode {barcode} on {scanned_date}")
                print(f"Name: {item['name']}")
                print(f"New Quantity: {new_entry['quantity_amount']} {new_entry['quantity_unit']}")

            with open('items.json', 'w') as f:
                json.dump(items, f, indent=2)
            break

    if not item_found and barcode_int in barcodes:
        new_item = {
            "barcode": barcode,
            "name": item_data["name"],
            "generic_name": item_data["generic_name"],
            "entries": [
                {
                    "quantity_amount": item_data["quantity_amount"],
                    "quantity_unit": item_data["quantity_unit"],
                    "expiration_days": item_data["expiration_days"],
                    "created_date": scanned_date
                }
            ]
        }
        items.append(new_item)
        print(f"Added new item for barcode {barcode} on {scanned_date}")
        print(f"Name: {item_data['name']}")
        print(f"New Quantity: {item_data['quantity_amount']} {item_data['quantity_unit']}")

        with open('items.json', 'w') as f:
            json.dump(items, f, indent=2)

    if not item_found and barcode_int not in barcodes:
        print(f"Barcode: {barcode}")
        print("This item is not in the database.")

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

                # Checks if the barcode is in the barcodes dictionary
                if int(barcode) in barcodes:
                    item_data = barcodes[int(barcode)]
                    add_quantity(barcode)
                    # Uses the item_data as needed
                    print(f"Barcode {barcode} found: {item_data}")
                else:
                    print(f"Barcode {barcode} not found in the database.")

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
        global items
        print("Recieved")
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
                inventory_data = json.dumps(items).encode()
                print(inventory_data)
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
                updated_items = json.loads(post_data.decode('utf-8'))
                global items
                items = {item['barcode']: item for item in updated_items}
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
    #barcode_scanner_thread = threading.Thread(target=run_barcode_scanner)
    http_server_thread.start()

    while True:
        pass
    #barcode_scanner_thread.start()

    #barcode_scanner_thread.join()
    #httpd.shutdown()
    #http_server_thread.join()
