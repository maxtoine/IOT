from adapter import SerialAdapter
from adapter.udp import UDPAdapter
from implementations.protocols import BinaryProtocol
from implementations.storages.storage import FileStorage
from config import ServerConfig

class ServerIot:
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.protocol_binary = BinaryProtocol()
        self.storage = FileStorage(config.storage_path)
        self.serial_adapter = SerialAdapter(
            port=config.serial_port,
            baudrate=config.baudrate,
            protocol=self.protocol_binary,
        )
       
        
    def start(self):
        print("Starting IoT Server...")
        self.run_serial_loop()
        
    def run_serial_loop(self):
        while True:
            try:
                model = self.serial_adapter.readUARTMessage()
                if model:
                    print(f"Received serial message: {model}")
                    self.storage.saveData(model)
            except KeyboardInterrupt:
                print("Stopping server...")
                self.stop()
                break
                

    def stop(self):
        self.serial_adapter.closeConnection()
        self.udp_adapter.stop_server()
