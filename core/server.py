from adapter import SerialAdapter
from adapter.udp import UDPAdapter
from implementations.protocols.protocols import BinaryProtocol, TextProtocol
from implementations.storages.storage import FileStorage
from config import ServerConfig

class ServerIot:
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.protocol_binary = BinaryProtocol()
        self.protocol_text = TextProtocol()
        self.storage = FileStorage(config.storage_path)
        self.serial_adapter = SerialAdapter(
            port=config.serial_port,
            baudrate=config.baudrate,
            protocol=self.protocol_binary
        )
        self.udp_adapter = UDPAdapter(
            host=config.udp_host,
            port=config.udp_port,
            protocol=self.protocol_text,
            on_message=self.handle_udp_message,
        )
        
    def start(self):
        print("Starting IoT Server...")
        self.udp_adapter.start_server()
        self.run_serial_loop()
        
    def run_serial_loop(self):
        while True:
            try:
                model = self.serial_adapter.readUARTMessage(None)
                if model:
                    print(f"Received serial message: {model}")
                    self.storage.saveData(model)
            except KeyboardInterrupt:
                print("Stopping server...")
                self.stop()
                break
                
    def handle_udp_message(self, model, client_address):
        print(f"Received UDP text message from {client_address}: {model}")
        self.storage.saveData(model)

    def stop(self):
        self.serial_adapter.closeConnection()
        self.udp_adapter.stop_server()
