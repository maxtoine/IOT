import os
from interface.interface_save import InterfaceSave
from core.model import Model

class FileStorage(InterfaceSave):
    def __init__(self, filename: str):
        self.filename = filename
        self._assurer_creation_fichier()

    def _assurer_creation_fichier(self):
        with open(self.filename, 'a+', encoding='utf-8') as f:
            pass

    def search_data(self, query: str, separateur: str = ';') -> list[Model]:
        liste_models = []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for ligne in f:
                    elements = ligne.strip().split(separateur)
                    if len(elements) >= 6 and elements[0].strip() == query:
                        model = Model(
                            address=elements[0],
                            formats=elements[1].upper(),
                            value_a=float(elements[2]),  # Au lieu de temperature
                            value_b=float(elements[3]),  # Au lieu de luminosity
                            value_c=float(elements[4]),  # Au lieu de humidity
                            end=float(elements[5])
                        )
                        liste_models.append(model)
            return liste_models
        except Exception as e:
            print(f"Erreur de recherche : {e}")
            return []
        
    def save_data(self, data: Model):
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(str(data) + '\n')

    def delete_data(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def data_exists(self) -> bool:
        return os.path.exists(self.filename)
        
    def load_data(self):
        pass # À implémenter selon tes besoins