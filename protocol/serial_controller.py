from core.model import Model


class SerialController:
    
    def __init__(self, storage, serial_adapter=None, serial_encodage=None, mon_adresse=0):
        self.storage = storage
        self.serial_adapter = serial_adapter
        self.serial_encodage = serial_encodage
        self.mon_adresse = mon_adresse
        self.ALLOWED_CHARS = set("TLHPU")


    def process_request(self, data_in : Model) -> dict:
        
        processed_data = data_in.formats
        
        if "":
            pass
        elif set(processed_data).issubset(self.ALLOWED_CHARS):
            self._format_save(data_in)
        else:
            print(f"Format non reconnu : {data_in.formats}")
    
    def _format_save(self, data_in : Model):
        self.storage.save_data(data_in)