# Module pour la sérialisation et désérialisation JSON
import json

# Import de l'interface définissant les méthodes obligatoires pour un encodeur
from interface.interface_encodage import InterfaceEncodage

class JsonEncodage(InterfaceEncodage):
    """
    Implémentation d'un encodeur JSON.
    S'occupe uniquement de la traduction entre des octets bruts (réseau)
    et des dictionnaires Python.
    """
    def decode(self, raw_data: bytes) -> dict:
        """Convertit des octets bruts en dictionnaire Python."""
        try:
            # Nettoie les espaces superflus et convertit les octets en chaîne UTF-8
            decoded_text = raw_data.strip().decode('utf-8')
            # Parse la chaîne JSON et la convertit en dictionnaire Python
            return json.loads(decoded_text)
        except json.JSONDecodeError:
            # Gère le cas où le JSON est invalide (format incorrect)
            print("[Erreur Encodage] Le message reçu n'est pas un JSON valide.")
            return None
        except Exception as e:
            # Gère les autres erreurs possibles (encodage, etc.)
            print(f"[Erreur Encodage] Problème de décodage : {e}")
            return None

    def encode(self, data_dict: dict) -> bytes:
        """Convertit un dictionnaire Python en JSON, puis en octets pour le réseau."""
        # Sérialise le dictionnaire Python en chaîne JSON
        json_text = json.dumps(data_dict)
        # Encode la chaîne JSON en octets UTF-8 pour transmission réseau
        return json_text.encode('utf-8')