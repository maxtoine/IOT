import serial


class SerialAdapter(serial.Serial):
    '''
    Classe Serial personnalisée pour gérer la connexion série et l'envoi de messages UART.
    Paramètres :
    - port : Le port série à utiliser (ex: "/dev/ttyS2")
    - baudrate : La vitesse de communication (ex: 115200)
    
    Méthodes :
    - sendUARTMessage(msg) : Envoie un message sur la connexion
    
    '''
    def __init__(self, port, baudrate, protocol):
        super().__init__()
        self._initUART(port, baudrate)
        self.protocol = protocol
        
    def _initUART(self, serialport, baudrate):
        '''
        Initialise la connexion série avec les paramètres spécifiés.
        
        Paramètres :
        - serialport (str) : Le port série à utiliser (ex: "/dev/ttyS2")
        - baudrate (int) : La vitesse de communication (ex: 115200)
        '''
               
        self.port = serialport
        self.baudrate = baudrate
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 0.1 # Petit timeout pour ne pas bloquer le CPU
        
        print(f'Connexion série sur {serialport}...')
        try:
            self.open()
            
        except serial.SerialException as e:
            print(f"Erreur: Port {serialport} non disponible. ({e})")
            exit()
    
    def sendUARTMessage(self, msg):
        ''' 
        Envoie un message sur la connexion série a faire l'encodage avants
        Paramètre : msg (str) - Le message à envoyer
        '''
        msg_bytes = self.protocol.encode(msg)
        self.write(msg_bytes)
        print("UART Envoyé: <{msg}>".format(msg=msg))
    
    def readUARTMessage(self):
        '''
        Laisse le protocole gérer sa propre lecture.
        '''
        try:         
            while self.isOpen(): 
                # MAGIE DE L'OOP : On donne "nous-même" (le port série) au protocole
                model = self.protocol.read_from_port(self)
                
                if model:
                    return model
                
        except (KeyboardInterrupt, SystemExit):
            print("\nArrêt de la connexion série...")
            self.close()
            exit()
            
        return None
    
    def closeConnection(self):
        '''
        Ferme la connexion série.
        '''
        print("Fermeture de la connexion série...")
        self.close()