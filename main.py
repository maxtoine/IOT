from core.server import ServerIot
from implementations.encodages import BinaryEncodage # ou TextEncodage()
from implementations.storages import FileStorage
from adapter import SerialAdapter

# 1. On choisit le protocole et le stockage
encodage = BinaryEncodage() 
stockage = FileStorage("values.txt")

# 2. On configure l'adaptateur série en utilisant read_mode et length !
adapter = SerialAdapter(
    port="/dev/pts/0", 
    baudrate=115200, 
    read_mode=encodage.framing_mode,  # <-- Corrigé ici (read_mode au lieu de framing_mode)
    length=encodage.framing_length    # <-- Corrigé ici (length au lieu de framing_length)
)

# 3. On injecte tout dans le serveur
serveur = ServerIot(
    adapter=adapter, 
    encodage=encodage, 
    storage=stockage, 
    mon_adresse="42"
)


# 4. C'est parti
serveur.start()