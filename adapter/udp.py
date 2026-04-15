import socketserver
import threading

class UDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        raw_data = self.request[0].strip()
        udp_socket = self.request[1]
        try:
            model = self.server.protocol.decode(raw_data)
            self.server.on_message(model, self.client_address)
            udp_socket.sendto(b"OK\n", self.client_address)
        except Exception as exc:
            print(f"UDP parse error from {self.client_address}: {exc}")
            udp_socket.sendto(b"ERROR\n", self.client_address)


class UDPAdapter:
    def __init__(self, host: str, port: int, protocol, on_message):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.on_message = on_message
        self.server = socketserver.ThreadingUDPServer((host, port), UDPRequestHandler)
        self.server.protocol = protocol
        self.server.on_message = on_message
        self.server.daemon_threads = True
        self.server.allow_reuse_address = True
        self._thread = None

    def start_server(self):
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()
        print(f"UDP server started on {self.host}:{self.port} with text protocol")

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        print("UDP server stopped")
