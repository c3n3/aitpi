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

class PrintCommandLibrary():
    def consume(self, message):
        for T in CommandLibrary._commands.keys():
            for command in CommandLibrary._commands[T]:
                print("/", T, "/", command)

InputConverter.init("inp.json")


# PostalService.addConsumer(
#     [CommandLibraryCommand.msgId, InputCommand.msgId],
#     PostalService.GLOBAL_SUBSCRIPTION,
#     Watcher())
PostalService.addConsumer([0], PostalService.GLOBAL_SUBSCRIPTION, Watcher())
PostalService.addConsumer([1], PostalService.GLOBAL_SUBSCRIPTION, PrintCommandLibrary())


while (True):
    TerminalKeyInput.takeInput(input())