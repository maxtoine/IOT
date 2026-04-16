from interface.interface_encodage import InterfaceEncodage
from core.model import Model

class TextEncodage(InterfaceEncodage):
    def encode(self, data: Model) -> bytes:
        values = [
            str(data.address),
            data.formats,
            str(data.value_a),
            str(data.value_b),
            str(data.value_c),
            str(data.end),
        ]
        return (";".join(values) + "\n").encode("utf-8")

    def decode(self, data) -> Model:
        print(f"[Texte] Décodage du message : {data}")
        text = data.decode("utf-8") if isinstance(data, (bytes, bytearray)) else str(data)
        parts = [part.strip() for part in text.split(";")]
        if len(parts) != 6:
            raise ValueError("TextProtocol attend 6 champs séparés par ';'.")
        return Model(
            address=parts[0],
            formats=parts[1],
            value_a=float(parts[2]),
            value_b=float(parts[3]),
            value_c=float(parts[4]),
            end=float(parts[5]),
        )
    
    def read_from_port(self, serial_port) -> Model:
        # Le texte lit jusqu'au \n
        if serial_port.in_waiting > 0:
            msg = serial_port.readline()
            print(f"[Texte] Message brut reçu : {msg}")
            if msg and len(msg.strip()) > 0:
                try:
                    return self.decode(msg)
                except ValueError as e:
                    print(f"[Texte] Trame ignorée : {e}")
        return None

