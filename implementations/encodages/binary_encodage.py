import ctypes
import struct
from core.model import Model
from interface.interface_encodage import InterfaceEncodage
import logging

logger = logging.getLogger(__name__)

# --- CONFIGURATION XTEA ---
XTEA_KEY = [0xACE1ACE1, 0x12345678, 0xDEADBEEF, 0xBEEFFACE] 
ROUNDS = 32

def xtea_decrypt(v, k):
    # Les entrées sont des entiers, on sécurise juste sur 32 bits
    v0 = v[0] & 0xFFFFFFFF
    v1 = v[1] & 0xFFFFFFFF
    
    delta = 0x9E3779B9
    sum_val = (delta * 32) & 0xFFFFFFFF
    
    for _ in range(32):
        term1 = ((((v0 << 4) & 0xFFFFFFFF) ^ (v0 >> 5)) + v0) & 0xFFFFFFFF
        term2 = (sum_val + k[(sum_val >> 11) & 3]) & 0xFFFFFFFF
        v1 = (v1 - (term1 ^ term2)) & 0xFFFFFFFF
        
        sum_val = (sum_val - delta) & 0xFFFFFFFF
        
        term3 = ((((v1 << 4) & 0xFFFFFFFF) ^ (v1 >> 5)) + v1) & 0xFFFFFFFF
        term4 = (sum_val + k[sum_val & 3]) & 0xFFFFFFFF
        v0 = (v0 - (term3 ^ term4)) & 0xFFFFFFFF
        
    return v0, v1

# --- STRUCTURE DE 30 OCTETS ---
class MaTrame(ctypes.LittleEndianStructure):
    _pack_ = 1  
    _fields_ = [
        ("adresse", ctypes.c_ubyte),        # 1 octet
        ("tag",     ctypes.c_char * 5),     # 5 octets
        # ÉTAPE 1 : On lit les données chiffrées comme 6 entiers (24 octets)
        ("payload", ctypes.c_uint32 * 6),   
        ("fin",     ctypes.c_ubyte)         # 1 octet
    ]

class BinaryEncodage(InterfaceEncodage):
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
        p = list(trame.payload) # Contient les 6 entiers chiffrés
        
        decrypted_uints = []
        # On déchiffre les entiers 2 par 2
        for i in range(0, 6, 2):
            v0, v1 = xtea_decrypt((p[i], p[i+1]), XTEA_KEY)
            decrypted_uints.append(v0)
            decrypted_uints.append(v1)
            
        # === ÉTAPE 2 : TRANSFORMATION EN FLOAT ===
        # 1. On prend nos 6 entiers décryptés et on en fait un flux d'octets purs ('<6I')
        raw_bytes = struct.pack('<6I', *decrypted_uints)
        # 2. On indique à Python de lire ces octets purs comme étant 6 floats ('<6f')
        floats = struct.unpack('<6f', raw_bytes)
        
        # Le résultat est garanti : "floats" contient maintenant de vrais nombres à virgule !
        # floats[0]=T, floats[1]=L, floats[2]=H, floats[3]=P, floats[4]=U, floats[5]=0.0
        
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