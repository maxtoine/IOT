import ctypes
import struct
from core.model import Model
from interface.interface_encodage import InterfaceEncodage
from implementations.cryptage.cryptage import Cryptage
import logging

logger = logging.getLogger(__name__)

# --- STRUCTURE DE 32 OCTETS ---
# (1 octet dest + 1 octet source + 5 octets tag + 24 octets payload + 1 octet fin = 32)
class MaTrame(ctypes.LittleEndianStructure):
    _pack_ = 1  
    _fields_ = [
        ('adresse_dest',   ctypes.c_ubyte),         # 1 octet
        ("adresse_source", ctypes.c_ubyte),         # 1 octet
        ("tag",            ctypes.c_char * 5),      # 5 octets
        ("payload",        ctypes.c_uint32 * 6),    # 24 octets
        ("fin",            ctypes.c_ubyte)          # 1 octet
    ]

class BinaryEncodage(InterfaceEncodage):
    framing_length = ctypes.sizeof(MaTrame)
    
    def __init__(self):
        self.cryptage = Cryptage()

    def extract_frames(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        trames_completes = []
        taille = self.framing_length
        while len(buffer) >= taille:
            trames_completes.append(buffer[:taille])
            buffer = buffer[taille:]
        return trames_completes, buffer

    def extract_address(self, data: bytes) -> str:
        # data[0] correspond à adresse_dest, data[1] à adresse_source
        return str(data[0]) 
    
    def encode(self, data: Model) -> bytes:
        # 1. On prépare nos 6 floats (dont le 0.0 de padding)
        floats = [
            data.temperature,
            data.luminosity,
            data.humidity,
            data.pressure,
            data.uv,
            0.0
        ]
        
        # 2. Conversion des floats en octets purs (24 octets)
        raw_bytes = struct.pack('<6f', *floats)
        
        # 3. Chiffrement
        encrypted_bytes = self.cryptage.encryptage(raw_bytes)
        
        # On copie directement la mémoire dans le payload de Ctypes
        payload_array = (ctypes.c_uint32 * 6).from_buffer_copy(encrypted_bytes)
        
        formatted_tag = data.formats.encode('utf-8')[:5].ljust(5, b'\x00')
        octet_fin = getattr(data, 'end', 255)
        
        # 4. Création de la trame finale
        trame = MaTrame(
            adresse_dest=int(data.adresse_dest),
            adresse_source=int(data.address),
            tag=formatted_tag,
            payload=payload_array,
            fin=int(octet_fin)
        )
        
        return bytes(trame)
    
    def decode(self, data: bytes) -> Model:
        trame = MaTrame.from_buffer_copy(data)
        
        # On extrait les 24 octets de la trame
        payload_bytes = bytes(trame.payload) 
        
        # On déchiffre pour obtenir 24 octets clairs
        decrypted_bytes = self.cryptage.decryptage(payload_bytes)
            
        # === ÉTAPE 2 : TRANSFORMATION EN FLOAT ===
        # Les octets étant DÉJÀ purs, on les unpack directement !
        floats = struct.unpack('<6f', decrypted_bytes)
        
        return Model(
            adresse_dest=str(trame.adresse_dest),
            address=str(trame.adresse_source),
            formats=trame.tag.decode('utf-8', errors='ignore').strip().strip('\x00'),
            temperature=floats[0],
            luminosity=floats[1],
            humidity=floats[2],
            pressure=floats[3],
            uv=floats[4],
            end=trame.fin
        )