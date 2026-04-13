import serial
import ctypes
import time

# Utilise le 'r' pour le chemin
SERIALPORT = r"\\.\pipe\mavm" 

class MaTrame(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("adresse", ctypes.c_ubyte),
        ("tag",     ctypes.c_char * 3),
        ("f1",      ctypes.c_float),
        ("f2",      ctypes.c_float),
        ("f3",      ctypes.c_float),
        ("fin",     ctypes.c_ubyte)
    ]

def run_client():
    try:
        # --- ASTUCE ICI ---
        # On ouvre le port SANS configuration (rtscts, dsrdtr, etc.)
        ser = serial.Serial(SERIALPORT, baudrate=115200, rtscts=False, dsrdtr=False, do_not_open=True)
        # On force l'ouverture sans configurer les paramètres série
        ser.open() 
        
        print(f"Connecté au Pipe : {SERIALPORT}")

        compteur = 0.0
        while True:
            trame = MaTrame()
            trame.adresse = 1
            trame.tag = b"SIM"
            trame.f1 = compteur
            trame.f2 = 20.0
            trame.f3 = 30.0
            trame.fin = 0x04

            ser.write(bytes(trame))
            print(f"Envoyé : {trame.f1:.2f}")

            compteur += 0.1
            time.sleep(1)

    except Exception as e:
        print(f"Erreur : {e}")