from aitpi.printer import Printer
from aitpi.postal_service import PostalService
from aitpi.message import *
class TerminalKeyInput():
    _keys = {}

    @staticmethod
    def initKey(button):
        if (button['trigger'] in TerminalKeyInput._keys):
            Printer.print("Duplicate trigger '%s', ignoring" % button['trigger'])
            return
        TerminalKeyInput._keys[button['trigger']] = "_button_{}".format(button['name'])

    @staticmethod
    def initEncoder(encoder):
        if (encoder['left_trigger'] in TerminalKeyInput._keys):
            Printer.print("Duplicate trigger '%s', ignoring" % encoder['left_trigger'])
            return
        if (encoder['right_trigger'] in TerminalKeyInput._keys):
            Printer.print("Duplicate trigger '%s', ignoring" % encoder['right_trigger'])
            return
        TerminalKeyInput._keys[encoder['left_trigger']] = "_left_{}".format(encoder['name'])
        TerminalKeyInput._keys[encoder['right_trigger']] = "_right_{}".format(encoder['name'])
    
    @staticmethod
    def takeInput(str):
        if (str in TerminalKeyInput._keys):
            # We send both down and up, since there is only ever one event for non interrupts
            val = TerminalKeyInput._keys[str]
            if ("_button_" in val):
                val = TerminalKeyInput._keys[str].replace("_button_", "")
                PostalService.sendMessage(InputCommand(val, "DOWN"))
                PostalService.sendMessage(InputCommand(val, "UP"))
            elif("_left_" in val):
                val = val.replace("_left_", "")
                PostalService.sendMessage(InputCommand(val, "LEFT"))
            elif("_right_" in val):
                val = val.replace("_right_", "")
                PostalService.sendMessage(InputCommand(val, "RIGHT"))

        else:
            print("Ignoring: ", str)

class InputInitializer():
    @staticmethod
    def initInput(input):
        if (input['type'] == 'button'):
            InputInitializer.initButton(input)
        elif (input['type'] == 'encoder'):
            InputInitializer.initEncoder(input)
        else:
            Printer.print("'%s' is not a supported type" % input['type'])

    @staticmethod
    def initButton(button):
        if (button['mechanism'] == 'key_input'):
            TerminalKeyInput.initKey(button)
        else:
            Printer.print("'%s' is not a supported button mechanism" % button['mechanism'])
    
    def initEncoder(encoder):
        if (encoder['mechanism'] == 'key_input'):
            TerminalKeyInput.initEncoder(encoder)
        else:
            Printer.print("'%s' is not a supported encoder mechanism" % encoder['mechanism'])
