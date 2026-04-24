import struct

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
                    buffer_global += raw_chunk
                    
                    # extract_frames utilisera automatiquement la nouvelle taille de 25 octets
                    # si vous avez bien mis à jour MaTrame dans binary_encodage.py
                    trames_completes, buffer_global = self.encodage.extract_frames(buffer_global)
                    
                    for trame in trames_completes:
                        adresse_recue = self.encodage.extract_address(trame)
                        
                        if adresse_recue in (self.mon_adresse, "0"):
                            # --- MODIFICATION ICI : Format '<B3sfffffB' pour 5 floats ---
                            # B (1), 3s (3), f (4), f (4), f (4), f (4), f (4), B (1) = 25 octets
                            # Mettre à jour le unpack pour 5s (string de 5)
                            brut = struct.unpack('<B5sfffffB', trame)
                            tag_brut = brut[1].decode('utf-8')
                            
                            # On récupère les 5 valeurs brutes
                            f1_b, f2_b, f3_b, f4_b, f5_b = brut[2], brut[3], brut[4], brut[5], brut[6]
                                
                            
                            # Affichage brut avec les 5 capteurs (T, L, H, P, U)
                            print(f"\n[RADIO BRUT] {tag_brut} | T:{f1_b:.2f} L:{f2_b:.2f} H:{f3_b:.2f} P:{f4_b:.2f} U:{f5_b:.2f}")

                            # --- AFFICHAGE DU FORMAT DÉCODÉ (Utilise votre Model à 5 valeurs) ---
                            model = self.encodage.decode(trame)
                            print(f"[SERVEUR OK] {model}")
                            self.storage.save_data(model)
                        else:
                            print(f"[-] Ignoré (Adresse {adresse_recue} inconnue)")

            except KeyboardInterrupt:
                self.stop()
                break
                
    def stop(self):
        self.adapter.close_connection()