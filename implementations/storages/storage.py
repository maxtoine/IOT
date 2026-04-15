from interface.interface_save import InterfaceSave

class FileStorage(InterfaceSave):
    def __init__(self, filename: str):
        self.filename = filename

    def saveData(self, data):
        with open(self.filename, 'a') as f:
            f.write(str(data) + '\n')

    def loadData(self):
        try:
            with open(self.filename, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def deleteData(self):
        try:
            import os
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def dataExists(self):
        import os
        return os.path.exists(self.filename)