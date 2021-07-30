from os import stat
from aitpi.printer import Printer
from aitpi.postal_service import PostalService
from aitpi.message import *
class TerminalKeyInput():
    _keys = {}
    _keyInterrupts = {}
    _listener = None

    @staticmethod
    def initKey(button):
        if (button['trigger'] in TerminalKeyInput._keys):
            Printer.print("Duplicate trigger '%s', ignoring" % button['trigger'])
            return
        TerminalKeyInput._keys[button['trigger']] = "_button_{}".format(button['name'])

    @staticmethod
    def onPress(key):
        if (not hasattr(key, 'char')):
            return
        TerminalKeyInput.handleInterrupt(key.char, "DOWN")

    @staticmethod
    def onRelease(key):
        if (not hasattr(key, 'char')):
            return
        TerminalKeyInput.handleInterrupt(key.char, "UP")

    @staticmethod
    def handleInterrupt(str, action):
        map = TerminalKeyInput._keyInterrupts
        if (str in map):
            val = map[str]
            if ("_button_" in val):
                val = map[str].replace("_button_", "")
                PostalService.sendMessage(InputCommand(val, action))
            # We only care about up presses for encoders
            elif("_left_" in val and action == "UP"):
                val = val.replace("_left_", "")
                PostalService.sendMessage(InputCommand(val, "LEFT"))
            # We only care about up presses for encoders
            elif("_right_" in val and action == "UP"):
                val = val.replace("_right_", "")
                PostalService.sendMessage(InputCommand(val, "RIGHT"))

    @staticmethod
    def registerKeyInterrupt(key):
        if (TerminalKeyInput._listener == None):
            from pynput import keyboard
            TerminalKeyInput._listener = keyboard.Listener(
                on_press=TerminalKeyInput.onPress,
                on_release=TerminalKeyInput.onRelease
            )
            TerminalKeyInput._listener.start()
        # Make sure we have do not have duplicate keys anywhere:
        if (key['trigger'] in TerminalKeyInput._keyInterrupts):
            Printer.print("Duplicate trigger '%s', ignoring" % key['trigger'])
            return
        TerminalKeyInput._keyInterrupts[key['trigger']] = "_button_{}".format(key['name'])

    @staticmethod
    def registerEncoderInterrupt(encoder):
        if (TerminalKeyInput._listener == None):
            from pynput import keyboard
            TerminalKeyInput._listener = keyboard.Listener(
                on_press=TerminalKeyInput.onPress,
                on_release=TerminalKeyInput.onRelease
            )
            TerminalKeyInput._listener.start()
        # Make sure we have do not have duplicate keys anywhere:
        if (encoder['left_trigger'] in TerminalKeyInput._keyInterrupts):
            Printer.print("Duplicate trigger '%s', ignoring, and '%s'" % (encoder['left_trigger'], encoder['right_trigger']))
            return
        if (encoder['right_trigger'] in TerminalKeyInput._keyInterrupts):
            Printer.print("Duplicate trigger '%s', ignoring, and '%s'" % (encoder['right_trigger'], encoder['left_trigger']))
            return
        TerminalKeyInput._keyInterrupts[encoder['right_trigger']] = "_right_{}".format(encoder['name'])
        TerminalKeyInput._keyInterrupts[encoder['left_trigger']] = "_left_{}".format(encoder['name'])


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
        TerminalKeyInput.handleInput(str)

    def handleInput(str):
        map = TerminalKeyInput._keys
        if (str in map):
            # We send both down and up, since there is only ever one event for non interrupts
            val = map[str]
            if ("_button_" in val):
                val = map[str].replace("_button_", "")
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
    _importedPI = False
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
        elif (button['mechanism'] == 'key_interrupt'):
            TerminalKeyInput.registerKeyInterrupt(button)
        else:
            Printer.print("'%s' is not a supported button mechanism" % button['mechanism'])
    

    def initEncoder(encoder):
        if (encoder['mechanism'] == 'key_input'):
            TerminalKeyInput.initEncoder(encoder)
        elif (encoder['mechanism'] == 'key_interrupt'):
            TerminalKeyInput.registerEncoderInterrupt(encoder)
        elif (encoder['mechanism'] == 'gpio'):
            if (not InputInitializer._importedPI):
                from aitpi.pi_input_initializer import PiEncoder
            PiEncoder(encoder)
        else:
            Printer.print("'%s' is not a supported encoder mechanism" % encoder['mechanism'])
