from genericpath import isdir
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
        PostalService.addConsumer(
            [CommandLibraryCommand.msgId, FolderMessage.msgId],
            PostalService.GLOBAL_SUBSCRIPTION,
            CommandLibrary
        )

        CommandLibrary.reloadFolders()
        for folder in CommandLibrary._foldersForCommands._settings:
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
        for commandList in CommandLibrary._commands.keys():
            if (command in CommandLibrary._commands[commandList].keys()):
                return True
        return False

    @staticmethod
    def reloadFolders():
        """Reloads all the command folders
        """
        # Clear out all old commands
        for T in CommandLibrary._folderCommands.keys():
            for command in CommandLibrary._folderCommands[T].keys():
                if (command in CommandLibrary._commands[T].keys()):
                    CommandLibrary._commands[T].pop(command)
        # Reset what we have so far.
        CommandLibrary._folderCommands = {}
        for index in range(0, len(CommandLibrary._foldersForCommands._settings)):
            for root, dirs, files in os.walk(
                CommandLibrary._foldersForCommands[index]['path'],
                topdown=False
                ):
                for name in files:
                    msgId = CommandLibrary._foldersForCommands[index]["id"]
                    T = CommandLibrary._foldersForCommands[index]["type"]
                    if (not T in CommandLibrary._folderCommands.keys()):
                        CommandLibrary._folderCommands[T] = {}
                    CommandLibrary._folderCommands[T][name] = {}
                    CommandLibrary._folderCommands[T][name]['id'] = msgId
                    CommandLibrary._folderCommands[T][name]['mechanism'] = CommandLibrary._foldersForCommands[index]["mechanism"]
        # Install each command back into the library
        for T in CommandLibrary._folderCommands.keys():
            for command in CommandLibrary._folderCommands[T].keys():
                if (not T in CommandLibrary._commands.keys()):
                    CommandLibrary._commands[T] = {}
                print(command, CommandLibrary._folderCommands[T][command])
                CommandLibrary._commands[T][command] = CommandLibrary._folderCommands[T][command]
                print()
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
    def addCommand(name, messageID, T, mechanism):
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
            CommandLibrary._commands[T][name] = { "id": messageID, "mechanism": mechanism }
        CommandLibrary.save()
        return True

    @staticmethod
    def removeCommand(T, name):
        """Removes a command

        Args:
            name (str): The name to remove
        """
        CommandLibrary._commands[T].pop(name)
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
            CommandLibrary.send(msg)
        elif (msg.msgId == FolderMessage.msgId):
            CommandLibrary.reloadFolders()

    @staticmethod
    def send(msg):
        """Handles sending a command to where the library says

        Args:
            command (unknown): Some data that will be sent
        """
        command = msg.data
        action = msg.event
        for T in CommandLibrary._commands.keys():
            if (command in CommandLibrary._commands[T].keys()):
                msg = InputMessage(command, action)
                msg.msgId = int(CommandLibrary._commands[T][command]['id'])
                PostalService.sendMessage(msg)
                return
        Printer.print("'{}' not found in the command library".format(command))
