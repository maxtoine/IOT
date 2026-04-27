import json

from interface.interface_encodage import InterfaceEncodage

class JsonEncodage(InterfaceEncodage):
    """
    S'occupe uniquement de la traduction entre des octets bruts (réseau)
    et des dictionnaires Python.
    """
    def decode(self, raw_data: bytes) -> dict:
        try:
            # On nettoie, on passe en texte, puis on convertit en dictionnaire
            decoded_text = raw_data.strip().decode('utf-8')
            return json.loads(decoded_text)
        except json.JSONDecodeError:
            print("[Erreur Encodage] Le message reçu n'est pas un JSON valide.")
            return None
        except Exception as e:
            print(f"[Erreur Encodage] Problème de décodage : {e}")
            return None

    def encode(self, data_dict: dict) -> bytes:
        """Prend un dictionnaire Python, le convertit en JSON, puis en octets."""
        json_text = json.dumps(data_dict)
        return json_text.encode('utf-8')