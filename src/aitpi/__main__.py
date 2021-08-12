from aitpi.aitpi import Aitpi
from aitpi.printer import Printer
from aitpi.postal_service import PostalService

class Watcher():
    def consume(self, message):
        Printer.print(" Watcher: %s %s" % (message.data, message.event))

PostalService.addConsumer([1,2,3,4,5,6,7,8,9], PostalService.GLOBAL_SUBSCRIPTION, Watcher())

Aitpi.addRegistry("../example_command_registry.json")
Aitpi.addRegistry("../reg2.json")

Aitpi.initInput("../example_input.json")

while (True):
    input()