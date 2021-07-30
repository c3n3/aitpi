from aitpi.message import CleanUp
from aitpi.printer import Printer
from aitpi.postal_service import PostalService

def initialize(inputJson, registryJson, folderedCommandsJson):
    pass

def shutdown():
    PostalService.sendMessage(CleanUp())
    Printer.print("OFF")
