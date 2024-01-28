from http.server import BaseHTTPRequestHandler, HTTPServer
import json

lastValue = []

class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global lastValue
        if self.path.endswith("/clear"):
            lastValue = []
        if self.path.endswith("/hello") or self.path.endswith("/clear"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

            #self.send_header('Access-Control-Allow-Credentials', 'true')
            self.end_headers()
            message = str(lastValue)
            self.wfile.write(bytes(message, "utf-8"))
            return
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)
    
    def do_POST(self):
       global lastValue

       content_length = int(self.headers['Content-Length'])
       post_data = self.rfile.read(content_length)
       post_data = post_data.decode('utf-8')
       json_data = json.loads(post_data)
       lastValue.append(json_data["message"])
       print(f"Received data: {post_data}")
       self.send_response(200)
       self.send_header('Content-type', 'text/html')
       self.send_header('Access-Control-Allow-Origin', '*')
       self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
       self.end_headers()
       self.wfile.write(bytes(str(lastValue), "utf-8"))
    
    def do_OPTIONS(self):
       self.send_response(200, "ok")
       self.send_header('Access-Control-Allow-Origin', '*')
       self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
       self.send_header('Access-Control-Allow-Headers', 'Content-Type')
       self.end_headers()

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