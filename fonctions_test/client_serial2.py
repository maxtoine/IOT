import serial
import time
import random

# --- CONFIGURATION DU CLIENT ---
SERIALPORT = "/dev/pts/1" 
BAUDRATE = 115200

def run_client_independant():
    try:
        ser = serial.Serial(
            port=SERIALPORT,
            baudrate=BAUDRATE,
            timeout=1
        )
        print(f"✅ Client de test connecté sur {SERIALPORT}...")
    except serial.SerialException as e:
        print(f"❌ Erreur : Port {SERIALPORT} non disponible. ({e})")
        return

    print("Début de l'envoi des trames texte (Format: ID;TAG;F1;F2;F3;FIN).")
    print("Appuyez sur Ctrl+C pour arrêter.")

    try:
        while True:
            # 1. Génération des données factices
            adresse = "42"  # Doit être une chaîne de caractères pour le format texte
            tag = "SEN"
            f1 = round(random.uniform(10.0, 30.0), 2)
            f2 = round(random.uniform(50.0, 100.0), 2)
            f3 = round(random.uniform(-10.0, 10.0), 2)
            fin = "255.0"

            # 2. FORMATAGE MANUEL (Exactement comme le ferait un code C++ sur un micro:bit)
            # On construit la chaîne de caractères avec des points-virgules et un saut de ligne
            trame_texte = f"{adresse};{tag};{f1};{f2};{f3};{fin}\n"

            # 3. Encodage brut en octets (UTF-8) pour passer dans le câble
            trame_bytes = trame_texte.encode('utf-8')
            
            # 4. Envoi
            ser.write(trame_bytes)
            print(f"📤 Envoyé : {trame_texte.strip()}")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt du client...")
    finally:
        if ser.is_open:
            ser.close()

if __name__ == '__main__':
    run_client_independant()