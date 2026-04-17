class Model():
    def __init__(self, address: str, formats: str, value_a: float, value_b: float, value_c: float, end: float):
        self.address = address
        self.formats = formats
        self.value_a = value_a  # Température
        self.value_b = value_b   # Luminosité
        self.value_c = value_c   # Humidité
        self.end = end
           
                
    def __str__(self):
        return f"{self.address};{self.formats};{self.value_a};{self.value_b};{self.value_c};{self.end}"