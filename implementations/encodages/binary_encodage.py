import ctypes
import struct
from core.model import Model
from interface.interface_encodage import InterfaceEncodage
import logging

logger = logging.getLogger(__name__)

# --- CONFIGURATION XTEA ---

XTEA_KEY = [0xACE1ACE1, 0x12345678, 0xDEADBEEF, 0xBEEFFACE] # dois etre pareil que celui dans le mircobit
ROUNDS = 32

#Champ    Taille    Contenu fixe
#adresse    1 oct.    ID (42)
#tag    3 oct.    "TLHPU"
#f1    4 oct.    Température (T)
#f2    4 oct.    Luminosité (L)
#f3    4 oct.    Humidité (H)
#f4    4 oct.    Pression (P)
#f5    4 oct.    UV (U)
#fin    1 oct.    255
def xtea_decrypt(v, k):
    v0, v1 = v
    delta = 0x9E3779B9
    num_rounds = 32
    # On calcule le sum final tel qu'il est après 32 rounds en C++
    sum_val = (delta * num_rounds) & 0xFFFFFFFF
    
    for _ in range(num_rounds):
        # 1. On déchiffre v1 en premier (ordre inverse de l'encryption)
        # Note : on applique le masque & 0xFFFFFFFF après CHAQUE opération sensible
        v1 = (v1 - (((((v0 << 4) & 0xFFFFFFFF) ^ (v0 >> 5)) + v0) ^ (sum_val + k[(sum_val >> 11) & 3]))) & 0xFFFFFFFF
        
        # 2. On décrémente sum
        sum_val = (sum_val - delta) & 0xFFFFFFFF
        
        # 3. On déchiffre v0
        v0 = (v0 - (((((v1 << 4) & 0xFFFFFFFF) ^ (v1 >> 5)) + v1) ^ (sum_val + k[sum_val & 3]))) & 0xFFFFFFFF
        
    return v0, v1

# --- STRUCTURE DE 30 OCTETS ---
class MaTrame(ctypes.LittleEndianStructure):
    _pack_ = 1  
    _fields_ = [
        ("adresse", ctypes.c_ubyte),        # 1 octet
        ("tag",     ctypes.c_char * 4),     # 4 octets (Réduit pour XTEA)
        ("payload", ctypes.c_uint32 * 6),   # 24 octets (Données chiffrées)
        ("fin",     ctypes.c_ubyte)         # 1 octet
    ]

class BinaryEncodage(InterfaceEncodage):
    # La taille est maintenant automatiquement 30 octets via ctypes
    framing_length = ctypes.sizeof(MaTrame) 

    def extract_frames(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        trames_completes = []
        taille = self.framing_length
        while len(buffer) >= taille:
            trames_completes.append(buffer[:taille])
            buffer = buffer[taille:]
        return trames_completes, buffer

    def extract_address(self, data: bytes) -> str:
        return str(data[0])
    
    def decode(self, data: bytes) -> Model:
        trame = MaTrame.from_buffer_copy(data)
        p = list(trame.payload) # Contient les 6 uint32 chiffrés
        
        decrypted_uints = []
        # On traite les 3 blocs de 8 octets (2 uint32 par bloc)
        for i in range(0, 6, 2):
            v0, v1 = xtea_decrypt((p[i], p[i+1]), XTEA_KEY)
            decrypted_uints.append(v0)
            decrypted_uints.append(v1)
            
        # On convertit les 6 entiers décryptés en 6 floats (Little Endian)
        raw_bytes = struct.pack('<6I', *decrypted_uints)
        floats = struct.unpack('<6f', raw_bytes)
        
        # floats[0]=T, floats[1]=L, floats[2]=H, floats[3]=P, floats[4]=U
        return Model(
            address=str(trame.adresse),
            formats=trame.tag.decode('utf-8', errors='ignore').strip(),
            temperature=floats[0],
            luminosity=floats[1],
            humidity=floats[2],
            pressure=floats[3],
            uv=floats[4],
            end=trame.fin
        )