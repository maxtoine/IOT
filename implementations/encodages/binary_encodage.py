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
        ("f1",      ctypes.c_float),  # temperature
        ("f2",      ctypes.c_float),  # luminosity
        ("f3",      ctypes.c_float),  # humidity
        ("f4",      ctypes.c_float),  # pressure
        ("f5",      ctypes.c_float),  # uv
        ("fin",     ctypes.c_ubyte)
    ]

class BinaryEncodage(InterfaceEncodage):
    framing_length = ctypes.sizeof(MaTrame)  # 25 octets

    def extract_frames(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        try:
            return self._extract_frames_impl(buffer)
        except Exception as e:
            logger.error(f"Erreur d'extraction des trames: {e}")
            return [], buffer

    def _extract_frames_impl(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        trames_completes = []
        taille_trame = self.framing_length  # 25 octets
        while len(buffer) >= taille_trame:
            trame = buffer[:taille_trame]
            trames_completes.append(trame)
            buffer = buffer[taille_trame:]
        return trames_completes, buffer

    def extract_address(self, data: bytes) -> str:
        if len(data) < 1:
            raise ValueError("Données insuffisantes pour extraire l'adresse")
        return str(data[0])

    def encode(self, data: Model) -> bytes:
        trame = MaTrame()
        trame.adresse = int(data.address)
        trame.tag     = data.formats.encode('utf-8')
        trame.f1      = data.temperature
        trame.f2      = data.luminosity
        trame.f3      = data.humidity
        trame.f4      = data.pressure
        trame.f5      = data.uv
        trame.fin     = int(data.end)
        return bytes(trame)

    def decode(self, data: bytes) -> Model:
        if len(data) != self.framing_length:
            raise ValueError(f"Taille de trame invalide: {len(data)} octets (attendu {self.framing_length})")
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