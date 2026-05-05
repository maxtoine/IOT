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
        buffer_global = b""
        print(f"[Serial] Surveillance active sur l'adresse : {self.mon_adresse}")
        last_heartbeat = time.time()

        while True:
            try:
                if time.time() - last_heartbeat > 5:
                    print("[Système] Toujours en attente de données...")
                    last_heartbeat = time.time()


                raw_chunk = self.adapter_serial.read_raw()
                
                if raw_chunk:
                    buffer_global += raw_chunk
                    
                    trames_completes, buffer_global = self.serial_encodage.extract_frames(buffer_global)
                    
                    if trames_completes:
                        print(f"DEBUG: {len(trames_completes)} trame(s) extraite(s) !")
                    
                    for trame in trames_completes:
                        addr = self.serial_encodage.extract_address(trame)

                        if int(addr) == int(self.mon_adresse):
                            model = self.serial_encodage.decode(trame)
                            print(f"[+] Message décodé : {model}")
                            self.storage.save_data(model)
                        else:
                            print(f"[-] Adresse {addr} ignorée.")
                
                time.sleep(0.1)
            except Exception as e:
                print(f"ERREUR DANS LA BOUCLE : {e}")
                time.sleep(1)
                
    def stop(self):
        self.adapter_serial.close_connection()
        self.udp_adapter.stop()
        print("IoT Server stopped.")