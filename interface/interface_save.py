
class InterfaceSave():
    '''
    Interface pour la sauvegarde de données.
    
    Méthodes à implémenter :
     - saveData(data) : Sauvegarde les données fournies
     - loadData() : Charge et retourne les données sauvegardées
     - deleteData() : Supprime les données sauvegardées
     - dataExists() : Vérifie si des données sont déjà sauvegardées
    '''
    def saveData(self, data):
        '''
        Sauvegarde les données fournies.
        Paramètre : data (any) - Les données à sauvegarder
        '''
        raise NotImplementedError("La méthode saveData doit être implémentée.")
    
    def loadData(self):
        '''
        Charge et retourne les données sauvegardées.
        Retour : Les données chargées
        '''
        raise NotImplementedError("La méthode loadData doit être implémentée.")
    
    def deleteData(self):
        '''
        Supprime les données sauvegardées.
        '''
        raise NotImplementedError("La méthode deleteData doit être implémentée.")
    
    def dataExists(self):
        '''
        Vérifie si des données sont déjà sauvegardées.
        Retour : True si des données existent, False sinon
        '''
        raise NotImplementedError("La méthode dataExists doit être implémentée.")