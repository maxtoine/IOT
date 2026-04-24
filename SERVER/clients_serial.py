import serial
import struct
import time
import random

# --- CONFIGURATION ---
SERIALPORT = "/dev/pts/3"
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
    adresse = 0        # 1 octet (0-255)
    tag = b"SEN"       # 3 octets
    fin = 255          # 1 octet (0-255)

    print("Début de l'envoi des trames. Appuyez sur Ctrl+C pour arrêter.")

    try:
        while True:
            # Génération de valeurs aléatoires simulant les capteurs
            temperature = random.uniform(10.0, 30.0)    # °C
            luminosity  = random.uniform(50.0, 100.0)   # %
            humidity    = random.uniform(-10.0, 10.0)   # %
            pressure    = random.uniform(950.0, 1050.0) # hPa
            uv          = random.uniform(0.0, 11.0)     # indice UV

            # --- PACKING BINAIRE ---
            # Format '<B3sfffffB' :
            # <  : Little-Endian
            # B  : unsigned char (1 octet)  -> adresse
            # 3s : char[3] (3 octets)       -> tag
            # f  : float (4 octets)         -> temperature
            # f  : float (4 octets)         -> luminosity
            # f  : float (4 octets)         -> humidity
            # f  : float (4 octets)         -> pressure
            # f  : float (4 octets)         -> uv
            # B  : unsigned char (1 octet)  -> fin
            # Total : 1 + 3 + 4*5 + 1 = 25 octets
            trame = struct.pack('<B3sfffffB', adresse, tag, temperature, luminosity, humidity, pressure, uv, fin)

            ser.write(trame)
            print(
                f"📤 Envoyé : ID:{adresse} | TAG:{tag.decode()} | "
                f"TEMP:{temperature:.2f} | LUM:{luminosity:.2f} | "
                f"HUM:{humidity:.2f} | PRES:{pressure:.2f} | UV:{uv:.2f}"
            )

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt du client...")
    finally:
        if ser.is_open:
            ser.close()

if __name__ == '__main__':
    run_client()