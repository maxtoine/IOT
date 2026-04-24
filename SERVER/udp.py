import socket
import json
import time

IP, PORT = "127.0.0.1", 10000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# On prépare une structure de données
data_to_send = {
    "method": "poll",
    "adress": "42"
}

# Conversion du dictionnaire en chaîne JSON, puis en octets
message_bytes = json.dumps(data_to_send).encode('utf-8')

print(f"[*] Envoi de l'objet JSON au serveur...")
sock.sendto(message_bytes, (IP, PORT))

while True:
    data, addr = sock.recvfrom(1024)
    try:
        # Décodage du JSON
        message_json = json.loads(data.decode('utf-8'))
        
        print(f"\n[+] Reçu de {addr}: message_json = {message_json}")
        
    except json.JSONDecodeError:
        print(f"[!] Erreur : Données reçues non valides (pas du JSON).")

sock.close()