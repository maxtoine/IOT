from core.server import ServerIot
from implementations.encodages import BinaryEncodage
from implementations.storages import SQLiteStorage
from adapter import SerialAdapter

# 1. On choisit le protocole et le stockage
encodage = BinaryEncodage() 
stockage = SQLiteStorage("values.db")

# 2. On configure l'adaptateur série en utilisant read_mode et length
adapter = SerialAdapter(
    port="/dev/pts/4", 
    baudrate=115200, 
    length=encodage.framing_length
)

# 3. On injecte tout dans le serveur
serveur = ServerIot(
    adapter=adapter, 
    encodage=encodage, 
    storage=stockage, 
    mon_adresse="0"
)


# 4. C'est parti
serveur.start()