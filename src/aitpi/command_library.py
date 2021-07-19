from genericpath import isdir
# from guitar.messaging.msg_list import CommandLibraryCommand
# from guitar.messaging.msg_list import FolderMessage
from aitpi.message import *
from aitpi.mirrored_json import MirroredJson
from aitpi.postal_service import PostalService
from aitpi.folder_watch import FolderWatch
import os
import time

from aitpi.printer import Printer

class CommandLibrary():
    """Represents a 'library' of all commands that the user can execute
    """
    _commands = None
    _foldersForCommands = None
    _folderCommands = {}

    def __init__(self):
        """This is a static class, not instantiation
        """
        raise "Static class"

    @staticmethod
    def init(commandRegJson, foldersJson):
        """Called to init the library. Reads in the commands from respective savable setting,
           Adds self as consumer with own message id
        """
        CommandLibrary._commands = MirroredJson(commandRegJson)
        CommandLibrary._foldersForCommands = MirroredJson(foldersJson)
        PostalService.addConsumer([CommandLibraryCommand.msgId, FolderMessage.msgId], PostalService.GLOBAL_SUBSCRIPTION, CommandLibrary)
        CommandLibrary._foldersForCommands.save()


        CommandLibrary.reloadFolders()
        for folder in CommandLibrary._foldersForCommands._settings.keys():
            if (not isdir(folder)):
                Printer.print("Did not find dir '{}' creating...".format(folder))
                os.system("mkdir {}".format(folder))
                time.sleep(0.1)

            # Add watch to every folder
            FolderWatch.watchFolder(folder, FolderMessage.msgId)

    @staticmethod
    def contains(command):
        for commandList in CommandLibrary._commands.keys():
            if (command in CommandLibrary._commands[commandList].keys()):
                return True
        return False

    @staticmethod
    def reloadFolders():
        """Reloads all the command folders i.e recordings / presets
        """
        # Clear out all old commands
        for T in CommandLibrary._folderCommands.keys():
            for command in CommandLibrary._folderCommands[T].keys():
                if (command in CommandLibrary._commands[T].keys()):
                    CommandLibrary._commands[T].pop(command)
        # Reset what we have so far.
        CommandLibrary._folderCommands = {}
        for folder in CommandLibrary._foldersForCommands._settings.keys():
            for root, dirs, files in os.walk(folder, topdown=False):
                for name in files:
                    msgId = CommandLibrary._foldersForCommands[folder]["msgId"]
                    T = CommandLibrary._foldersForCommands[folder]["type"]
                    if (not T in CommandLibrary._folderCommands.keys()):
                        CommandLibrary._folderCommands[T] = {}
                    CommandLibrary._folderCommands[T][name] = msgId
        # Install each command back into the library
        for T in CommandLibrary._folderCommands.keys():
            for command in CommandLibrary._folderCommands[T].keys():
                CommandLibrary._commands[T][command] = CommandLibrary._folderCommands[T][command]
        CommandLibrary.save()

    @staticmethod
    def getAllCommands():
        """Gets the list of commands

        Returns:
            list: commands
        """
        ret = {}
        for T in CommandLibrary._commands.keys():
            for command in CommandLibrary._commands[T].keys():
                ret[command] = CommandLibrary._commands[T][command]
        return ret

    @staticmethod
    def getCommands(T):
        """Gets a dict of commands by type

        Returns:
            Dictionary: commands
        """
        ret = {}
        for command in CommandLibrary._commands[T].keys():
            ret[command] = CommandLibrary._commands[T][command]
        return ret

    @staticmethod
    def getTypes():
        return CommandLibrary._commands.keys()

    @staticmethod
    def addCommand(name, messageID, T):
        """Adds a command to the library

        Args:
            name (str): The name of the command
            messageID (int): The message id the command is sent to

        Returns:
            [type]: True if added. False if duplicate (not added)
        """
        if (CommandLibrary.contains(name)):
            Printer.print("Cannot add '{}', duplicate name".format(name))
            return False
        else:
            if (not T in CommandLibrary._commands.keys()):
                CommandLibrary._commands[T] = {}
            CommandLibrary._commands[T][name] = messageID
        CommandLibrary.save()
        return True

    @staticmethod
    def removeCommand(name):
        """Removes a command

        Args:
            name (str): The name to remove
        """
        CommandLibrary._commands.pop(name)
        CommandLibrary.save()

    @staticmethod
    def save():
        """Saves all the commands
        """
        CommandLibrary._commands.save()

    @staticmethod
    def consume(msg):
        """Handles sending actuall commands,
           and watches folder commands for changes.

        Args:
            msg (Message): Either a command, or a folder update
        """
        if (msg.msgId == CommandLibraryCommand.msgId):
            CommandLibrary.send(msg.data)
        elif (msg.msgId == FolderMessage.msgId):
            CommandLibrary.reloadFolders()

    @staticmethod
    def send(command):
        """Handles sending a command to where the library says

        Args:
            command (unknown): Some data that will be sent
        """
        for T in CommandLibrary._commands.keys():
            if (command in CommandLibrary._commands[T].keys()):
                msg = Message(command)
                msg.msgId = int(CommandLibrary._commands[T][command])
                PostalService.sendMessage(msg)
                return
        Printer.print("'{}' not found in the command library".format(command))

CommandLibrary.init()