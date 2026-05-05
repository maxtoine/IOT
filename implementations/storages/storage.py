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

    def search_data(self, query, separateur: str = ';') -> list[Model]:
        liste_models = []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for ligne in f:
                    elements = ligne.strip().split(separateur)
                    # On vérifie qu'on a bien les 8 colonnes (ID;TAG;T;L;H;P;U;FIN)
                    if len(elements) >= 8 and elements[0].strip() == query:
                        model = Model(
                            address=elements[0],
                            formats=elements[1].upper(),
                            temperature=float(elements[2]),
                            luminosity=float(elements[3]),
                            humidity=float(elements[4]),
                            pressure=float(elements[5]),
                            uv=float(elements[6]),
                            end=int(elements[7])
                        )
                        liste_models.append(model)
            return liste_models
        except Exception as e:
            print(f"Erreur de recherche dans storage : {e}")
            return []
        
    def save_data(self, data: Model):
        # Utilise la méthode __str__ du Model qui génère déjà les 8 colonnes
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
        pass