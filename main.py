from core.server import ServerIot
from implementations.encodages import BinaryEncodage
from implementations.storages import SQLiteStorage
from adapter import SerialAdapter, UdpAdapter

# 1. On choisit le protocole et le stockage
encodage = BinaryEncodage() 
stockage = SQLiteStorage("values.db")
adresse="0.0.0.0"
port=10000

# 2. On configure l'adaptateur série en utilisant read_mode et length
adapter_serial = SerialAdapter(
    port="/dev/pts/1", 
    baudrate=115200, 
    length=encodage.framing_length
)

udp_adapter = UdpAdapter(adresse, port)

# 3. On injecte tout dans le serveur
serveur = ServerIot(
    adapter_serial=adapter_serial, 
    udp_adapter=udp_adapter, 
    encodage=encodage, 
    storage=stockage, 
)


# 4. C'est parti
serveur.start()