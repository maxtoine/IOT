import ctypes
from core.model import Model
from interface.interface_encodage import InterfaceEncodage
import logging

logger = logging.getLogger(__name__)

#Champ    Taille    Contenu fixe
#adresse    1 oct.    ID (42)
#tag    3 oct.    "TLHPU"
#f1    4 oct.    Température (T)
#f2    4 oct.    Luminosité (L)
#f3    4 oct.    Humidité (H)
#f4    4 oct.    Pression (P)
#f5    4 oct.    UV (U)
#fin    1 oct.    255

class MaTrame(ctypes.LittleEndianStructure):
    _pack_ = 1  
    _fields_ = [
        ("adresse", ctypes.c_ubyte),
        ("tag",     ctypes.c_char * 5), # 5 caractères pour le tag (ex: "T", "L", "H", "P", "U")
        ("f1",      ctypes.c_float), # T
        ("f2",      ctypes.c_float), # L
        ("f3",      ctypes.c_float), # H
        ("f4",      ctypes.c_float), # P
        ("f5",      ctypes.c_float), # U
        ("fin",     ctypes.c_ubyte)
    ]

class BinaryEncodage(InterfaceEncodage):
  
    framing_length = ctypes.sizeof(MaTrame) # 25 octets

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
        taille_trame = self.framing_length # 25 octets
        
        # On boucle tant qu'on a assez d'octets pour faire au moins une trame complète
        while len(buffer) >= taille_trame:
            # On extrait les 25 premiers octets exacts
            trame = buffer[:taille_trame]
            trames_completes.append(trame)
            
            # On retire ces 25 octets du buffer pour garder ce qui reste
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
        trame.f1      = data.temperature
        trame.f2      = data.luminosity
        trame.f3      = data.humidity
        trame.f4      = data.pressure
        trame.f5      = data.uv
        trame.fin = int(data.end)
        return bytes(trame)

    def decode(self, data: bytes) -> Model:
        trame = MaTrame.from_buffer_copy(data)
    
        return Model(
            address=str(trame.adresse),
            formats=trame.tag.decode('utf-8'),
            temperature=trame.f1,
            luminosity=trame.f2,
            humidity=trame.f3,
            pressure=trame.f4,
            uv=trame.f5,
            end=trame.fin
        )