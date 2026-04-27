from core.model import Model

class InterfaceEncodage:
    # Indique à l'adaptateur comment découper les trames ("line" ou "fixed")
    
    def decode(self, data: bytes) -> Model:
        """Doit décoder une trame complète en un objet Model."""
        raise NotImplementedError()

    def encode(self, data: Model) -> bytes:
        """Doit encoder un objet Model en une trame complète (bytes)."""
        raise NotImplementedError()
    