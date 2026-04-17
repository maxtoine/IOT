from core.model import Model

class InterfaceSave:
    def search_data(self, query: str) -> list[Model]:
        raise NotImplementedError()
    
    def save_data(self, data: Model):
        raise NotImplementedError()
    
    def load_data(self):
        raise NotImplementedError()
    
    def delete_data(self):
        raise NotImplementedError()
    
    def data_exists(self) -> bool:
        raise NotImplementedError()