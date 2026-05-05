from core.server import ServerIot
from implementations.encodages import BinaryEncodage, JsonEncodage
from implementations.storages import SQLiteStorage
from adapter import SerialAdapter, UdpAdapter
from implementations.storages.storage import FileStorage

# 1. On choisit le protocole et le stockage
serial_encodage = BinaryEncodage() 
json_encodage = JsonEncodage()
#stockage = SQLiteStorage("values.db")
stockage = FileStorage("values.txt")

# 2. On configure l'adaptateur série en utilisant read_mode et length
adapter_serial = SerialAdapter(
    port="COM6", 
    baudrate=115200, 
    #length=serial_encodage.framing_length
    length=1
)

udp_adapter = UdpAdapter(
    "0.0.0.0", 
    10000, 
    encodage=json_encodage)

# 3. On injecte tout dans le serveur
serveur = ServerIot(
    adapter_serial=adapter_serial, 
    udp_adapter=udp_adapter, 
    serial_encodage=serial_encodage, 
    storage=stockage, 
    adresse=42
)


# 4. C'est parti
serveur.start()