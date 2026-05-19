# Import du serveur IoT principal
from core.server import ServerIot
# Import des encodeurs (binaire pour série, JSON pour UDP)
from implementations.encodages import BinaryEncodage, JsonEncodage
# Import du stockage en base de données SQLite
from implementations.storages import SQLiteStorage
# Import des adaptateurs pour la communication série et UDP
from adapter import SerialAdapter, UdpAdapter
# Import du stockage fichier (alternative)
from implementations.storages.storage import FileStorage



# ===== ÉTAPE 1 : INITIALISATION DES COMPOSANTS =====

# Crée l'encodeur binaire pour la communication série avec les capteurs
serial_encodage = BinaryEncodage() 
# Crée l'encodeur JSON pour les requêtes UDP depuis l'app Android
json_encodage = JsonEncodage()
# Initialise la base de données SQLite pour stocker les mesures
stockage = SQLiteStorage("values.db")
# Alternative : utiliser un stockage en fichier texte au lieu de BDD
#stockage = FileStorage("values.txt")

# ===== ÉTAPE 2 : CONFIGURATION DES ADAPTATEURS =====

# Configure l'adaptateur série pour communiquer avec le micro:bit/passerelle
# Port : COM7 (à adapter selon votre système)
# Baudrate : 115200 (vitesse de transmission standard)
adapter_serial = SerialAdapter(
    port="COM7", 
    baudrate=115200, 
)

# Configure l'adaptateur UDP pour les requêtes de l'app Android
# Host : 0.0.0.0 (écoute sur tous les interfaces réseau)
# Port : 10000 (port UDP d'écoute)
# Encodage : JSON pour les messages réseau
udp_adapter = UdpAdapter(
    "0.0.0.0", 
    10000, 
    encodage=json_encodage)

# ===== ÉTAPE 3 : INJECTION DES DÉPENDANCES =====

# Crée le serveur IoT en lui passant tous les composants initialisés
serveur = ServerIot(
    adapter_serial=adapter_serial,      # Communication série avec les capteurs
    udp_adapter=udp_adapter,             # Communication UDP avec Android
    serial_encodage=serial_encodage,     # Encodeur binaire pour la série
    storage=stockage,                    # Base de données pour les mesures
    adresse=00                           # Adresse unique du contrôleur
)


# ===== ÉTAPE 4 : DÉMARRAGE DU SERVEUR =====

# Lance le serveur IoT (démarre les adaptateurs série et UDP)
serveur.start()