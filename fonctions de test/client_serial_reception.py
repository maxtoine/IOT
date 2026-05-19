import serial
import struct
import time
import random
import threading

# --- CONFIGURATION ---
SERIALPORT = "/dev/pts/2"
BAUDRATE = 115200

# Le format de base utilisé pour envoyer ET recevoir :
# 1 octet (dest) + 1 octet (src) + 5 octets (tag) + 5 * 4 octets (floats) + 1 octet (fin) = 28 octets
FORMAT_TRAME = '<BB5sfffffB'
TAILLE_TRAME = struct.calcsize(FORMAT_TRAME) 

def ecoute_serie(ser: serial.Serial):
    """
    Fonction qui tourne en arrière-plan pour écouter les ordres du serveur.
    """
    print(f"[Écoute] Démarrage du thread de réception (Taille attendue: {TAILLE_TRAME} octets)...")
    buffer = b""
    
    while ser.is_open:
        try:
            # On lit tout ce qui est disponible
            if ser.in_waiting > 0:
                buffer += ser.read(ser.in_waiting)
                
            # Tant qu'on a au moins la taille d'une trame complète (28 octets)
            while len(buffer) >= TAILLE_TRAME:
                # On extrait la première trame
                trame = buffer[:TAILLE_TRAME]
                buffer = buffer[TAILLE_TRAME:] # On garde le reste
                
                # Décodage de la trame reçue
                try:
                    donnees_decodables = struct.unpack(FORMAT_TRAME, trame)
                    addr_dest = donnees_decodables[0]
                    addr_src = donnees_decodables[1]
                    tag = donnees_decodables[2].decode('utf-8').strip('\x00') # On enlève les octets nuls potentiels
                    val1 = donnees_decodables[3]
                    
                    print(f"\n[📥 RÉCEPTION MATÉRIELLE] Ordre reçu ! ")
                    print(f"  > Dest: {addr_dest} | Src: {addr_src} | Tag: '{tag}' | Val1: {val1:.2f}")
                    
                    # C'est ici que tu peux ajouter un comportement !
                    if tag == "CMD  ":
                        if val1 == 1.0:
                            print("  > ACTION : Allumer la LED ! 💡")
                        elif val1 == 0.0:
                            print("  > ACTION : Éteindre la LED ! 🌑")
                            
                except struct.error:
                    print("[!] Erreur de décodage de la trame reçue.")

            time.sleep(0.05) # Petite pause pour le processeur
            
        except Exception as e:
            if ser.is_open:
                print(f"[Erreur Écoute] {e}")
                time.sleep(1)

def run_client():
    try:
        ser = serial.Serial(
            port=SERIALPORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )
        print(f"✅ Client série connecté sur {SERIALPORT}...")
    except serial.SerialException as e:
        print(f"❌ Erreur : Port {SERIALPORT} non disponible. ({e})")
        return

    # --- LANCEMENT DU THREAD D'ÉCOUTE ---
    thread_ecoute = threading.Thread(target=ecoute_serie, args=(ser,), daemon=True)
    thread_ecoute.start()

    # --- PARAMÈTRES DE LA TRAME ---
    address_destination = 0
    adresse = 42
    tag = b"TLHPU" 
    fin = 255 

    print("Début de l'envoi des trames (Format 28 octets).")

    try:
        while True:
          pass

    except KeyboardInterrupt:
        print("\nArrêt du client...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Port série fermé.")

if __name__ == '__main__':
    run_client()