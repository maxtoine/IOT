import ctypes
from interface.interface_protocol import InterfaceProtocol
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

class BinaryProtocol(InterfaceProtocol):
    def encode(self, data: Model) -> bytes:
        trame = MaTrame()
        trame.adresse = int(data.adress)
        trame.tag = data.formats.encode('utf-8')
        trame.f1 = data.data_1
        trame.f2 = data.data_2
        trame.f3 = data.data_3
        trame.fin = int(data.end)
        return bytes(trame)

    def decode(self, data: bytes) -> Model:
        trame = MaTrame.from_buffer_copy(data)
        return Model(
            adress=trame.adresse,
            formats=trame.tag.decode('utf-8'),
            data_1=trame.f1,
            data_2=trame.f2,
            data_3=trame.f3,
            end=trame.fin
        )

    def size(self) -> int:
        return ctypes.sizeof(MaTrame)


class TextProtocol(InterfaceProtocol):
    def encode(self, data: Model) -> bytes:
        values = [
            str(data.adress),
            data.formats,
            str(data.data_1),
            str(data.data_2),
            str(data.data_3),
            str(data.end),
        ]
        return ";".join(values).encode("utf-8")

    def decode(self, data: bytes) -> Model:
        text = data.decode("utf-8") if isinstance(data, (bytes, bytearray)) else str(data)
        parts = [part.strip() for part in text.split(";")]
        if len(parts) != 6:
            raise ValueError("TextProtocol attend 6 champs séparés par ';'.")
        return Model(
            adress=parts[0],
            formats=parts[1],
            data_1=float(parts[2]),
            data_2=float(parts[3]),
            data_3=float(parts[4]),
            end=float(parts[5]),
        )

    def size(self) -> int:
        return 0