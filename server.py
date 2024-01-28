from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import requests
import threading
import json
import random
import string
import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

with open('ingredients.txt', 'r') as file:
    all_ingredients = [line.strip().lower() for line in file.readlines()]

data = {}
scan_results = {}
ip = " 172.23.129.173"
#ip = "172.23.129.18"

scanning = False

class WebServerHandler(BaseHTTPRequestHandler):
    
    def set_common_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
    
    def do_GET(self):
        global data
        if self.path == "/":
            try:
                with open('index.html', 'r') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.set_common_headers()
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.set_common_headers()
                self.wfile.write(b'Index file not found')

        elif self.path.endswith("/styles.css"):
            try:
                with open('styles.css', 'r') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/css')
                    self.set_common_headers()
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.set_common_headers()
                self.wfile.write(b'CSS file not found')

        elif self.path.endswith("/client.js"):
            try:
                with open('client.js', 'r') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/javascript')
                    self.set_common_headers()
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.set_common_headers()
                self.wfile.write(b'JS file not found')

        elif self.path.endswith("/table.js"):
            try:
                with open('table.js', 'r') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/javascript')
                    self.set_common_headers()
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.set_common_headers()
                self.wfile.write(b'JS file not found')
        elif self.path.endswith("/read"):
            with open('data.json', 'r') as f:
                data = json.load(f)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.set_common_headers()
            self.wfile.write(json.dumps(data).encode())
        elif self.path.startswith("/recipe"):
            # Parse the URL
            parsed_url = urlparse(self.path)
            
            # Extract the query parameters
            params = parse_qs(parsed_url.query)
            
            # Now you can access the parameters as a dictionary
            ingredients =          params.get('ingredients',          ['[]'])[0].replace("[", "").replace("]", "").split(",")
            mandatoryIngredients = [params.get('must', [])[0]]

            url = 'https://realfood.tesco.com/api/ingredientsearch/getrecipes'
            
            data = {
                # These are a harcoded example. Anything is fine, but make to use at least 3 ingredients and only use terms defined
                # in ingredients.txt
                'ingredients': ingredients,
                'mandatoryIngredients': mandatoryIngredients,
                'dietaryRequirements': []
            }
            response = requests.post(url, json=data)

            json_data = response.json()
            #print(json.dumps(json_data, indent=2))

            # Just names
            response = ""
            for recipe in json_data['results']:
                name = recipe['recipeName']
                response += f"<p>{name}</p>"
                #print(f"{name}")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_common_headers()
            self.wfile.write(json.dumps(json_data).encode())

        elif self.path.endswith("/scanresults"):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_common_headers()
      
            self.wfile.write(json.dumps(scan_results).encode())

    def do_POST(self):
        global data,scanning

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode('utf-8')

        if self.path.endswith("/update"):
            json_data = json.loads(post_data)
            with open('data.json', 'w') as f:
                json.dump(json_data, f)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.set_common_headers()
            self.wfile.write(b'Data updated successfully')

        elif self.path.endswith("/enablescan"):
            scanning = True
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.set_common_headers()
            print("Starting Scanning")

        elif self.path.endswith("/disablescan"):
            scanning = False
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.set_common_headers()
            print("Stopping Scanning")

        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.set_common_headers()


    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.set_common_headers()
def ocr_thread():
    global scanning, scan_results

    print("OCR thread started.")

    cap = cv2.VideoCapture(1)
    tog = 1
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        if scanning:
            if tog == 0:
                cap = cv2.VideoCapture(0)# Restart the camera
                tog = 1
            ret, frame = cap.read()
            if ret:
                print("Scanning...")
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                #ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                text = pytesseract.image_to_string(gray, lang='eng', config='--psm 11')
                print(text)
                captured_ingredients = [i.strip().lower() for i in re.split(',|\n', text) if i.strip().lower() in all_ingredients]
                if captured_ingredients:
                    scan_results = {"name":captured_ingredients[0]}
                    print(f"Captured ingredient: {scan_results}")
                else:
                    scan_results = {}
                
                cv2.imshow('Camera Frame', gray)
                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        else:
            if tog == 1:# Turn off camera once
                cap.release()
                tog = 0
    print("OCR thread exiting.")

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print ("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    
    # Start the OCR thread
    ocr_thread = threading.Thread(target=ocr_thread)
    ocr_thread.start()

    # Main server thread
    main()
