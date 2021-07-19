class Message():
    """Simplist message class
    """
    msgId = None
    def __init__(self, data):
        """Inits data

        Args:
            data (unknown): Just some data to send
        """
        self.data = data

class InputChangeRequest(Message):
    msgId = -1000
    def __init__(self, name, newVal) -> None:
        self.name = name
        self.newVal = newVal

class RegistryChangeRequest(Message):
    msgId = -1001
    def __init__(self, type, name, newVal) -> None:
        self.type = type
        self.name = name
        self.newVal = newVal

class CommandLibraryCommand(Message):
    """Sent to command library
    """
    msgId = -1002

class InputCommand(Message):
    """When a button is pressed
    """
    msgId = -1003

class FolderMessage(Message):
    """When a folder changes
    """
    msgId = -1004