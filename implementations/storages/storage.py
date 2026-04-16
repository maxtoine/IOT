import os
from interface.interface_save import InterfaceSave
from core.model import Model

class FileStorage(InterfaceSave):
    def __init__(self, filename: str):
        self.filename = filename
        # À l'initialisation, on s'assure juste que le fichier existe, 
        # sans le charger en mémoire !
        self._assurer_creation_fichier()

    def _assurer_creation_fichier(self):
        """Crée le fichier vide s'il n'existe pas encore."""
        with open(self.filename, 'a+', encoding='utf-8') as f:
            pass

    def search_data(self, query: str, separateur: str = ';'):
        liste_models = []
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for _, ligne in enumerate(f, 1):
                    # 1. On découpe la ligne TOUT DE SUITE
                    elements = ligne.strip().split(separateur)
                    
                    # 2. On vérifie qu'elle est complète
                    if len(elements) >= 6:
                        # 3. ON CIBLE LA RECHERCHE : On compare la colonne 0 (l'adresse) avec la query
                        # On utilise "==" au lieu de "in" pour une correspondance exacte (Ex: "42" == "42")
                        if elements[0].strip() == query:
                            
                            address = elements[0].strip()
                            formats = elements[1].strip().upper()
                            data_1 = float(elements[2].strip())
                            data_2 = float(elements[3].strip())
                            data_3 = float(elements[4].strip())
                            end = float(elements[5].strip())
                            
                            nouveau_model = Model(address, formats, data_1, data_2, data_3, end)
                            liste_models.append(nouveau_model)
                            
            return liste_models
        
        except Exception as e:
            print(f"Une erreur s'est produite lors de la recherche : {e}")
            return []
        
    def save_data(self, data: Model):
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(str(data) + '\n')

    def delete_data(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def data_exists(self):
        return os.path.exists(self.filename)
    
    def load_data(self):
        pass
       