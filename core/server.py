from interface.interface_save import InterfaceSave
from interface.interface_encodage import InterfaceEncodage
from adapter import SerialAdapter

class ServerIot:
    def __init__(self, adapter, encodage, storage, mon_adresse: str):
        self.adapter = adapter
        self.encodage = encodage
        self.storage = storage
        self.mon_adresse = str(mon_adresse)
       
    def start(self):
        print("Starting IoT Server...")
        self.run_serial_loop()
        
    def run_serial_loop(self):
        buffer_global = b""  # Notre mémoire tampon
        
        while True:
            try:
                raw_chunk = self.adapter.read_raw()
                
                if raw_chunk:
                    buffer_global += raw_chunk  # On ajoute les nouveaux morceaux au tampon
                    
                    # On demande à l'encodage d'extraire TOUTES les trames complètes
                    # et de nous rendre ce qui n'est pas encore complet (le reste du buffer)
                    trames_completes, buffer_global = self.encodage.extract_frames(buffer_global)
                    
                    for trame in trames_completes:
                        adresse_recue = self.encodage.extract_address(trame)
                        
                        if adresse_recue == self.mon_adresse or adresse_recue == "00":
                            model = self.encodage.decode(trame)
                            print(f"[+] Message décodé : {model}")
                            self.storage.save_data(model)
                        else:
                            print(f"[-] Ignoré (Adresse {adresse_recue} inconnue)")

            except KeyboardInterrupt:
                self.stop()
                break
                
    def stop(self):
        self.adapter.close_connection()