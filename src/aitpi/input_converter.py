from aitpi.input_initializer import InputInitializer
from aitpi.mirrored_json import MirroredJson
from aitpi.message import *
from aitpi.command_registry import CommandRegistry
from aitpi import router
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

        itemIndex = InputConverter.getIndex(input_unit)

        if (itemIndex == -1):
            Printer.print("Invalid input_unit {}".format(input_unit))
            return
        if (not CommandRegistry.contains(command)):
            Printer.print("Invalid command '{}'".format(command))
            return
        t1 = InputConverter._inputUnits[itemIndex]['type']
        t2 = CommandRegistry.getCommand(command)['input_type']
        if (t1 != t2):
            Printer.print("Changing to mismatch input type '%s' '%s'" % (t1, t2), Printer.WARNING)

        InputConverter._inputUnits[itemIndex]['reg_link'] = command
        InputConverter._inputUnits.save()

    @staticmethod
    def getIndex(value, key='name'):
        """ Gets the index of an item by an attribute

        Args:
            value (string): The value of the attribute we are looking for
            key (str, optional): The attribute key we are looking for. Defaults to 'name'.

        Returns:
            int: The index of the item, -1 if not found
        """
        for index, i in enumerate(InputConverter._inputUnits._settings):
            if (i[key] == value):
                return index
        return -1

    @staticmethod
    def consume(msg):
        """Handles sending out commands when button is pressed

        Args:
            msg (str): The message containing the input_unit number
        """
        input_unit = str(msg.data)
        i = InputConverter.getIndex(input_unit)
        if (i != -1):
            router.sendMessage(
                CommandRegistryCommand(
                    InputConverter._inputUnits[i]['reg_link'],
                    msg.event,
                    InputConverter._inputUnits[i]['type']))
        else:
            Printer.print("'{}' not a valid input".format(input_unit))


    @staticmethod
    def init(file):
        """Initializes all the input mechanisms

        Args:
            file (string): The string 
        """
        router.addConsumer([InputCommand.msgId], InputConverter)
        InputConverter._inputUnits = MirroredJson(file)
        uniqueList = []
        for index, input_unit in enumerate(InputConverter._inputUnits._settings):
            if (input_unit['type'] == 'encoder'):
                uniqueList.append(input_unit['left_trigger'])
                uniqueList.append(input_unit['right_trigger'])
            elif (input_unit['type'] == 'button'):
                uniqueList.append(input_unit['trigger'])
            else:
                Printer.print("'%s' type not supported" % input_unit['type'], Printer.ERROR)
            if (not CommandRegistry.contains(input_unit['reg_link'])
                and input_unit['reg_link'] != ''):
                Printer.print("Found invalid input_unit command '{}', removing...".format(input_unit['reg_link']))
                InputConverter._inputUnits[index]['reg_link'] = ''
        InputConverter._inputUnits.save()
        if (len(uniqueList) != len(set(uniqueList))):
            Printer.print("Duplicate triggers detected: ", Printer.ERROR)
            for dup in set(uniqueList):
                if (uniqueList.count(dup) > 1):
                    Printer.print(" '%s'" % dup)
        for index, input_unit in enumerate(InputConverter._inputUnits._settings):
            InputInitializer.initInput(input_unit)
        Printer.print("Input initialization complete!")
