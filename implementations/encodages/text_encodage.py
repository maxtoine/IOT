from core.model import Model
from interface.interface_encodage import InterfaceEncodage
import logging

logger = logging.getLogger(__name__)

class TextEncodage(InterfaceEncodage):


    def _extract_frames_impl(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        trames_completes = []
        
        # On boucle tant qu'il y a un saut de ligne dans le buffer
        while b'\n' in buffer:
            # maxsplit=1 permet de couper juste au premier \n trouvé
            trame, buffer = buffer.split(b'\n', 1)
            
            # On ignore les lignes vides qui pourraient survenir
            if trame.strip(): 
                trames_completes.append(trame)
                
        return trames_completes, buffer
    
    def extract_frames(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        """
        Extrait toutes les trames complètes du buffer.
        Retourne un tuple : (liste des trames complètes, le reste du buffer incomplet)
        """
        try:
            return self._extract_frames_impl(buffer)
        except Exception as e:
            logger.error(f"Erreur d'extraction des trames: {e}")
            return [], buffer # En cas d'erreur, on rend le buffer pour ne rien perdre
        
    def extract_address(self, data: bytes) -> str:
        # Ultra rapide : on coupe au premier ';' et on ne traduit que cette petite partie
        adresse_bytes = data.split(b';')[0] 
        return adresse_bytes.decode('utf-8').strip()
    
    def encode(self, data: Model) -> bytes:
        values = [
            data.address, data.formats, 
            str(data.value_a), str(data.value_b), 
            str(data.value_c), str(data.end)
        ]
        return (";".join(values) + "\n").encode("utf-8")

    def decode(self, data: bytes) -> Model:
        text = data.decode("utf-8").strip()
        parts = [part.strip() for part in text.split(";")]
        
        if len(parts) != 6:
            raise ValueError(f"Trame invalide: {text} (attendu 6 parties, reçu {len(parts)})")
            
        formats = parts[1].upper()
                    
        return Model(
            address=parts[0],
            formats=formats,
            value_a=parts[2],
            value_b=parts[3],
            value_c=parts[4],
            end=parts[5]
        )