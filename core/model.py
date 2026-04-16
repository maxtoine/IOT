class Model():
    def __init__(self, address: str, formats: str, value_a: float, value_b: float, value_c: float, end: float):
        self.address = address  # Corrigé 'adress' en 'address'
        self.formats = formats
        self.end = end
        
        # The class itself sorts the data upon creation!
        # We standardize the attributes: temperature, luminosity, humidity
        match formats:
            case 'TLH':
                self.temperature = value_a  # Temp
                self.luminosity = value_b   # Lum
                self.humidity = value_c     # Hum
            case 'LTH':
                self.temperature = value_b  # Temp is in 2nd position
                self.luminosity = value_a   # Lum is in 1st position
                self.humidity = value_c     # Hum
            case _:
                print(f"⚠️ Format inconnu : {formats}. Les valeurs seront assignées par défaut.")
                self.temperature = value_a  # Temp
                self.luminosity = value_b   # Lum
                self.humidity = value_c     # Hum
          
                
    def __str__(self):
        return f"{self.address};{self.formats};{self.temperature};{self.luminosity};{self.humidity};{self.end}"