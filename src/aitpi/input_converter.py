from aitpi.mirrored_json import MirroredJson
from aitpi.message import *
from aitpi.command_library import CommandLibrary
from aitpi.postal_service import PostalService
from aitpi.printer import Printer

class InputConverter():
    """Handles the map of input_unit buttons to commands, and sends messages accordingly
    """
    _inputUnits = None

    def __init__(self):
        """This is a static class
        """
        raise "Static class"

    @staticmethod
    def getMap():
        """Returns the map of input_unit

        Returns:
            [type]: [description]
        """
        return InputConverter._inputUnits

    @staticmethod
    def change(input_unit, command):
        """Called to change a input_unit's mapped command

        Args:
            input_unit (str): The 'button' to change
            command (str): The command to change to
        """
        Printer.print("Setting {} to {}".format(input_unit, command))
        if (input_unit in InputConverter._fixed):
            Printer.print("Cannot change input_unit {}".format(input_unit))
        elif (not CommandLibrary.contains(command)):
            Printer.print("Invalid command '{}'".format(command))
        elif (not input_unit in InputConverter._inputUnits.keys()):
            Printer.print("Invalid input_unit {}".format(input_unit))
        else:
            InputConverter._inputUnits[input_unit] = command

    @staticmethod
    def consume(msg):
        """Handles sending out commands when button is pressed

        Args:
            msg (str): The message containing the input_unit number
        """
        if (msg is InputChangeRequest):
            Printer.print("Change request not supported yet.")
            return
        input_unit = str(msg.data)
        if (input_unit in list(InputConverter._inputUnits.keys())):
            PostalService.sendMessage(CommandLibraryCommand(InputConverter._inputUnits[input_unit]))
        else:
            Printer.print("'{}' not a valid button: {}".format(input_unit, list(InputConverter._inputUnits.keys())))

    @staticmethod
    def init(file):
        InputConverter._inputUnits = MirroredJson(file)
        for input_unit in list(InputConverter._inputUnits.keys()):
            if (not CommandLibrary.contains(InputConverter._inputUnits[input_unit]) and InputConverter._inputUnits[input_unit] != ''):
                Printer.print("Found invalid input_unit command '{}', removing...".format(InputConverter._inputUnits[input_unit]))
                InputConverter._inputUnits[input_unit] = ''
        InputConverter._inputUnits.save()

InputConverter.init()
PostalService.addConsumer([InputCommand.msgId], PostalService.GLOBAL_SUBSCRIPTION, InputConverter)
