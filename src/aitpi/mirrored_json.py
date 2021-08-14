import json
import os
from aitpi.printer import Printer

class MirroredJson():
    """ Tries its best to mimick a json file, and reflect changes in file upon saving.
        Very useful for handling settings that need to be persistent
    """
    def __init__(self, file):
        """ The file to mirror

        Args:
            file (string): path to the file
        """
        self.file = file
        if (not self.load()):
            Printer.print("Unable to find '{}'".format(file), Printer.ERROR)
        self.save()

    def __len__(self):
        """ So we can call len(MirroredJson)

        Returns:
            int: The length of the settings
        """
        return len(self._settings)

    def __getitem__(self, name):
        """Gets a item

        Args:
            name (str): Name of item

        Returns:
            unknown: Some result
        """
        if (name == ''):
            return None
        if (isinstance(self._settings, list)):
            if (len(self._settings) <= name):
                Printer.print("Index '%s' out of bounds" % name)
                return None
            return self._settings[name]
        if (not (name in self._settings.keys())):
            Printer.print("'{}' not found in {}".format(name, self.file), Printer.ERROR)
            return None
        else:
            return self._settings[name]

    def __setitem__(self, name, val):
        """Sets some item

        Args:
            name (str): Item name
            val (unkown): Some thing
        """
        self._settings[name] = val
        self.save()

    def save(self):
        """Saves self to mirrord json file
        """
        f = open(self.file,'w')
        f.write(json.dumps(self._settings, indent=4))

    def load(self):
        """Loads from mirrored json file

        Returns:
            bool: True if succeeds, false otherwise
        """
        if os.path.isfile(self.file):
            f = open(self.file,'r')
            self._settings = json.load(f)
            f.close()
            return True
        return False

    def keys(self):
        """Gets keys

        Returns:
            keys: Keys
        """
        return self._settings.keys()

    def pop(self, key, if_fail = ""):
        """Pops an item from settings

        Args:
            key (str): The key to pop
            if_fail (str, optional): What happens on failure. Defaults to "".

        Returns:
            unknown: result
        """
        return self._settings.pop(key, if_fail)
