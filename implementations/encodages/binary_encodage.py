import ctypes
from interface.interface_encodage import InterfaceEncodage
from core.model import Model

class MaTrame(ctypes.LittleEndianStructure):
    _pack_ = 1  # Pas d'alignement d'octets (17 octets pile)
    _fields_ = [
        ("adresse", ctypes.c_ubyte),    # 1 octet
        ("tag",     ctypes.c_char * 3), # 3 octets
        ("f1",      ctypes.c_float),    # 4 octets
        ("f2",      ctypes.c_float),    # 4 octets
        ("f3",      ctypes.c_float),    # 4 octets
        ("fin",     ctypes.c_ubyte)     # 1 octet
    ]

class BinaryEncodage(InterfaceEncodage):
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
        trame = MaTrame.from_buffer_copy(data)
        return Model(
            address=trame.adresse,
            formats=trame.tag.decode('utf-8'),
            value_a=trame.f1,
            value_b=trame.f2,
            value_c=trame.f3,
            end=trame.fin
        )

    
    def read_from_port(self, serial_port) -> Model:
        # Le binaire lit exactement 17 octets
        taille = ctypes.sizeof(MaTrame)
        if serial_port.in_waiting >= taille:
            msg = serial_port.read(taille)
            return self.decode(msg)
        return None
