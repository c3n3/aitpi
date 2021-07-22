from aitpi.command_library import CommandLibrary
from aitpi.input_converter import InputConverter
from aitpi.postal_service import PostalService
from aitpi.message import *
from aitpi.printer import Printer
from aitpi.input_initializer import *

CommandLibrary.init("test.json", "folder_test.json")


class Watcher():
    def consume(self, message):
        Printer.print(" Watcher: %s %s" % (message.data, message.event))

InputConverter.init("inp.json")


# PostalService.addConsumer(
#     [CommandLibraryCommand.msgId, InputCommand.msgId],
#     PostalService.GLOBAL_SUBSCRIPTION,
#     Watcher())
PostalService.addConsumer([0], PostalService.GLOBAL_SUBSCRIPTION, Watcher())


while (True):
    TerminalKeyInput.takeInput(input())