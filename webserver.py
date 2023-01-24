from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import asyncio
import websockets
hostName = ""
serverPort = 80

class MyServer(BaseHTTPRequestHandler):
    sockets = []
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
            print(self.sockets)

    def do_POST(self):
        if self.path == '/message':
            self.log_request()
            length = int(self.headers.get('Content-Length'))
            jsonString = self.rfile.read(length)
            message = json.loads(jsonString)
            with open("messages.txt", 'a') as messagefile:
                messagefile.write(f"{message['name']}: {message['message']}\n")
            self._broadcast("u")

    async def handle_websocket(self, websocket, path):
        self.sockets.append(websocket)
        try:
            while True:
                message = await websocket.recv()
                print(f"Received: {message} at {path}")
                response = process_message(message)
                await websocket.send(response)
        finally:
            self.sockets.remove(websocket)

    def _broadcast(self, message):
        for websocket in self.sockets:
            websocket.send(message)


webServer = HTTPServer((hostName, serverPort), MyServer)

def run_http_server():
    server_address = (hostName, serverPort)
    httpd = HTTPServer(server_address, MyServer)
    httpd.serve_forever()

async def run_websocket_server():
    global webServer
    start_server = websockets.serve(webServer.handle_websocket, hostName, serverPort)
    await start_server.serve_forever()

if __name__ == "__main__":        
    loop = asyncio.get_event_loop()
    http_server_task = loop.run_in_executor(None, run_http_server)
    websocket_server_task = asyncio.ensure_future(run_websocket_server())
    loop.run_until_complete(asyncio.gather(http_server_task, websocket_server_task))
