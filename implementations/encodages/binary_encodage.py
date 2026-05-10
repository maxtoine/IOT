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
    # On s'assure que les entrées sont strictement sur 32 bits
    v0 = v[0] & 0xFFFFFFFF
    v1 = v[1] & 0xFFFFFFFF
    
    delta = 0x9E3779B9
    # Le 'sum' initial après 32 itérations d'encryption
    sum_val = (delta * 32) & 0xFFFFFFFF
    
    for _ in range(32):
        # --- Déchiffrement de v1 ---
        # term1 = (((v0 << 4) ^ (v0 >> 5)) + v0)
        term1 = ((((v0 << 4) & 0xFFFFFFFF) ^ (v0 >> 5)) + v0) & 0xFFFFFFFF
        # term2 = sum + k[(sum >> 11) & 3]
        term2 = (sum_val + k[(sum_val >> 11) & 3]) & 0xFFFFFFFF
        # v1 -= term1 ^ term2
        v1 = (v1 - (term1 ^ term2)) & 0xFFFFFFFF
        
        # --- Décrémentation de sum ---
        sum_val = (sum_val - delta) & 0xFFFFFFFF
        
        # --- Déchiffrement de v0 ---
        # term3 = (((v1 << 4) ^ (v1 >> 5)) + v1)
        term3 = ((((v1 << 4) & 0xFFFFFFFF) ^ (v1 >> 5)) + v1) & 0xFFFFFFFF
        # term4 = sum + k[sum & 3]
        term4 = (sum_val + k[sum_val & 3]) & 0xFFFFFFFF
        # v0 -= term3 ^ term4
        v0 = (v0 - (term3 ^ term4)) & 0xFFFFFFFF
        
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
        
        # === LE DIAGNOSTIC ULTIME ===
        print(f"RAW PAYLOAD (Chiffré) : {p}")
        
        decrypted_uints = []
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