from aitpi.message import CleanUp
from aitpi.printer import Printer
from aitpi.postal_service import PostalService
from aitpi.command_registry import CommandRegistry
from aitpi.input_converter import InputConverter
from aitpi.postal_service import PostalService
from aitpi.message import *
from aitpi.printer import Printer
from aitpi.input_initializer import *




class Watcher():
    def consume(self, message):
        Printer.print(" Watcher: %s %s" % (message.data, message.event))

class PrintCommandRegistry():
    def consume(self, message):
        for T in CommandRegistry._commands.keys():
            for command in CommandRegistry._commands[T]:
                print("/", T, "/", command)

def initialize(inputJson, registryJson, folderedCommandsJson):
    CommandRegistry.init(registryJson, folderedCommandsJson)
    InputConverter.init(inputJson)

def shutdown():
    PostalService.sendMessage(CleanUp())
    Printer.print("OFF")
