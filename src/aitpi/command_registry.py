from genericpath import isdir
from aitpi.message import *
from aitpi.mirrored_json import MirroredJson
from aitpi.postal_service import PostalService
from aitpi.folder_watch import FolderWatch
import os
import time

from aitpi.printer import Printer

class CommandRegistry():
    """Represents a 'registry' of all commands that the user can execute
    """

    def __init__(self, commandRegJson=None, foldersJson=None):
        """Setup data structures
        """
        self._commands = None
        self._foldersForCommands = None
        self._folderCommands = {}
        self._commands = MirroredJson(commandRegJson)
        self._foldersForCommands = MirroredJson(foldersJson)
        PostalService.addConsumer(
            [CommandRegistryCommand.msgId, FolderMessage.msgId],
            PostalService.GLOBAL_SUBSCRIPTION,
            self
        )

        self.reloadFolders()
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

    def contains(self, command):
        for commandList in self._commands.keys():
            if (command in self._commands[commandList].keys()):
                return True
        return False

    def reloadFolders(self):
        """Reloads all the command folders
        """
        # Clear out all old commands
        for T in self._folderCommands.keys():
            for command in self._folderCommands[T].keys():
                if (command in self._commands[T].keys()):
                    self._commands[T].pop(command)
        # Reset what we have so far.
        self._folderCommands = {}
        for index in range(0, len(self._foldersForCommands._settings)):
            for root, dirs, files in os.walk(
                self._foldersForCommands[index]['path'],
                topdown=False
                ):
                for name in files:
                    msgId = self._foldersForCommands[index]["id"]
                    T = self._foldersForCommands[index]["type"]
                    if (not T in self._folderCommands.keys()):
                        self._folderCommands[T] = {}
                    self._folderCommands[T][name] = {}
                    self._folderCommands[T][name]['id'] = msgId
                    self._folderCommands[T][name]['mechanism'] = self._foldersForCommands[index]["mechanism"]
        # Install each command back into the library
        for T in self._folderCommands.keys():
            for command in self._folderCommands[T].keys():
                if (not T in self._commands.keys()):
                    self._commands[T] = {}
                print(command, self._folderCommands[T][command])
                self._commands[T][command] = self._folderCommands[T][command]
                print()
        self.save()

    def getAllCommands(self):
        """Gets the list of commands

        Returns:
            list: commands
        """
        ret = {}
        for T in self._commands.keys():
            for command in self._commands[T].keys():
                ret[command] = self._commands[T][command]
        return ret

    def getCommands(self, T):
        """Gets a dict of commands by type

        Returns:
            Dictionary: commands
        """
        ret = {}
        for command in self._commands[T].keys():
            ret[command] = self._commands[T][command]
        return ret

    def getTypes(self):
        return self._commands.keys()

    def addCommand(self, name, messageID, T, mechanism):
        """Adds a command to the library

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
            if (not T in self._commands.keys()):
                self._commands[T] = {}
            self._commands[T][name] = { "id": messageID, "mechanism": mechanism }
        self.save()
        return True

    @staticmethod
    def removeCommand(T, name):
        """Removes a command

        Args:
            name (str): The name to remove
        """
        self._commands[T].pop(name)
        self.save()

    @staticmethod
    def save():
        """Saves all the commands
        """
        self._commands.save()

    @staticmethod
    def consume(msg):
        """Handles sending actuall commands,
           and watches folder commands for changes.

        Args:
            msg (Message): Either a command, or a folder update
        """
        if (msg.msgId == selfCommand.msgId):
            self.send(msg)
        elif (msg.msgId == FolderMessage.msgId):
            self.reloadFolders()

    @staticmethod
    def send(msg):
        """Handles sending a command to where the library says

        Args:
            command (unknown): Some data that will be sent
        """
        command = msg.data
        action = msg.event
        for T in self._commands.keys():
            if (command in self._commands[T].keys()):
                msg = InputMessage(command, action)
                msg.msgId = int(self._commands[T][command]['id'])
                PostalService.sendMessage(msg)
                return
        Printer.print("'{}' not found in the command library".format(command))
