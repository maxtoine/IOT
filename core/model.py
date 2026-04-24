class Model():
    def __init__(self, address: str, formats: str, temperature: float, luminosity: float, humidity: float, pressure: float, uv: float, end: float):
        self.address = address
        self.formats = formats
        self.temperature = temperature
        self.luminosity = luminosity
        self.humidity = humidity
        self.pressure = pressure
        self.uv = uv
        self.end = end
           
                
    def __str__(self):
        return f"{self.address};{self.formats};{self.temperature};{self.luminosity};{self.humidity};{self.pressure};{self.uv};{self.end}"