import http.server
import socketserver
from http.server import BaseHTTPRequestHandler
import json
import cv2
from pyzbar.pyzbar import decode
import time
import os
import threading

PORT = 8000

# Loads items from a file called items.txt
if os.path.exists('items.json'):
    with open('items.json', 'r') as f:
        items_data = f.read()
        items = {item['barcode']: item for item in json.loads(items_data)}
    print("Loaded Ingredients")
else:
    print("Error: 'items.txt' file not found.")
    items = {}

scanned_barcodes = {}

def run_barcode_scanner():
    decode_barcode_from_webcam()

def add_quantity(barcode):
    if barcode in items:
        item = items[barcode]
        print(f"Barcode: {barcode}")
        print(f"Name: {item['name']}")
        item['quantity_amount'] += 1
        print(f"New Quantity: {item['quantity_amount']} {item['quantity_unit']}")
    else:
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
                cv2.rectangle(frame, (obj.rect.left, obj.rect.top),
                              (obj.rect.left + obj.rect.width, obj.rect.top + obj.rect.height),
                              (0, 255, 0), 2)
                cv2.putText(frame, barcode, (obj.rect.left, obj.rect.top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                add_quantity(barcode)

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

    http_server_thread.join()
    httpd.shutdown()
    barcode_scanner_thread.join()
