from core.model import Model

class InterfaceEncodage:
    
    def decode(self, data) -> Model:
        raise NotImplementedError()

    def encode(self, data: Model) -> bytes:
        raise NotImplementedError()
        
    def read_from_port(self, serial_port) -> Model:
        """Le protocole pioche dans le port série à sa manière"""
        raise NotImplementedError()