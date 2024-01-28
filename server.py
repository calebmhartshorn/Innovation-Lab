from http.server import BaseHTTPRequestHandler, HTTPServer
import json

data = {}
ip = "172.23.130.169"


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
        elif self.path.endswith("/read"):
            with open('data.json', 'r') as f:
                data = json.load(f)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.set_common_headers()
            self.wfile.write(json.dumps(data).encode())


    def do_POST(self):
        global data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode('utf-8')

        if self.path.endswith("/update"):
            json_data = json.loads(post_data)

            # Update data.json with the new data
            with open('data.json', 'w') as f:
                json.dump(json_data, f)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.set_common_headers()
            self.wfile.write(b'Data updated successfully')
        else:
            print(f"Received data: {post_data}")

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.set_common_headers()


    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.set_common_headers()


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
    main()
