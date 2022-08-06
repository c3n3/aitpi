from setuptools import Command
from aitpi.message import CleanUp
from aitpi.printer import Printer
from aitpi import router
from aitpi.command_registry import CommandRegistry
from aitpi.input_converter import InputConverter
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
    router.sendMessage(CleanUp())

def takeInput(input):
    """ Takes arbitrary string input to pass into the command system

    Args:
        input (string): Anything
    """
    TerminalKeyInput.takeInput(input)

def addCommandToRegistry(registryFile, command, id, type, inputType):
    """ Adds a command to the registry

    Args:
        registryFile (string): The path to the json file the registry mirrors
        command (string): string denoting the name of the command
        id (int): The id the command will be sent over
        type (string): The type of the new command
        inputType (string): the type of input 'button', 'encoder'
    """
    for registry in CommandRegistry._registries:
        if (registry.regFile == registryFile):
            registry.addCommand(command, id, type, inputType)

def clearCommandTypeInRegistry(registryFile, type):
    """ Clears all commands from a 'type' in a registry

    Args:
        registryFile (string): The path to the json file the registry mirrors
        type (string): The type to clear
    """
    for registry in CommandRegistry._registries:
        if (registry.regFile == registryFile):
            registry.clearType(type)
            break

def updateRegistryFromFile(registryFile):
    """ Updates registry from file

    Args:
        registryFile (string): The path to the json file the registry mirrors
    """
    for registry in CommandRegistry._registries:
        if (registry.regFile == registryFile):
            registry.updateFromFile()
            break

def removeCommandFromRegistry(registryFile, command):
    """ Removes a command from the registry

    Args:
        registryFile (string): The path to the json file the registry mirrors
        command (string): The name of the command
        type (string): The type of the command
    """
    for registry in CommandRegistry._registries:
        if (registry.regFile == registryFile):
            registry.removeCommand(command)

def changeInputRegLink(inputName, regLink):
    """ Changes the reg link of an input unit

    Args:
        inputName (string): The input unit name
        regLink (string): The new link to a command registry
    """
    InputConverter.change(inputName, regLink)

def getFolderedCommands(foldersFile, folderedName):
    """[summary]

    Args:
        foldersFile (string): The path to the json file the registry mirrors
        folderedName (string): The name of the foldered comands entry
    """
    return CommandRegistry.getFolder(foldersFile, folderedName)

def getCommandsByInputType(inputType):
    commands = CommandRegistry.getAllCommandsGlobal()
    ret = []
    for command in commands:
        if command['input_type'] == inputType:
            ret.append(command)
    return ret

def getCommandsByType(T):
    ret = []
    for registry in CommandRegistry._registries:
        ret.extend(registry.getCommandsByType(T))
    return ret

def getCommands():
    """ Gets all the commands from any command registry

    Returns:
        []: an array of all command names
    """
    return CommandRegistry.getAllCommandsGlobal()

def getInputs():
    """ Get all of the inputs from json
    """
    return InputConverter._inputUnits._settings

def getInputsByType(T):
    """ Get inputs by their type
    """
    ret = []
    for input in InputConverter._inputUnits:
        if input['type'] == T:
            ret.append(input)
    return ret