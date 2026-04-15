from core.model import Model

class InterfaceProtocol:
    
    def __init__(self):
        pass

    def decode(self, data) -> Model:
        raise NotImplementedError("decode method must be implemented by subclasses")

    def encode(self, data: Model) -> bytes:
        raise NotImplementedError("encode method must be implemented by subclasses")
    
    def size(self) -> int:
        raise NotImplementedError("size method must be implemented by subclasses")