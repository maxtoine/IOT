from core.model import Model

class InterfaceSave():
    '''
    Interface pour la sauvegarde de données.
    
    Méthodes à implémenter :
     - saveData(data) : Sauvegarde les données fournies
     - loadData() : Charge et retourne les données sauvegardées
     - deleteData() : Supprime les données sauvegardées
     - dataExists() : Vérifie si des données sont déjà sauvegardées
    '''
    def shearch_data(self, query) -> list[Model]:
        '''
        Recherche des données correspondant à la requête fournie.
        Paramètre : query (any) - La requête de recherche
        Retour : Les données correspondant à la requête
        '''
        raise NotImplementedError("La méthode shearch_data doit être implémentée.")
    
    def save_data(self, data: Model):
        '''
        Sauvegarde les données fournies.
        Paramètre : data (Model) - Les données à sauvegarder
        '''
        raise NotImplementedError("La méthode save_data doit être implémentée.")
    
    def load_data(self):
        '''
        Charge et retourne les données sauvegardées.
        Retour : Les données chargées
        '''
        raise NotImplementedError("La méthode load_data doit être implémentée.")
    
    def delete_data(self):
        '''
        Supprime les données sauvegardées.
        '''
        raise NotImplementedError("La méthode delete_data doit être implémentée.")
    
    def data_exists(self):
        '''
        Vérifie si des données sont déjà sauvegardées.
        Retour : True si des données existent, False sinon
        '''
        raise NotImplementedError("La méthode data_exists doit être implémentée.")