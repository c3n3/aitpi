from aitpi.message import CleanUp
from aitpi.printer import Printer
from aitpi.postal_service import PostalService
from aitpi.command_library import CommandLibrary
from aitpi.input_converter import InputConverter
from aitpi.postal_service import PostalService
from aitpi.message import *
from aitpi.printer import Printer
from aitpi.input_initializer import *




class Watcher():
    def consume(self, message):
        Printer.print(" Watcher: %s %s" % (message.data, message.event))

class PrintCommandLibrary():
    def consume(self, message):
        for T in CommandLibrary._commands.keys():
            for command in CommandLibrary._commands[T]:
                print("/", T, "/", command)

def initialize(inputJson, registryJson, folderedCommandsJson):
    CommandLibrary.init(registryJson, folderedCommandsJson)
    InputConverter.init(inputJson)

def shutdown():
    PostalService.sendMessage(CleanUp())
    Printer.print("OFF")
