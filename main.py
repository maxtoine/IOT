#!/usr/bin/env python3

from core.server import ServerIot
from config import ServerConfig
from implementations.storages.storage import FileStorage

if __name__ == "__main__":
    
     # Exemple d'utilisation
    storage = FileStorage('values.txt')
        
    # Rechercher des données
    resultats = storage.search_data('42')
    for res in resultats:
        print(res)
        
    config = ServerConfig.from_env()
    server = ServerIot(config)
    server.start()