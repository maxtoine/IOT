import serial
import struct
import time
import random

# --- CONFIGURATION ---
SERIALPORT = "/dev/pts/2"
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

    # --- PARAMÈTRES DE LA TRAME ---
    adresse = 42         # 1 octet (B)
    # Le tag DOIT faire 5 octets pour correspondre au (ctypes.c_char * 5) du serveur
    # On utilise "TLHPU" comme dans tes commentaires
    tag = b"TLHPU"       # 5 octets (5s)
    fin = 255            # 1 octet (B)

    print("Début de l'envoi des trames (Format 27 octets).")

    try:
        while True:
            # Génération de valeurs
            temperature = random.uniform(10.0, 30.0)
            luminosity  = random.uniform(50.0, 100.0)
            humidity    = random.uniform(-10.0, 10.0)
            pressure    = random.uniform(950.0, 1050.0)
            uv          = random.uniform(0.0, 11.0)

            # --- PACKING BINAIRE CORRIGÉ ---
            # Format '<B5sfffffB' :
            # <  : Little-Endian
            # B  : unsigned char (1 oct.) -> adresse
            # 5s : char[5] (5 oct.)       -> tag (Indispensable pour l'alignement)
            # f  : float (4 oct.)         -> f1 (Temp)
            # f  : float (4 oct.)         -> f2 (Lum)
            # f  : float (4 oct.)         -> f3 (Hum)
            # f  : float (4 oct.)         -> f4 (Pres)
            # f  : float (4 oct.)         -> f5 (UV)
            # B  : unsigned char (1 oct.) -> fin
            # TOTAL : 1 + 5 + (4*5) + 1 = 27 octets
            
            trame = struct.pack('<B5sfffffB', 
                                adresse, 
                                tag, 
                                temperature, 
                                luminosity, 
                                humidity, 
                                pressure, 
                                uv, 
                                fin)

            ser.write(trame)
            
            print(f"📤 Envoyé ({len(trame)} octets) : ID:{adresse} | TAG:{tag.decode()} | T:{temperature:.2f}°")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt du client...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == '__main__':
    run_client()