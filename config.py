from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerConfig:
    serial_port: str = "/dev/pts/3"
    baudrate: int = 115200
    storage_path: str = "values.txt"
    
    
    @classmethod
    def from_env(cls):
        import os
        return cls(
            serial_port=os.getenv('SERIAL_PORT', cls.serial_port),
            baudrate=int(os.getenv('BAUDRATE', cls.baudrate)),
            storage_path=os.getenv('STORAGE_PATH', cls.storage_path),
        )