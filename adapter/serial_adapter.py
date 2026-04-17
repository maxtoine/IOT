import serial

class SerialAdapter:
    def __init__(self, port: str, baudrate: int, read_mode: str = "line", length: int = 0):
        self.port = port
        self.baudrate = baudrate
        self.read_mode = read_mode
        self.length = length
        self._serial = serial.Serial()
        self._init_uart()
        
    def _init_uart(self):
        self._serial.port = self.port
        self._serial.baudrate = self.baudrate
        self._serial.bytesize = serial.EIGHTBITS
        self._serial.parity = serial.PARITY_NONE
        self._serial.stopbits = serial.STOPBITS_ONE
        self._serial.timeout = 0.1 
        
        print(f"Connexion série sur {self.port} à {self.baudrate} bauds...")
        try:
            self._serial.open()
        except serial.SerialException as e:
            print(f"Erreur: Port {self.port} non disponible. ({e})")
            exit()
    
    def read_raw(self) -> bytes:
        """Lit toutes les données disponibles dans le port série, sans filtre."""
        if not self._serial.is_open:
            return None

        in_waiting = self._serial.in_waiting
        if in_waiting > 0:
            return self._serial.read(in_waiting) # On aspire TOUT ce qui est prêt
            
        return None
                    
        
    def send_raw(self, data: bytes):
        if self._serial.is_open:
            self._serial.write(data)
    
    def close_connection(self):
        print("Fermeture de la connexion série...")
        if self._serial.is_open:
            self._serial.close()