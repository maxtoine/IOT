class Model():
    def __init__(self, adresse_dest, address, formats, temperature=0.0, luminosity=0.0, humidity=0.0, pressure=0.0, uv=0.0, end=255):
        self.adresse_dest = adresse_dest
        self.address = address
        self.formats = formats
        self.temperature = temperature
        self.luminosity = luminosity
        self.humidity = humidity
        self.pressure = pressure
        self.uv = uv
        self.end = end
           
    def __str__(self):
        # On aligne l'affichage sur les 8 colonnes pour le stockage
        # Format : ID;TAG;TEMP;LUM;HUM;PRES;UV;FIN
        return (f"{self.adresse_dest};{self.address};{self.formats};"
                f"{self.temperature:.2f};{self.luminosity:.2f};"
                f"{self.humidity:.2f};{self.pressure:.2f};"
                f"{self.uv:.2f};{self.end}")