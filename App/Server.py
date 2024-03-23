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
if os.path.exists('items.json'):
    with open('items.json', 'r') as f:
        items_data = f.read()
        items = {item['barcode']: item for item in json.loads(items_data)}
    print("Loaded Ingredients")
else:
    print("Error: 'items.json' file not found.")
    items = {}

if os.path.exists('barcodes.json'):
    with open('barcodes.json', 'r') as f:
        barcodes_data = f.read()
    barcodes = {}
    for item in json.loads(barcodes_data):
        for barcode, data in item.items():
            barcodes[int(barcode)] = data
    print("Loaded Barcodes")
else:
    print("Error: 'barcodes.json' file not found.")
    barcodes = {}


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

    for item in items:
        if int(item['barcode']) == barcode_int:
            print("Found item in items.json")
            print(f"Barcode: {barcode}")
            print(f"Name: {item['name']}")
            item['quantity_amount'] += item_data["quantity_amount"]
            print(f"New Quantity: {item['quantity_amount']} {item['quantity_unit']}")
            item_found = True

            with open('items.json', 'w') as f:
                json.dump(items, f, indent=2)
            break

    if not item_found and barcode_int in barcodes:
        new_item = {
            "barcode": barcode,
            "name": item_data["name"],
            "generic_name": item_data["generic_name"],
            "quantity_amount": 1,
            "quantity_unit": item_data["quantity_unit"],
            "expiration_days": item_data["expiration_days"]
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        items.append(new_item)
        print("Added new item to items.json found in barcodes.json")
        print(f"Barcode: {barcode}")
        print(f"Name: {item_data['name']}")
        print(f"New Quantity: {new_item['quantity_amount']} {new_item['quantity_unit']}")
        print(f"Scanned Date: {new_item['created_date']}")

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
                inventory_data = [{'name': item['name'], 'ingredients': [item['generic_name']], 'quantity_amount': item['quantity_amount'], 'quantity_unit': item['quantity_unit'], 'expiration_days': item['expiration_days'], 'barcode': item['barcode']} for item in items.values()]
                print(f"Sending inventory data: {inventory_data}")
                self.wfile.write(json.dumps(inventory_data).encode())
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
    barcode_scanner_thread = threading.Thread(target=run_barcode_scanner)

    http_server_thread.start()
    barcode_scanner_thread.start()

    barcode_scanner_thread.join()
    httpd.shutdown()
    http_server_thread.join()
