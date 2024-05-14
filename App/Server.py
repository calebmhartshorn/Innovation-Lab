# import OS and set environment variables
import os
os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-user/' # Set root working dir
os.environ['LIBCAMERA_LOG_LEVELS'] = '4'             # Hide libcamera logs
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'       # Hide pygame messages

# Default Libs
import time, datetime, threading, http.server, socketserver, json, logging

# Non-default Libs
import cv2                                   # OpenCV - For vision processing 
from pyzbar.pyzbar import decode, ZBarSymbol # Pyzbar - For barcode reading
from picamera2 import Picamera2              # Picamera2 - RPi Camera drivers
import pygame                                # pygame - For sound effects

# Local files
from gui_app import App, State

# Setup logging
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(level=logging.DEBUG)
formatter =  logging.Formatter('%(levelname)s : %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# Globals
HTTP_SERVER_PORT = 8000

inventory = {}
app = None


def add_quantity(barcode):
    barcode = str(barcode)
    scanned_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if barcode in inventory:
        inventory_entry = inventory[barcode]
        inventory_entry['scans'].append(scanned_date)
    else:
        inventory[barcode] = {
            "name": "Unknown",
            "generic_name": "Unknown",
            "size": 1,
            "size_units": "Unit",
            "shelf_life": 7,
            "scans": [scanned_date]
        }

    with open('inventory.json', 'w') as f:
        json.dump(inventory, f, indent=2)

def remove_quantity(barcode):
    barcode = str(barcode)    
    if barcode in inventory:
        inventory_entry = inventory[barcode]
        if len(inventory_entry['scans']) > 0:
            inventory_entry['scans'].pop(0)
            with open('inventory.json', 'w') as f:
                json.dump(inventory, f, indent=2)
    
def decode_barcode_from_webcam():
    global app

    cv2.namedWindow('image',cv2.WINDOW_GUI_NORMAL)
    
    Picamera2.set_logging(Picamera2.ERROR)
    picam2 = Picamera2()
    
    config = picam2.create_still_configuration(
        main = {"size": picam2.sensor_resolution}
    )
    picam2.configure(config)
    picam2.set_controls({"ExposureTime": 20000, "AnalogueGain": 50.0})
    picam2.start()
    
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2)
    pygame.mixer.init()
    sound = pygame.mixer.Sound('blip-131856.mp3')
    
    while True:
        frame = picam2.capture_array()

        scale = 0.2
        width = int(frame.shape[1] * scale)
        height = int(frame.shape[0] * scale)
        frame = cv2.resize(frame, (width, height))
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        decoded_objects = decode(frame, symbols=[ZBarSymbol.EAN13])

        for obj in decoded_objects:
            barcode = obj.data.decode('utf-8')

            try:
                barcode_int = int(barcode)
            except ValueError:
                print(f"Invalid barcode: {barcode}")
                continue

            playing = sound.play()
            time.sleep(.5)

            try:
                print(app.state)
                if app.state == State.MAIN:
                    add_quantity(barcode_int)
                elif app.state == State.SCAN_OUT:
                    remove_quantity(barcode_int)
            except Exception as e:
                print(f"Error adding barcode to inventory: {e}")

            cv2.rectangle(frame, (obj.rect.left, obj.rect.top),
                          (obj.rect.left + obj.rect.width, obj.rect.top + obj.rect.height),
                          (0, 255, 0), 2)
            cv2.putText(frame, str(barcode_int), (obj.rect.left, obj.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imshow('image', frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

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
                with open('website/index.html', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/client.js':
                self.send_response(200)
                self.send_header('Content-type', 'text/javascript')
                self.end_headers()
                with open('website/client.js', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/styles.css':
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                with open('website/styles.css', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/Assets/leaf.jpg':
                self.send_response(200)
                self.send_header('Content-type', 'text/javascript')
                self.end_headers()
                with open('website/assets/leaf.jpg', 'rb') as f:
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

def main():
    global inventory, app
    
    # Read in inventory
    if os.path.exists('inventory.json'):
        with open('inventory.json', 'r', encoding='UTF-8') as f:
            inventory = json.load(f)
    else:
        print("File 'inventory.json' not found. Creating a new one.")
        inventory = {}
    
    with socketserver.TCPServer(("", HTTP_SERVER_PORT), MyHTTPRequestHandler) as httpd:
        # Instantiate GUI app
        app = App(logger, inventory)
        
        # Create thread objects
        app_thread = threading.Thread(target=app.start)
        http_server_thread = threading.Thread(target=httpd.serve_forever)
        
        # Start threads
        app_thread.start()
        http_server_thread.start()

        decode_barcode_from_webcam()

        # Terminate & join remaining threads
        app.shutdown()
        httpd.shutdown()
        app_thread.join()
        http_server_thread.join()

if __name__ == "__main__":
    main()
