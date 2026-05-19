# Import de l'interface pour la gestion du stockage des données
from interface.interface_save import InterfaceSave
# Import de l'interface pour l'encodage/décodage des données
from interface.interface_encodage import InterfaceEncodage
# Import du contrôleur UDP qui gère la logique des requêtes
from protocol import UdpController

# Module de temps pour les vérifications d'inactivité
import time

class ServerIot:
    """
    Serveur IoT principal : orchestre la communication série, UDP et la gestion des données.
    Gère la réception des données capteur via série et communique avec les clients Android via UDP.
    """
   
    def __init__(self, adapter_serial, udp_adapter, serial_encodage, storage, adresse=0):
        """
        Initialise le serveur IoT avec tous les adaptateurs nécessaires.
        
        Args:
            adapter_serial : Adaptateur pour la communication série (micro:bit, etc.)
            udp_adapter : Adaptateur pour les requêtes UDP (Android)
            serial_encodage : Encodeur/décodeur pour le format des trames série
            storage : Instance de la base de données
            adresse : Adresse unique de ce serveur sur le réseau (par défaut 0)
        """
        
        # Adaptateur série pour communiquer avec le matériel
        self.adapter_serial = adapter_serial
        # Adaptateur UDP pour communiquer avec l'app Android
        self.udp_adapter = udp_adapter
        # Encodeur/décodeur pour les trames série
        self.serial_encodage = serial_encodage
        # Base de données pour stocker les mesures des capteurs
        self.storage = storage
        # Adresse unique de ce contrôleur sur le réseau
        self.mon_adresse = adresse

        # Le Cerveau UDP (qui a besoin du stockage et de l'accès matériel)
        # Crée le contrôleur UDP responsable du traitement des requêtes
        self.udp_controller = UdpController(
            storage=self.storage, 
            serial_adapter=self.adapter_serial,
            serial_encodage=self.serial_encodage,
            mon_adresse=self.mon_adresse
        )
        
        # Attache la méthode de traitement des requêtes UDP au callback de l'adaptateur
        self.udp_adapter.set_logic_callback(self.udp_controller.process_request)

    def start(self):
        """Démarre le serveur IoT : lance l'adaptateur UDP et la boucle de lecture série."""
        print("Starting IoT Server...")
        # Démarre l'adaptateur UDP pour écouter les requêtes des clients
        self.udp_adapter.start()
        # Lance la boucle de surveillance de la communication série
        self.run_serial_loop()
    
    def run_serial_loop(self):
        """
        Boucle infinie de lecture série.
        Reçoit les trames des capteurs, les décode et les sauvegarde en base de données.
        """
        # Buffer global pour accumuler les octets reçus jusqu'à former des trames complètes
        buffer_global = b""
        print(f"[Serial] Surveillance active sur l'adresse : {self.mon_adresse}")
        # Timestamp du dernier message de heartbeat (pour afficher "toujours actif" périodiquement)
        last_heartbeat = time.time()

        while True:
            try:
                # Affiche un message de heartbeat toutes les 5 secondes pour montrer que le serveur fonctionne
                if time.time() - last_heartbeat > 5:
                    print("[Système] Toujours en attente de données...")
                    last_heartbeat = time.time()

                # Lit les octets bruts disponibles depuis la liaison série
                raw_chunk = self.adapter_serial.read_raw()
                
                if raw_chunk:
                    # Ajoute les nouveaux octets reçus au buffer global
                    buffer_global += raw_chunk
                    
                    # Extrait les trames complètes du buffer en utilisant le délimiteur défini
                    trames_completes, buffer_global = self.serial_encodage.extract_frames(buffer_global)
                    
                    if trames_completes:
                        print(f"DEBUG: {len(trames_completes)} trame(s) extraite(s) !")
                    
                    # Traite chaque trame reçue
                    for trame in trames_completes:
                        # Extrait l'adresse de destination de la trame
                        addr = self.serial_encodage.extract_address(trame)

                        # Vérifie que cette trame est destinée à ce serveur
                        if int(addr) == int(self.mon_adresse):
                            # Décode la trame pour obtenir un modèle de données exploitable
                            model = self.serial_encodage.decode(trame)
                            print(f"[+] Message décodé : {model}")
                            # Sauvegarde les données du capteur en base de données
                            self.storage.save_data(model)
                        else:
                            # Ignore les trames destinées à d'autres adresses
                            print(f"[-] Adresse {addr} ignorée.")
                # Pause courte pour éviter de surcharger le CPU
                time.sleep(0.1)
            except Exception as e:
                # Gère les erreurs lors de la réception ou du traitement des données
                print(f"ERREUR DANS LA BOUCLE : {e}")
                
    def stop(self):
        """Arrête le serveur IoT et ferme toutes les connexions."""
        # Ferme la connexion série
        self.adapter_serial.close_connection()
        # Arrête l'adaptateur UDP
        self.udp_adapter.stop()
        print("IoT Server stopped.")