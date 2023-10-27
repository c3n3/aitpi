from .input_initializer import InputInitializer
from .mirrored_json import MirroredJson
from .message import *
from .command_registry import CommandRegistry
from . import router
from .printer import Printer
from .input_unit import InputUnit

class InputConverter():
    """Handles the map of input_unit buttons to commands, and sends messages accordingly
    """
    _inputUnits = None
    _uniqueList = []

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
            itemIndex = InputConverter.getIndex(input_unit, key='trigger')
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
            if (key in i and i[key] == value):
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
        if (i == -1):
            i = InputConverter.getIndex(input_unit, 'trigger')
        if (i != -1):
            t = 'button'
            if ('type' in InputConverter._inputUnits[i]):
                t = InputConverter._inputUnits[i]['type']
            router.sendMessage(
                CommandRegistryCommand(
                    InputConverter._inputUnits[i]['reg_link'],
                    msg.event,
                    t))
        else:
            Printer.print("'{}' not a valid input".format(input_unit))

    @staticmethod
    def addInput(input_unit):
        if ('type' in input_unit):
            if (input_unit['type'] == 'encoder'):
                InputConverter._uniqueList.append(input_unit['left_trigger'])
                InputConverter._uniqueList.append(input_unit['right_trigger'])
            elif (input_unit['type'] == 'button'):
                InputConverter._uniqueList.append(input_unit['trigger'])
            else:
                Printer.print("'%s' type not supported. Not adding." % input_unit['type'], Printer.ERROR)
                return
        if ('reg_link' not in input_unit):
            input_unit['reg_link'] = ''
        if (not CommandRegistry.contains(input_unit['reg_link'])
            and input_unit['reg_link'] != ''):
            Printer.print("Found invalid input_unit command '{}', removing...".format(input_unit['reg_link']))
            input_unit['reg_link'] = ''

        if ('name' in input_unit and InputConverter.getIndex(input_unit['name'])):
            Printer.print("Duplicate name '{}', Not adding.".format(input_unit['name']), Printer.ERROR)
            return

        if (type(input_unit) ==  InputUnit):
            InputConverter._inputUnits.append(input_unit.getValue())
        else:
            InputConverter._inputUnits.append(input_unit)
        InputConverter._inputUnits.save()
        InputInitializer.initInput(input_unit)

    @staticmethod
    def removeInput(nameOrTrigger):
        index = InputConverter.getIndex(nameOrTrigger, 'trigger')
        if (index == -1):
            index = InputConverter.getIndex(nameOrTrigger, 'name')
        if (index == -1):
            return

        input_unit = InputConverter._inputUnits[index]

        if (InputInitializer.removeInput(input_unit)):
            InputConverter._inputUnits.remove(input_unit)

    @staticmethod
    def init(file):
        """Initializes all the input mechanisms

        Args:
            file (string): The string 
        """
        router.addConsumer([InputCommand.msgId], InputConverter)
        InputConverter._inputUnits = MirroredJson(file)
        for index, input_unit in enumerate(InputConverter._inputUnits._settings):
            if ('type' in input_unit):
                if (input_unit['type'] == 'encoder'):
                    InputConverter._uniqueList.append(input_unit['left_trigger'])
                    InputConverter._uniqueList.append(input_unit['right_trigger'])
                elif (input_unit['type'] == 'button'):
                    InputConverter._uniqueList.append(input_unit['trigger'])
                else:
                    Printer.print("'%s' type not supported" % input_unit['type'], Printer.ERROR)
            if (not CommandRegistry.contains(input_unit['reg_link'])
                and input_unit['reg_link'] != ''):
                Printer.print("Found invalid input_unit command '{}', removing...".format(input_unit['reg_link']))
                InputConverter._inputUnits[index]['reg_link'] = ''
        InputConverter._inputUnits.save()
        if (len(InputConverter._uniqueList) != len(set(InputConverter._uniqueList))):
            Printer.print("Duplicate triggers detected: ", Printer.ERROR)
            for dup in set(InputConverter._uniqueList):
                if (InputConverter._uniqueList.count(dup) > 1):
                    Printer.print(" '%s'" % dup)
        for index, input_unit in enumerate(InputConverter._inputUnits._settings):
            InputInitializer.initInput(input_unit)
        Printer.print("Input initialization complete!")
