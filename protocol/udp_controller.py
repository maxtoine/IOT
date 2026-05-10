from core.model import Model

class UdpController:
    """
    Le Cerveau du protocole UDP.
    Reçoit des dictionnaires, interroge la BDD ou le matériel, et renvoie des dictionnaires.
    """
    def __init__(self, storage, serial_adapter=None, serial_encodage=None, mon_adresse=0):
        self.storage = storage
        self.serial_adapter = serial_adapter
        self.serial_encodage = serial_encodage
        self.mon_adresse = mon_adresse
        self.ALLOWED_CHARS = set("TLHPU")

    def process_request(self, data_in: dict) -> dict:
        """Point d'entrée appelé par l'UdpAdapter."""
        print(f"[Protocole UDP] Requête reçue : {data_in}")
        
        method = data_in.get("method")
        
        # --- ROUTAGE DES COMMANDES ---
        match method:
            case "poll":
                return self._handle_poll(data_in)
                
            case "message": # MODIF 3 : On écoute la méthode "message" envoyée par Android
                return self._handle_message(data_in)
                 
            case _:
                return {"status": "error", "message": f"Méthode '{method}' inconnue"}

    # --- LOGIQUE DÉTAILLÉE DES COMMANDES ---

    def _handle_poll(self, data: dict) -> dict:
        """Gère la demande de lecture en base de données."""
        address_demandee = data.get("address")
        
        # MODIF SQLITE : On utilise ta fonction get_last_n qui gère tout (même si l'adresse est None !)
        list_data = self.storage.get_last_n(1, address_demandee)
        
        if not list_data:
            return {"status": "error", "message": "Aucune donnée disponible sur le serveur."}

        # get_last_n(1) renvoie une liste d'1 seul élément, on prend donc l'index 0
        data_last = list_data[0] 
        
        # ALIGNEMENT DES CLÉS AVEC ANDROID ET FORMATTAGE
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
        if not self.serial_adapter:
            return {"status": "error", "message": "Le système matériel n'est pas connecté."}
        
        # L'application Android place le texte dans la variable "message"
        nouvel_ordre = data.get("message", "").strip().upper() # On force en majuscule au cas où
        
        if not nouvel_ordre:
            return {"status": "error", "message": "L'ordre envoyé est vide."}

        if not set(nouvel_ordre).issubset(self.ALLOWED_CHARS) :
            return {"status": "error", "message": f"Formats invalides. Seuls les caractères {self.ALLOWED_CHARS} sont autorisés."}

        # MODIF 4 : ENVOI TEXTE BRUT POUR LA PASSERELLE
        # On n'encode PAS en binaire 30 octets. La passerelle attend juste un String avec un \n
        commande_texte = f"{nouvel_ordre}\n"
        
        # On convertit le string en bytes et on l'envoie sur l'UART
        self.serial_adapter.send_raw(commande_texte.encode('utf-8'))
        
        return {"status": "success", "message": f"Ordre '{nouvel_ordre}' transmis au capteur."}