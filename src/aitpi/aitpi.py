from aitpi.message import CleanUp
from aitpi.printer import Printer
from aitpi.postal_service import PostalService
from aitpi.command_registry import CommandRegistry
from aitpi.input_converter import InputConverter
from aitpi.postal_service import PostalService
from aitpi.message import *
from aitpi.printer import Printer
from aitpi.input_initializer import *


class Aitpi():
    def addRegistry(registryJson, folderedCommandsJson=None):
        CommandRegistry(registryJson, folderedCommandsJson)

    def initInput(inputJson):
        InputConverter.init(inputJson)

    def shutdown():
        PostalService.sendMessage(CleanUp())
        Printer.print("OFF")
