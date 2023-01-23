from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
#THIS IS LUKE
#Nathan
#comment
#2
hostName = ""
serverPort = 80

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open ("index.html", "r") as indexfile:
                self.wfile.write(bytes(indexfile.read(), "utf-8"))
        
        if self.path == '/content':
            self.send_response(200)
            self.send_header("content-type", "text")
            self.end_headers()
            with open ("messages.txt", "r") as messagefile:
                self.wfile.write(bytes(messagefile.read(), "utf-8"))

    def do_POST(self):
        if self.path == '/message':
            self.log_request()
            length = int(self.headers.get('Content-Length'))
            jsonString = self.rfile.read(length)
            message = json.loads(jsonString)
            with open("messages.txt", 'a') as messagefile:
                messagefile.write(f"{message['name']}: {message['message']}\n")

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
