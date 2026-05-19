# Module pour créer des serveurs UDP et gérer les requêtes réseau
import socketserver
# Module pour exécuter les tâches en parallèle (threads)
import threading

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    """
    Gestionnaire de requêtes UDP.
    Traite chaque message UDP reçu en 3 étapes : décodage, logique métier, encodage et réponse.
    """
    
    def handle(self):
        """Traite une requête UDP reçue du client (Android)."""
        # Récupère les données brutes et le socket utilisé pour la réponse
        raw_data = self.request[0]
        socket = self.request[1]
        
        # 1. DÉCODAGE (Délégué à l'encodeur JSON)
        # Convertit les octets bruts en dictionnaire Python
        dict_in = self.server.encodage.decode(raw_data)
        if not dict_in: 
            # Si le décodage échoue, on arrête le traitement
            return
        
        # 2. LOGIQUE MÉTIER (Déléguée au UdpController)
        # Vérifie qu'un callback de traitement est défini
        if self.server.logic_callback:
            # Exécute la logique métier (requête poll, message, etc.)
            dict_out = self.server.logic_callback(dict_in)
            
            # 3. ENCODAGE ET ENVOI DE LA RÉPONSE
            if dict_out:
                # Convertit le dictionnaire de réponse en octets JSON
                response_bytes = self.server.encodage.encode(dict_out)
                # Envoie la réponse au client (Android) via UDP
                socket.sendto(response_bytes, self.client_address)
        else:
            print("[Avertissement] Message ignoré : Aucun logic_callback défini.")

class CustomUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    """
    Serveur UDP personnalisé avec support du threading et de callbacks personnalisés.
    Permet de configurer l'encodeur et la logique de traitement des requêtes.
    """
    def __init__(self, server_address, RequestHandlerClass, logic_callback, encodage):
        """
        Initialise le serveur UDP.
        
        Args:
            server_address : Tuple (host, port) du serveur
            RequestHandlerClass : Classe gestionnaire des requêtes (ThreadedUDPRequestHandler)
            logic_callback : Fonction de traitement des requêtes
            encodage : Encodeur pour convertir octets <-> dictionnaires
        """
        # Appelle le constructeur parent du serveur UDP
        super().__init__(server_address, RequestHandlerClass)
        # Stocke le callback de logique métier
        self.logic_callback = logic_callback 
        # Stocke l'encodeur JSON pour utilisation dans le gestionnaire
        self.encodage = encodage

class UdpAdapter:
    """
    Adaptateur UDP principal.
    Encapsule le serveur UDP et fournit les méthodes start/stop pour contrôler le service.
    """
    def __init__(self, host, port, encodage, logic_callback=None):
        """
        Initialise l'adaptateur UDP.
        
        Args:
            host : Adresse IP du serveur (ex: "0.0.0.0" pour écouter tous les interfaces)
            port : Port UDP (ex: 5005)
            encodage : Encodeur pour les requêtes/réponses
            logic_callback : Fonction de traitement initial (peut être définie plus tard)
        """
        # Crée le serveur UDP personnalisé avec les paramètres fournis
        self.server = CustomUDPServer((host, port), ThreadedUDPRequestHandler, logic_callback, encodage)
        
    def set_logic_callback(self, logic_callback):
        """Définit ou modifie le callback de logique métier (appel du UdpController)."""
        self.server.logic_callback = logic_callback
        
    def start(self):
        """Démarre le serveur UDP dans un thread daemon pour écouter les requêtes."""
        print(f"[Réseau] Démarrage de l'adaptateur UDP sur {self.server.server_address}...")
        # Crée un thread qui exécutera serve_forever() (boucle d'écoute infinie)
        self.thread = threading.Thread(target=self.server.serve_forever)
        # Configure le thread comme daemon (s'arrête avec le programme principal)
        self.thread.daemon = True
        # Démarre le thread
        self.thread.start()
        
    def stop(self):
        """Arrête le serveur UDP et ferme les connexions."""
        print("[Réseau] Arrêt de l'adaptateur UDP...")
        # Arrête la boucle d'écoute du serveur
        self.server.shutdown()
        # Attend la fin du thread avec timeout de 1 seconde
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        # Ferme complètement le socket du serveur
        self.server.server_close()