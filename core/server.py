from interface.interface_save import InterfaceSave
from interface.interface_encodage import InterfaceEncodage

import time

class ServerIot:
   
    def __init__(self, adapter_serial, udp_adapter, encodage, storage):
        
        self.adapter_serial = adapter_serial
        self.udp_adapter = udp_adapter
        self.encodage = encodage
        self.storage = storage
        self._last_model = None
        self.mon_adresse = 42 
        self.udp_adapter.set_logic_callback(self.process_udp_logic) 

    
    
    def start(self):
        print("Starting IoT Server...")
        self.udp_adapter.start()
        self.run_serial_loop()
    
    def process_udp_logic(self, data: dict) -> dict:
        """
        Le cerveau reçoit un DICTIONNAIRE et doit renvoyer un DICTIONNAIRE.
        Il ne sait pas que ça vient d'un JSON !
        """
        print(f"[Logique IOT] Reçu : {data}")

        # On extrait la commande (par exemple, si le client Android envoie {"commande": "getValues"})
        commande = data.get("method")

        match commande:
            case "poll":
                list_data = self.storage.search_data(data.get("adress"))
                data_last = list_data[0]
                json = {
                    "status": "success",
                    "adress": data_last.address,
                    "formats": data_last.formats,
                    "temperature": data_last.temperature,
                    "humidity": data_last.humidity,
                    "luminosity": data_last.luminosity,
                    "pressure" : data_last.pressure,
                    "uv" : data_last.uv,
                }      
                return json
            
            case _:
                return {"status": "error", "message": "Commande inconnue"}

        
    def run_serial_loop(self):
        buffer_global = b""  # Notre mémoire tampon

        while True:
            try:
                raw_chunk = self.adapter_serial.read_raw()
                
                if raw_chunk:
                    buffer_global += raw_chunk  # On ajoute les nouveaux morceaux au tampon
                    
                    # On demande à l'encodage d'extraire TOUTES les trames complètes
                    # et de nous rendre ce qui n'est pas encore complet (le reste du buffer)
                    trames_completes, buffer_global = self.encodage.extract_frames(buffer_global)
                    
                    for trame in trames_completes:
                        adresse_recue = self.encodage.extract_address(trame)
                        
                        if adresse_recue == self.mon_adresse:
                            model = self.encodage.decode(trame)
                            print(f"[+] Message décodé : {model}")
                            self.storage.save_data(model)
            
            time.sleep(0.1)

            except KeyboardInterrupt:
                self.stop()
                break
                
    def stop(self):
        self.adapter_serial.close_connection()
        self.udp_adapter.stop()
        print("IoT Server stopped.")