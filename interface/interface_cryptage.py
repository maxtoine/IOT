
class InterfaceCryptage:
    # Indique à l'adaptateur comment découper les trames ("line" ou "fixed")
    
    def decryptage(self, data: bytes) -> bytes:
        """Doit décoder une trame complète en un objet Model."""
        raise NotImplementedError()

    def encryptage(self, data: bytes) -> bytes:
        """Doit encoder un objet Model en une trame complète (bytes)."""
        raise NotImplementedError()
    