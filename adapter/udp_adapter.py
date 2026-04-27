import socketserver
import threading

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        raw_data = self.request[0]
        socket = self.request[1]
        
        # 1. DÉCODAGE (Délégué à l'encodeur)
        dict_in = self.server.encodage.decode(raw_data)
        if not dict_in: 
            return
        
        # 2. LOGIQUE MÉTIER (Déléguée au UdpController)
        if self.server.logic_callback:
            dict_out = self.server.logic_callback(dict_in)
            
            # 3. ENCODAGE ET ENVOI
            if dict_out:
                response_bytes = self.server.encodage.encode(dict_out)
                socket.sendto(response_bytes, self.client_address)
        else:
            print("[Avertissement] Message ignoré : Aucun logic_callback défini.")

class CustomUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    # On ajoute "encodage" au constructeur
    def __init__(self, server_address, RequestHandlerClass, logic_callback, encodage):
        super().__init__(server_address, RequestHandlerClass)
        self.logic_callback = logic_callback 
        self.encodage = encodage

class UdpAdapter:
    # On demande l'encodage à l'initialisation
    def __init__(self, host, port, encodage, logic_callback=None):
        self.server = CustomUDPServer((host, port), ThreadedUDPRequestHandler, logic_callback, encodage)
        
    def set_logic_callback(self, logic_callback):
        self.server.logic_callback = logic_callback
        
    def start(self):
        print(f"[Réseau] Démarrage de l'adaptateur UDP sur {self.server.server_address}...")
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        print("[Réseau] Arrêt de l'adaptateur UDP...")
        self.server.shutdown()
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.server.server_close()