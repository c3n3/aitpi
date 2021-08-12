from os import stat
from aitpi.printer import Printer
from aitpi.postal_service import PostalService
from aitpi.message import *
import RPi.GPIO as GPIO
import threading
from time import sleep

__initedPi = False

def _piInit():
    global __initedPi
    if (not __initedPi):
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
    __initedPi = True

class PiEncoder():
    _initedEncoders = []
    def __init__(self, encoder):
        try:
            self.triggerL = int(encoder['left_trigger'])
        except:
            Printer.print("Invalid left_trigger '%s' under '%s'" % (encoder['left_trigger'], encoder['name']))
            return

        try:
            self.triggerR = int(encoder['right_trigger'])
        except:
            Printer.print("Invalid right_trigger '%s' under '%s'" % (encoder['right_trigger'], encoder['name']))
            return

        _piInit()
        self.encoder = encoder
        self.triggerLCounter = 1
        self.triggerRCounter = 1

        self.LockRotary = threading.Lock()
        try:
            GPIO.setup(self.triggerL, GPIO.IN)
            GPIO.setup(self.triggerR, GPIO.IN)
            GPIO.add_event_detect(self.triggerL, GPIO.RISING, callback=self.handleInterrupt)
            GPIO.add_event_detect(self.triggerR, GPIO.RISING, callback=self.handleInterrupt)
        except Exception:
            Printer.print("Failed to init encoder '%s'" % encoder['name'])
            return
        PiEncoder._initedEncoders.append(self)
        return

    def handleInterrupt(self, leftOrRight):
        triggerL = GPIO.input(self.triggerL)
        triggerR = GPIO.input(self.triggerR)

        if self.triggerLCounter == triggerL and self.triggerRCounter == triggerR:
            return

        self.triggerLCounter = triggerL
        self.triggerRCounter = triggerR

        if (triggerL and triggerR):
            self.LockRotary.acquire()
            if leftOrRight == self.triggerR:
                PostalService.sendMessage(InputCommand(self.encoder['name'], "RIGHT"))
            else:
                PostalService.sendMessage(InputCommand(self.encoder['name'], "LEFT"))
            self.LockRotary.release()
        return

class PiButton():
    _buttons = []
    def __init__(self, button):
        bounce = 25
        _piInit()
        try:
            GPIO.setup(int(button['trigger']), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except:
            Printer.print("Failed to setup button '%s'" % button['name'])
        try:
            GPIO.add_event_detect(int(button['trigger']), GPIO.BOTH, callback=self.press, bouncetime=bounce)
        except:
            Printer.print("Failed to add event interrupt to button '%s'" % button['name'])
        self.button = button

    def press(self, gpio):
        if (GPIO.input(int(self.button['trigger'])) != 1):
            PostalService.sendMessage(InputCommand(self.button['name'], "DOWN"))
        else:
            PostalService.sendMessage(InputCommand(self.button['name'], "UP"))

class PiCleanup():
    @staticmethod
    def consume(msg):
        GPIO.cleanup()

PostalService.addConsumer([CleanUp.msgId], PostalService.GLOBAL_SUBSCRIPTION, PiCleanup)
