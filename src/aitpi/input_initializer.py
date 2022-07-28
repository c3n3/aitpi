from os import stat
from aitpi.printer import Printer
from aitpi import router
from aitpi.message import *
class TerminalKeyInput():
    """Handles input from a keyboard
    """

    # Change these to whatever you want, high is when pressed, low is when not pressed
    highValue = "1"
    lowValue = "0"

    # The keys registered for manual input
    _keys = {}

    # The keys registered for interrupts
    _keyInterrupts = {}

    # Our keyboard listener, only exists if someone uses 'key_interrupt'
    _listener = None

    @staticmethod
    def initKey(button):
        """ Inits a key to be recognized as valid input

        Args:
            button (Dictionary): Information about a button
        """
        if (button['trigger'] in TerminalKeyInput._keys):
            Printer.print("Duplicate trigger '%s', ignoring" % button['trigger'])
            return
        TerminalKeyInput._keys[button['trigger']] = "_button_{}".format(button['name'])

    @staticmethod
    def onPress(key):
        """ Callback for pressing a key

        Args:
            key (Key): A key object defined by pynput
        """
        # We are not guaranteed a char input, NOTE: Maybe we need to support non char keys?
        if (not hasattr(key, 'char')):
            return
        TerminalKeyInput.handleInterrupt(key.char, "1")

    @staticmethod
    def onRelease(key):
        """ Callback for releasing a key

        Args:
            key (Key): A key object defined by pynput
        """
        # We are not guaranteed a char input, NOTE: Maybe we need to support non char keys?
        if (not hasattr(key, 'char')):
            return
        TerminalKeyInput.handleInterrupt(key.char, "0")

    @staticmethod
    def handleInterrupt(str, action):
        """ Handles all the interrupt keys

        Args:
            str (string): The key pressed
            action ([type]): The event that took place to trigger this, "0" or "1"
        """
        map = TerminalKeyInput._keyInterrupts
        if (str in map):
            val = map[str]
            if ("_button_" in val):
                val = map[str].replace("_button_", "")
                router.sendMessage(InputCommand(val, action))
            # We only care about up presses for encoders
            # NOTE: This seems really minor and natural, but could be configurable with the json
            elif("_left_" in val and action == "1"):
                val = val.replace("_left_", "")
                router.sendMessage(InputCommand(val, "LEFT"))
            elif("_right_" in val and action == "1"):
                val = val.replace("_right_", "")
                router.sendMessage(InputCommand(val, "RIGHT"))

    @staticmethod
    def registerKeyInterrupt(key):
        """ Registers a new interrupt key to report

        Args:
            key (Dictionary): Information about the key
        """
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
        """ Registers a new 'encoder' for 

        Args:
            encoder (Dictionary): Info about the encoder
        """
        if (TerminalKeyInput._listener == None):
            from pynput import keyboard
            TerminalKeyInput._listener = keyboard.Listener(
                on_press=TerminalKeyInput.onPress,
                on_release=TerminalKeyInput.onRelease
            )
            TerminalKeyInput._listener.start()
        # Make sure we have do not have duplicate keys anywhere:
        if (encoder['left_trigger'] in TerminalKeyInput._keyInterrupts):
            Printer.print("Duplicate trigger '%s', ignoring encoder" % (encoder['left_trigger']))
            return
        if (encoder['right_trigger'] in TerminalKeyInput._keyInterrupts):
            Printer.print("Duplicate trigger '%s', ignoring encoder" % (encoder['right_trigger']))
            return
        TerminalKeyInput._keyInterrupts[encoder['right_trigger']] = "_right_{}".format(encoder['name'])
        TerminalKeyInput._keyInterrupts[encoder['left_trigger']] = "_left_{}".format(encoder['name'])


    @staticmethod
    def initEncoder(encoder):
        """ Initializes an encoder

        Args:
            encoder (Dictionary): Info about the encoder
        """
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
        """ Manually input a key for all 'key_input' type inputs

        Args:
            str (string): Anything, will be ignored if not registered
        """
        TerminalKeyInput.handleInput(str)

    def handleInput(str):
        """ Handles any input

        Args:
            str (string): Anything
        """
        map = TerminalKeyInput._keys
        if (str in map):
            # We send both down and up, since there is only ever one event for non interrupts
            val = map[str]
            if ("_button_" in val):
                val = map[str].replace("_button_", "")
                router.sendMessage(InputCommand(val, TerminalKeyInput.highValue))
                router.sendMessage(InputCommand(val, TerminalKeyInput.lowValue))
            elif("_left_" in val):
                val = val.replace("_left_", "")
                router.sendMessage(InputCommand(val, "LEFT"))
            elif("_right_" in val):
                val = val.replace("_right_", "")
                router.sendMessage(InputCommand(val, "RIGHT"))

class InputInitializer():
    """ Handles initializing all input
    """

    # Lets us know if we have already imported the pi modules.
    # We import only when needed so that this does not crash on a normal computer
    _importedPI = False

    @staticmethod
    def initInput(input):
        """ Inits some input unit. Will print an error if invalid

        Args:
            input (Dictionary): information about the input unit
        """
        if (input['type'] == 'button'):
            InputInitializer.initButton(input)
        elif (input['type'] == 'encoder'):
            InputInitializer.initEncoder(input)
        else:
            Printer.print("'%s' is not a supported type" % input['type'])

    @staticmethod
    def initButton(button):
        """ Inits a 'button' 

        Args:
            button (Dictionary): Info about the button
        """
        if (button['mechanism'] == 'key_input'):
            TerminalKeyInput.initKey(button)
        elif (button['mechanism'] == 'key_interrupt'):
            TerminalKeyInput.registerKeyInterrupt(button)
        elif (button['mechanism'] == 'rpi_gpio'):
            if (not InputInitializer._importedPI):
                from aitpi.pi_input_initializer import PiButton
                from aitpi.pi_input_initializer import PiEncoder
            PiButton(button)
        else:
            Printer.print("'%s' is not a supported button mechanism" % button['mechanism'])


    def initEncoder(encoder):
        """ Init a new encoder

        Args:
            encoder (Dictionary): Info about the encoder
        """
        if (encoder['mechanism'] == 'key_input'):
            TerminalKeyInput.initEncoder(encoder)
        elif (encoder['mechanism'] == 'key_interrupt'):
            TerminalKeyInput.registerEncoderInterrupt(encoder)
        elif (encoder['mechanism'] == 'rpi_gpio'):
            if (not InputInitializer._importedPI):
                from aitpi.pi_input_initializer import PiEncoder
                from aitpi.pi_input_initializer import PiButton
            PiEncoder(encoder)
        else:
            Printer.print("'%s' is not a supported encoder mechanism" % encoder['mechanism'])
