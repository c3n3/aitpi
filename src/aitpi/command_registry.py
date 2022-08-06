from genericpath import isdir
from aitpi.message import *
from aitpi.mirrored_json import MirroredJson
from aitpi import router
from aitpi.folder_watch import FolderWatch
import os
import time

from aitpi.printer import Printer

class CommandRegistry():
    """ Represents a 'registry' of all commands that the user can execute
    """

    _registries = []

    def __init__(self, commandRegJson=None, foldersJson=None):
        """ Setup data structures
        """
        self.regFile = commandRegJson
        self.foldersFile = foldersJson
        self._commands = None
        self._foldersForCommands = None
        self._commands = MirroredJson(commandRegJson)
        self._foldersForCommands = MirroredJson(foldersJson) if foldersJson != None else None
        router.addConsumer(
            [CommandRegistryCommand.msgId],
            self
        )
        if (self._foldersForCommands != None):

            # Watch all the folders
            self.initFoldersForCommands()

            # Remove all old foldered commands
            self.cleanAllFolderCommands()

            # Reload all commands from the folders
            for folder in range(0, len(self._foldersForCommands)):
                self.reloadFolder(self._foldersForCommands[folder]['path'])
        CommandRegistry._registries.append(self)

    def cleanAllFolderCommands(self):
        """ Removes all folderd commands from the json file
        """
        for item in self._foldersForCommands._settings:
            if (item == None):
                return
            # Clear out all old commands
            # We assume the folder has changed entirely
            commands = self.getCommandsByType(item['type'])
            for command in commands:
                if 'path' in command:
                    self._commands.pop(command)
        self.save()

    def initFoldersForCommands(self):
        """ Takes care of initalizing the foldersForCommands setup
        """

        # Now we need to subscribe to the folder messages
        router.addConsumer(
            [FolderMessage.msgId],
            self
        )
        for folder in self._foldersForCommands._settings:
            if (not isdir(folder['path'])):
                Printer.print("Did not find dir '{}' creating...".format(folder['path']))
                os.system("mkdir {}".format(folder['path']))
                time.sleep(0.1)
            try:
                if (int(folder['id']) < 0):
                    Printer.print("Message ID below zero for '%s'" % folder['path'], Printer.WARNING)
                    Printer.print("- Unsupported behavior, negative numbers reserved for AITPI.", Printer.WARNING)
                else:
                    FolderWatch.watchFolder(folder['path'], FolderMessage.msgId)
            # TODO: Check exception type so we don't say this is an invalid ID when another error occured
            except:
                Printer.print("Invalid folder message id '%s'" % folder['id'], Printer.ERROR)
            # Add watch to every folder

    @staticmethod
    def contains(command):
        """ Returns whether the command exists in this registry
        """
        if (CommandRegistry.getCommand(command) == None):
            return False
        return True

    @staticmethod
    def getCommand(command):
        for registry in CommandRegistry._registries:
            if (command in registry._commands):
                return registry._commands[command]
        return None

    @staticmethod
    def getAllCommandsGlobal():
        ret = {}
        for registry in CommandRegistry._registries:
            for commandList in registry._commands.keys():
                ret[commandList] = registry._commands[commandList]
        return ret

    @staticmethod
    def getFolder(foldersFile, name):
        for registry in CommandRegistry._registries:
            if (registry.foldersFile != foldersFile):
                continue
            for index in range(0, len(registry._foldersForCommands)):
                folder = registry._foldersForCommands[index]
                if (folder['name'] == name):
                    return folder
        return None

    def findByProperty(self, array, propertyName, propertyVal):
        """ Find an item in an array by a property of that item

            Returns:
                bool: if contains
        """
        for item in array:
            if (item[propertyName] == propertyVal):
                return item
        return None

    def reloadFolder(self, folder):
        """ Reloads all the command folders
        """
        item = self.findByProperty(self._foldersForCommands, 'path', folder)
        if (item == None):
            return
        commandsToClean = []
        for command in self._commands:
            if self._commands[command]['type'] == item['type']:
                commandsToClean.append(command)
        for command in commandsToClean:
            self._commands.pop(command)

        # Add all the files to the registry
        for root, dirs, files in os.walk(
            folder,
            topdown=False
            ):
            for name in files:
                msgId = item['id']
                if (name not in self._commands.keys()):
                    self._commands[name] = {}
                self._commands[name]['id'] = msgId
                self._commands[name]['input_type'] = item['input_type']
                self._commands[name]['path'] = folder
                self._commands[name]['type'] = item['type']
        # Update the mirrored json
        self.save()

    def getAllCommands(self):
        """ Gets the list of commands

        Returns:
            list: commands
        """
        return self._commands

    def getCommandsByType(self, T):
        """ Gets a dict of commands by type

        Returns:
            Dictionary: commands
        """
        ret = {}
        for command in self._commands:
            print(command)
            if self._commands[command]['type'] == T:
                ret[command] = self._commands[command]
        return ret

    def getTypes(self):
        """ Returns all types in the registry

        Returns:
            list: list of all types
        """
        ret = []
        for command in self._commands:
            if command['type'] not in ret:
                ret.append(command['type'])
        return self._commands.keys()

    def addCommand(self, name, messageID, T, inputType):
        """ Adds a command to the library

        Args:
            name (str): The name of the command
            messageID (int): The message id the command is sent to

        Returns:
            [type]: True if added. False if duplicate (not added)
        """
        if (self.contains(name)):
            Printer.print("Cannot add '{}', duplicate name".format(name))
            return False
        else:
            self._commands[name] = { "id": messageID, "input_type": inputType, 'type': T }
        self.save()
        return True

    def removeCommand(self, name):
        """ Removes a command

        Args:
            name (str): The name to remove
        """
        self._commands.pop(name)
        self.save()

    def clearType(self, T):
        """ Removes all the commands of a type

        Args:
            T (string): the type
        """
        purgeList = []
        for command in self._commands:
            if command['type'] == T:
                purgeList.append(command)
        for purge in purgeList:
            self._commands.pop(purge)

    def save(self):
        """ Saves all the commands to the mirrored json
        """
        self._commands.save()

    def consume(self, msg):
        """ Handles sending actuall commands,
            and watches folder commands for changes.

        Args:
            msg (Message): Either a command, or a folder update
        """
        if (msg.msgId == CommandRegistryCommand.msgId):
            self.send(msg)
        elif (msg.msgId == FolderMessage.msgId):
            self.reloadFolder(msg.data)

    def send(self, msg):
        """ Handles sending a command to where the library says

        Args:
            command (unknown): Some data that will be sent
        """
        command = msg.data
        action = msg.event
        type = msg.type
        if (command in self._commands):
            if (self._commands[command]['input_type'] != type):
                Printer.print("Mismatched input_type for command '%s'" % command, Printer.WARNING)
            msg = InputMessage(command, action, self._commands[command])
            msg.msgId = int(self._commands[command]['id'])
            router.sendMessage(msg)
            return

    def updateFromFile(self):
        self._commands.load()