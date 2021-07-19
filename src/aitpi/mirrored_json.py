import json
import os
from aitpi.printer import Printer

class MirroredJson():
    """Represents a setting, that can and will be saved to a mirrored json file.
    """
    def __init__(self, file):
        """inits a new setting

        Args:
            name (name of setting): [description]
            t (str): The type of setting, determines which folder it is placed
            settings (dict, optional): A dictionary of all settings. Defaults to None.
            autoLoadUponCreation (bool, optional): Tells if this should auto load the settings. Defaults to True.
            defaultFile (string): A file that will be loaded in case the normal file does not exist
        """
        self.file = file
        if (not self.load()):
            Printer.print("Unable to find '{}'".format(file), Printer.ERROR)
        self.save()

    def __getitem__(self, name):
        """Gets a item

        Args:
            name (str): Name of item

        Returns:
            unknown: Some result
        """
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
        f.write(json.dumps(self._settings))

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
            TODO: result
        """
        return self._settings.pop(key, if_fail)
