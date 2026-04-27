from core.model import Model


class SerialController:
    
    def __init__(self, storage, serial_adapter=None, serial_encodage=None, mon_adresse=0):
        self.storage = storage
        self.serial_adapter = serial_adapter
        self.serial_encodage = serial_encodage
        self.mon_adresse = mon_adresse

    def process_request(self, data_in: bytes):
        pass