import ctypes
from core.model import Model
from interface.interface_encodage import InterfaceEncodage
import logging

logger = logging.getLogger(__name__)

class MaTrame(ctypes.LittleEndianStructure):
    _pack_ = 1  
    _fields_ = [
        ("adresse", ctypes.c_ubyte),
        ("tag",     ctypes.c_char * 3),
        ("f1",      ctypes.c_float),
        ("f2",      ctypes.c_float),
        ("f3",      ctypes.c_float),
        ("fin",     ctypes.c_ubyte)
    ]

class BinaryEncodage(InterfaceEncodage):
  
    framing_length = ctypes.sizeof(MaTrame) # 17 octets

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
        
    def _extract_frames_impl(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        trames_completes = []
        taille_trame = self.framing_length # 17 octets
        
        # On boucle tant qu'on a assez d'octets pour faire au moins une trame complète
        while len(buffer) >= taille_trame:
            # On extrait les 17 premiers octets exacts
            trame = buffer[:taille_trame]
            trames_completes.append(trame)
            
            # On retire ces 17 octets du buffer pour garder ce qui reste
            buffer = buffer[taille_trame:]
            
        return trames_completes, buffer
       
    def extract_address(self, data: bytes) -> str:
        # Ultra rapide : l'adresse est le TOUT PREMIER octet (index 0) !
        if len(data) < 1:
            raise ValueError("Données insuffisantes pour extraire l'adresse")
        return str(data[0])
    
    def encode(self, data: Model) -> bytes:
        trame = MaTrame()
        trame.adresse = int(data.address)
        trame.tag = data.formats.encode('utf-8')
        trame.f1 = data.value_a
        trame.f2 = data.value_b
        trame.f3 = data.value_c
        trame.fin = int(data.end)
        return bytes(trame)

    def decode(self, data: bytes) -> Model:
        if len(data) != self.framing_length:
            raise ValueError(f"Taille de trame invalide: {len(data)} octets (attendu {self.framing_length})")
            
        trame = MaTrame.from_buffer_copy(data)
        formats = trame.tag.decode('utf-8')
        
        return Model(
            address=str(trame.adresse),
            formats=formats,
            value_a=trame.f1,
            value_b=trame.f2,
            value_c=trame.f3,
            end=trame.fin
        )