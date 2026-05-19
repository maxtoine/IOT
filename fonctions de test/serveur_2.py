import socketserver
import serial
import threading
import ctypes
import time
#socat -d -d PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0
# --- CONFIGURATION ---
HOST = "0.0.0.0"
UDP_PORT = 10000
MICRO_COMMANDS = ["TL", "LT"]
FILENAME = "values.txt"
SERIALPORT = "/dev/pts/3"  # Changer en /dev/ttyS2 pour Linux
BAUDRATE = 115200

# --- DÉFINITION DE LA STRUCTURE (C-Style) ---
class MaTrame(ctypes.LittleEndianStructure):
    _pack_ = 1  # Pas d'alignement d'octets (17 octets pile)
    _fields_ = [
        ("adresse", ctypes.c_ubyte),    # 1 octet
        ("tag",     ctypes.c_char * 3), # 3 octets
        ("f1",      ctypes.c_float),    # 4 octets
        ("f2",      ctypes.c_float),    # 4 octets
        ("f3",      ctypes.c_float),    # 4 octets
        ("fin",     ctypes.c_ubyte)     # 1 octet
    ]

# Variable globale pour stocker la dernière valeur lisible
LAST_VALUE = "No data yet"
TRAME_SIZE = ctypes.sizeof(MaTrame)

# --- SERVEUR UDP ---
class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # On décode la commande texte venant de l'app Android/UDP
        try:
            raw_data = self.request[0].strip()
            data = raw_data.decode('utf-8')
            socket = self.request[1]
            
            print(f"UDP Recu: {data} depuis {self.client_address}")

            if data in MICRO_COMMANDS:
                sendUARTMessage(data)
            elif data == "getValues()":
                # On renvoie la dernière chaîne de caractères construite
                socket.sendto(LAST_VALUE.encode('utf-8'), self.client_address)
            else:
                print(f"Commande inconnue: {data}")
        except Exception as e:
            print(f"Erreur handler UDP: {e}")

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

# --- GESTION SERIAL (UART) ---
ser = serial.Serial()

def initUART():        
    ser.port = SERIALPORT
    ser.baudrate = BAUDRATE
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout = 0.1 # Petit timeout pour ne pas bloquer le CPU
    
    print(f'Connexion série sur {SERIALPORT}...')
    try:
        ser.open()
    except serial.SerialException as e:
        print(f"Erreur: Port {SERIALPORT} non disponible. ({e})")
        exit()

def sendUARTMessage(msg):
    # Envoi texte simple vers le microcontrôleur
    ser.write(msg.encode('utf-8'))
    print(f"UART Envoyé: <{msg}>")

# --- LOGIQUE PRINCIPALE ---
if __name__ == '__main__':
    initUART()
    
    # Ouvrir le fichier en mode "Append"
    f = open(FILENAME, "a")
    print('Serveur prêt. Appuyez sur Ctrl-C pour quitter.')

    # Lancement du serveur UDP dans un thread séparé
    server = ThreadedUDPServer((HOST, UDP_PORT), ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    try:
        server_thread.start()
        print(f"Serveur UDP actif sur le port {UDP_PORT}")

        while ser.isOpen():
            # On vérifie si on a assez d'octets pour remplir une structure complète
            if ser.in_waiting >= TRAME_SIZE:
                # Lecture des octets bruts
                raw_bytes = ser.read(TRAME_SIZE)
                
                # --- MAGIE CTYPES : Octets -> Objet ---
                try:
                    trame = MaTrame.from_buffer_copy(raw_bytes)
                    
                    # Extraction des données
                    tag_str = trame.tag.decode('ascii', errors='ignore')
                    val_str = f"ID:{trame.adresse};TAG:{tag_str};F1:{trame.f1:.2f};F2:{trame.f2:.2f};F3:{trame.f3:.2f}"
                    
                    # Mise à jour de la variable globale pour le client UDP
                    LAST_VALUE = val_str
                    
                    # Affichage et sauvegarde
                    print(f"UART Recu (Objet): {val_str}")
                    f.write(val_str + "\n")
                    f.flush()
                except Exception as e:
                    print(f"Erreur de casting binaire: {e}")
            
            time.sleep(0.01) # Petit repos CPU

    except (KeyboardInterrupt, SystemExit):
        print("\nArrêt du serveur...")
        server.shutdown()
        server.server_close()
        f.close()
        ser.close()
        exit()