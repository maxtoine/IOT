from core.model import Model

class InterfaceEncodage:
    # Indique à l'adaptateur comment découper les trames ("line" ou "fixed")
    framing_mode: str 
    framing_length: int = 0 
    
    def extract_frames(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        """Doit retourner une liste de trames complètes extraites du buffer, et le reste du buffer qui n'est pas encore complet."""
        raise NotImplementedError()

    def _extract_frames_impl(self, buffer: bytes) -> tuple[list[bytes], bytes]:
        """Implémentation spécifique de l'extraction des trames, à fournir dans les classes filles."""
        raise NotImplementedError()
    
    def decode(self, data: bytes) -> Model:
        """Doit décoder une trame complète en un objet Model."""
        raise NotImplementedError()

    def encode(self, data: Model) -> bytes:
        """Doit encoder un objet Model en une trame complète (bytes)."""
        raise NotImplementedError()
    
    def extract_address(self, data: bytes) -> str:
        """Lit uniquement l'adresse sans décoder le reste."""
        raise NotImplementedError()