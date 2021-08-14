from aitpi.message import CleanUp
from aitpi.printer import Printer
from aitpi.postal_service import PostalService
from aitpi.command_registry import CommandRegistry
from aitpi.input_converter import InputConverter
from aitpi.postal_service import PostalService
from aitpi.message import *
from aitpi.printer import Printer
from aitpi.input_initializer import TerminalKeyInput
from aitpi.input_initializer import *

_initRegistry = False

def addRegistry(registryJson, folderedCommandsJson=None):
    """ Adds a new command registry to Aitpi

    Args:
        registryJson (string): path to a json file
        folderedCommandsJson (string, optional): path to a json file, defaults to None
    """
    CommandRegistry(registryJson, folderedCommandsJson)
    global _initRegistry
    _initRegistry = True

def initInput(inputJson):
    """ Initializes the input json

    Args:
        inputJson (string): path to a json file
    """
    global _initRegistry
    if (_initRegistry == False):
        Printer.print("Command registry must be added first", Printer.ERROR)
    else:
        InputConverter.init(inputJson)

def shutdown():
    """ Disables the Aitpi TODO: Does nothing
    """
    PostalService.sendMessage(CleanUp())
    Printer.print("OFF")

def takeInput(input):
    """ Takes arbitrary string input to pass into the command system

    Args:
        input (string): Anything
    """
    TerminalKeyInput.takeInput(input)