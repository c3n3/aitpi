class Printer():
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"

    def __init__(self) -> None:
        """ Fails since this is a static class
        """
        raise "No instantiation, static class"

    @staticmethod
    def print(msg, level = Printer.INFO):
        """ Prints out a message according to the log level

        Args:
            msg (str): the message to print
            level (str): the log level. Use class defined levels
        """
        print("ABTPI {}: {}".format(level, msg))