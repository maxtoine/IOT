# Module pour la communication série (UART/USB)
import serial

class SerialAdapter:
    """
    Adaptateur pour la communication série avec le micro:bit ou la passerelle.
    Gère l'ouverture, la lecture et l'écriture sur le port série.
    """
    def __init__(self, port: str, baudrate: int):
        """
        Initialise l'adaptateur série.
        
        Args:
            port : Port série à utiliser (ex: "COM3" sur Windows, "/dev/ttyUSB0" sur Linux)
            baudrate : Vitesse de transmission en bauds (ex: 115200)
        """
        # Port série à utiliser
        self.port = port
        # Vitesse de transmission en bauds (bits par seconde)
        self.baudrate = baudrate
        # Objet de la connexion série
        self._serial = serial.Serial()
        # Initialise les paramètres et ouvre la connexion
        self._init_uart()
        
    def _init_uart(self):
        """Configure les paramètres UART et ouvre la connexion série."""
        # Assigne le port à la connexion
        self._serial.port = self.port
        # Assigne la vitesse de transmission
        self._serial.baudrate = self.baudrate
        # Configure la taille des données : 8 bits (standard)
        self._serial.bytesize = serial.EIGHTBITS
        # Configure la parité : aucune (pas de vérification supplémentaire)
        self._serial.parity = serial.PARITY_NONE
        # Configure les bits de stop : 1 bit (standard)
        self._serial.stopbits = serial.STOPBITS_ONE
        # Configure le timeout de lecture : 0.1 secondes (non-bloquant)
        self._serial.timeout = 0.1 
        
        print(f"Connexion série sur {self.port} à {self.baudrate} bauds...")
        try:
            # Ouvre la connexion série
            self._serial.open()
        except serial.SerialException as e:
            # Gère l'erreur si le port n'existe pas ou est déjà utilisé
            print(f"Erreur: Port {self.port} non disponible. ({e})")
            exit()
    
    def read_raw(self) -> bytes:
        """
        Lit toutes les données disponibles dans le buffer série.
        Retourne les octets bruts sans filtrage.
        """
        # Vérifie que la connexion est ouverte
        if not self._serial.is_open:
            return None

        # Récupère le nombre d'octets disponibles à la lecture
        in_waiting = self._serial.in_waiting
        if in_waiting > 0:
            # Lit tous les octets disponibles à la fois
            return self._serial.read(in_waiting) # On aspire TOUT ce qui est prêt
            
        # Aucune donnée disponible
        return None
                    
    def send_raw(self, data: bytes):
        """Envoie des octets bruts sur le port série."""
        # Vérifie que la connexion est ouverte avant d'envoyer
        if self._serial.is_open:
            # Écrit les octets sur le port série
            self._serial.write(data)
    
    def close_connection(self):
        """Ferme la connexion série proprement."""
        print("Fermeture de la connexion série...")
        # Vérifie que la connexion est encore ouverte
        if self._serial.is_open:
            # Ferme la connexion série
            self._serial.close()