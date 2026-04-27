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
        
        # On extrait la commande principale
        method = data_in.get("method")
        
        # --- ROUTAGE DES COMMANDES ---
        match method:
            case "poll":
                return self._handle_poll(data_in)
                
            case "formats":
                return self._handle_formats(data_in)
                 
            case _:
                return {"status": "error", "message": f"Méthode '{method}' inconnue"}

    # --- LOGIQUE DÉTAILLÉE DES COMMANDES ---

    def _handle_poll(self, data: dict) -> dict:
        """Gère la demande de lecture en base de données."""
        address_demandee = data.get("address")
        
        if address_demandee is None:
             return {"status": "error", "message": "Il manque la clé 'address' dans la requête."}

        list_data = self.storage.search_data(address_demandee)
        
        if not list_data:
            return {"status": "error", "message": f"Aucune donnée pour l'adresse {address_demandee}"}

        data_last = list_data[0]
        
        # On construit le dictionnaire de réponse
        return {
            "status": "success",
            "address": data_last.address,
            "formats": data_last.formats,
            "temperature": data_last.temperature,
            "humidity": data_last.humidity,
            "luminosity": data_last.luminosity,
            "pressure": data_last.pressure,
            "uv": data_last.uv,
        }

    def _handle_formats(self, data: dict) -> dict:
        """Gère la demande d'action matérielle (via l'UART)."""
        if not self.serial_adapter or not self.serial_encodage:
            return {"status": "error", "message": "Le système matériel n'est pas connecté."}
        
        format = data.get("formats", "")
        if format and not set(format).issubset(self.ALLOWED_CHARS) :
            return {"status": "error", "message": f"Formats invalides. Seuls les caractères {self.ALLOWED_CHARS} sont autorisés."}

        if len(format) > 5:
            return {"status": "error", "message": "Le champ 'formats' doit contenir au moins 5 caractères."}

        # 1. On crée le Model à partir de la demande Android
        model_a_envoyer = Model(
            address_destination=data.get("address", 0),
            address=self.mon_adresse,
            formats=format, # Un tag fixe de 5 caractères pour les commandes
            temperature=0.0, # Valeur envoyée par l'Android
            luminosity=0.0, humidity=0.0, pressure=0.0, uv=0.0, end=255
        )

        # 2. On transforme le Model en 28 octets via ton BinaryEncodage
        trame_binaire = self.serial_encodage.encode(model_a_envoyer)

        # 3. On envoie sur le port Série
        self.serial_adapter.send_raw(trame_binaire)
        
        return {"status": "success", "message": "Ordre binaire transmis au matériel."}