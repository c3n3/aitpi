from aitpi.printer import Printer
class Consumer():
    """The simplest consumer class
    """
    # isActive is static just to verify that it will always exist,
    # instances when edited will not change this value
    isActive = False
    def __init__(self):
        """inits the recieve buffer
        """
        self.receiveBuffer = []

    def consume(self, msg):
        """Consumes a message

        Args:
            msg (Message): The message recieved
        """
        Printer.print("Default comsumer recieved some message")
