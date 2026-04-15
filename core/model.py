
class Model():
    def __init__(self, adress: str, formats: str, data_1: float, data_2: float, data_3: float, end: float):
        self.adress = adress
        self.formats = formats
        self.data_1 = data_1
        self.data_2 = data_2
        self.data_3 = data_3
        self.end = end
        
    def __str__(self):
        return f"{self.adress} (format {self.formats}) - {self.data_1}, {self.data_2}, {self.data_3} - End: {self.end}"