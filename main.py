#!/usr/bin/env python3

from core.server import ServerIot
from config import ServerConfig

if __name__ == "__main__":
    config = ServerConfig.from_env()
    server = ServerIot(config)
    server.start()