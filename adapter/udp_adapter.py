import json
import socketserver
import threading

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        dict_in = self.read_udp()
        if not dict_in: return
        
        # SÉCURITÉ : On vérifie que le callback a bien été défini avant de l'appeler
        if self.server.logic_callback:
            dict_out = self.server.logic_callback(dict_in)
            
            if dict_out:
                self.write_udp(dict_out)
        else:
            print("[Avertissement] Message ignoré : Aucun logic_callback défini.")

    def read_udp(self) -> dict:
        """Récupère les octets, lit l'UTF-8, et transforme le JSON en dictionnaire."""
        try:
            raw_data = self.request[0].strip()
            decoded_text = raw_data.decode('utf-8')
            # json.loads() convertit la chaîne '{"cmd":"LED_ON"}' en dictionnaire Python
            return json.loads(decoded_text)
        except json.JSONDecodeError:
            print("[Erreur] Le message reçu n'est pas un JSON valide.")
            return None # On ignore le message malformé

    def write_udp(self, response_dict: dict):
        """Prend un dictionnaire Python, le convertit en JSON, puis en octets."""
        # json.dumps() convertit le dictionnaire Python en texte JSON
        json_text = json.dumps(response_dict)
        socket = self.request[1]
        socket.sendto(json_text.encode('utf-8'), self.client_address)

class CustomUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def __init__(self, server_address, RequestHandlerClass, logic_callback):
        super().__init__(server_address, RequestHandlerClass)
        self.logic_callback = logic_callback 

class UdpAdapter:
    def __init__(self, host, port, logic_callback = None):
        self.server = CustomUDPServer((host, port), ThreadedUDPRequestHandler, logic_callback)
        
    def set_logic_callback(self, logic_callback):
        """Assigne ou modifie la fonction de traitement métier après l'initialisation."""
        self.server.logic_callback = logic_callback
        
    def start(self):
        print(f"[Réseau] Démarrage de l'adaptateur UDP sur {self.server.server_address}...")
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        print("[Réseau] Arrêt de l'adaptateur UDP...")
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()