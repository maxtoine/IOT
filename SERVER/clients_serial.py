import serial
import struct
import time
import random

# --- CONFIGURATION ---
# IMPORTANT : Si le serveur écoute sur /dev/pts/3, le client doit être sur le port lié (ex: /dev/pts/4).
# Voir l'astuce 'socat' ci-dessous pour créer ce lien virtuel.
SERIALPORT = "/dev/pts/4" 
BAUDRATE = 115200

def run_client():
    try:
        ser = serial.Serial(
            port=SERIALPORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        print(f"✅ Client série connecté sur {SERIALPORT}...")
    except serial.SerialException as e:
        print(f"❌ Erreur : Port {SERIALPORT} non disponible. ({e})")
        return

    # Paramètres fixes pour la simulation
    adresse = 42              # 1 octet (0-255)
    tag = b"SEN"              # 3 octets (doit être en bytes)
    fin = 255                 # 1 octet (0-255)

    print("Début de l'envoi des trames. Appuyez sur Ctrl+C pour arrêter.")

    try:
        while True:
            # Génération de valeurs flottantes aléatoires pour f1, f2, f3
            f1 = random.uniform(10.0, 30.0)
            f2 = random.uniform(50.0, 100.0)
            f3 = random.uniform(-10.0, 10.0)

            # --- PACKING BINAIRE ---
            # Explication du format '<B3sfffB' :
            # <  : Little-Endian (comme attendu par ton serveur)
            # B  : unsigned char (1 octet) -> adresse
            # 3s : char[3] (3 octets)      -> tag
            # f  : float (4 octets)        -> f1
            # f  : float (4 octets)        -> f2
            # f  : float (4 octets)        -> f3
            # B  : unsigned char (1 octet) -> fin
            # Total : 1 + 3 + 4 + 4 + 4 + 1 = 17 octets (Pile la taille de ta MaTrame !)
            
            trame = struct.pack('<B3sfffB', adresse, tag, f1, f2, f3, fin)
            
            # Envoi sur le port série
            ser.write(trame)
            
            print(f"📤 Envoyé : ID:{adresse} | TAG:{tag.decode()} | F1:{f1:.2f} | F2:{f2:.2f} | F3:{f3:.2f}")
            
            # Pause avant le prochain envoi
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt du client...")
    finally:
        if ser.is_open:
            ser.close()

if __name__ == '__main__':
    run_client()