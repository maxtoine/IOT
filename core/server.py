from interface.interface_save import InterfaceSave
from interface.interface_encodage import InterfaceEncodage
from protocol import UdpController

import time

class ServerIot:
   
    def __init__(self, adapter_serial, udp_adapter, serial_encodage, storage, adresse=0):
        
        self.adapter_serial = adapter_serial
        self.udp_adapter = udp_adapter
        self.serial_encodage = serial_encodage
        self.storage = storage
        self.mon_adresse = adresse

        # Le Cerveau UDP (qui a besoin du stockage et de l'accès matériel)
        self.udp_controller = UdpController(
            storage=self.storage, 
            serial_adapter=self.adapter_serial,
            serial_encodage=self.serial_encodage,
            mon_adresse=self.mon_adresse
        )
        
        self.udp_adapter.set_logic_callback(self.udp_controller.process_request)

    def start(self):
        print("Starting IoT Server...")
        self.udp_adapter.start()
        self.run_serial_loop()
    
    def run_serial_loop(self):
        buffer_global = b""  # Notre mémoire tampon
        print("[Serial] Starting Serial Loop...")
        while True:
            try:
                raw_chunk = self.adapter_serial.read_raw()
                
                if raw_chunk:
                    buffer_global += raw_chunk  # On ajoute les nouveaux morceaux au tampon
                    
                    # On demande à l'encodage d'extraire TOUTES les trames complètes
                    # et de nous rendre ce qui n'est pas encore complet (le reste du buffer)
                    trames_completes, buffer_global = self.serial_encodage.extract_frames(buffer_global)
                    
                    for trame in trames_completes:
                        adresse_recue = self.serial_encodage.extract_address(trame)
                        
                        if adresse_recue == self.mon_adresse:
                            model = self.serial_encodage.decode(trame)
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