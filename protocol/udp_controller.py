from core.model import Model

class UdpController:
    """
    Le Cerveau du protocole UDP.
    Reçoit des dictionnaires, interroge la BDD ou le matériel, et renvoie des dictionnaires.
    """
    def __init__(self, storage, serial_adapter=None, serial_encodage=None, mon_adresse=0):
        # Storage : instance de la base de données pour stocker/récupérer les données des capteurs
        self.storage = storage
        # Serial adapter : interface pour communiquer avec le matériel via UART
        self.serial_adapter = serial_adapter
        # Serial encodage : encodeur pour convertir les modèles en format compatible avec la passerelle
        self.serial_encodage = serial_encodage
        # Mon adresse : l'adresse unique de ce contrôleur sur le réseau
        self.mon_adresse = mon_adresse
        # Caractères autorisés pour les ordres de commande (T=température, L=luminosité, H=humidité, P=pression, U=UV)
        self.ALLOWED_CHARS = set("TLHPU")

    def process_request(self, data_in: dict) -> dict:
        """Point d'entrée appelé par l'UdpAdapter."""
        print(f"[Protocole UDP] Requête reçue : {data_in}")
        
        # Extrait la méthode (type de requête) du dictionnaire d'entrée
        method = data_in.get("method")
        
        # --- ROUTAGE DES COMMANDES ---
        # Dirige la requête vers le gestionnaire approprié en fonction de la méthode
        match method:
            case "poll":
                # Requête de lecture des données d'un capteur depuis la BDD
                return self._handle_poll(data_in)
                
            case "message": # MODIF 3 : On écoute la méthode "message" envoyée par Android
                # Requête de commande matérielle envoyée par l'app Android
                return self._handle_message(data_in)
                 
            case _:
                # Gère les méthodes non reconnues
                return {"status": "error", "message": f"Méthode '{method}' inconnue"}

    # --- LOGIQUE DÉTAILLÉE DES COMMANDES ---

    def _handle_poll(self, data: dict) -> dict:
        """Gère la demande de lecture en base de données."""
        # Récupère l'adresse du capteur dont on souhaite les données
        address_demandee = data.get("address")
        
        # MODIF SQLITE : On utilise ta fonction get_last_n qui gère tout (même si l'adresse est None !)
        # Récupère la dernière mesure pour le capteur spécifié
        list_data = self.storage.get_last_n(1, address_demandee)
        
        # Vérifie si des données ont été trouvées en base de données
        if not list_data:
            return {"status": "error", "message": "Aucune donnée disponible sur le serveur."}

        # get_last_n(1) renvoie une liste d'1 seul élément, on prend donc l'index 0
        data_last = list_data[0]
        
        # ALIGNEMENT DES CLÉS AVEC ANDROID ET FORMATTAGE
        # Retourne les données formatées pour l'application Android (clés standards et valeurs avec 2 décimales)
        return {
            "status": "success",
            "address": data_last.address, 
            "formats": data_last.formats,
            "temperature": f"{data_last.temperature:.2f}",
            "humidity": f"{data_last.humidity:.2f}",
            "light": f"{data_last.luminosity:.2f}", 
            "pressure": f"{data_last.pressure:.2f}",
            "uv": f"{data_last.uv:.2f}",
        }

    def _handle_message(self, data: dict) -> dict:
        """Gère la demande d'action matérielle envoyée par l'EditText d'Android."""
        # Vérifie que le système matériel est connecté via l'adaptateur série
        if not self.serial_adapter:
            return {"status": "error", "message": "Le système matériel n'est pas connecté."}
        
        # Extrait et normalise l'ordre reçu : supprime espaces inutiles et convertit en majuscule
        # L'application Android place le texte dans la variable "message"
        nouvel_ordre = data.get("message").strip().upper() # On force en majuscule au cas où
        # Récupère l'adresse du capteur cible de la commande
        adress_capteur = data.get("address")
        
        # Vérifie que la commande n'est pas vide
        if not nouvel_ordre:
            return {"status": "error", "message": "L'ordre envoyé est vide."}

        # Valide que tous les caractères de la commande sont autorisés
        if not set(nouvel_ordre).issubset(self.ALLOWED_CHARS) :
            return {"status": "error", "message": f"Formats invalides. Seuls les caractères {self.ALLOWED_CHARS} sont autorisés."}

        # MODIF 4 : ENVOI TEXTE BRUT POUR LA PASSERELLE
        # On n'encode PAS en binaire 30 octets. La passerelle attend juste un String avec un \n
        # Crée un modèle de commande avec les paramètres nécessaires
        commande_model = Model(adresse_dest= adress_capteur, address=self.mon_adresse, formats=nouvel_ordre, end=255)
        
        # Encode le modèle de commande au format attendu par la passerelle série
        commande_encoder = self.serial_encodage.encode(commande_model)
        # Convertit le string en bytes et l'envoie sur l'UART du matériel
        self.serial_adapter.send_raw(commande_encoder)
        
        # Retourne un accusé de réception de la commande
        return {"status": "success", "message": f"Ordre '{nouvel_ordre}' transmis au capteur."}