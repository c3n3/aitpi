import time
from aitpi.printer import Printer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from aitpi.postal_service import PostalService
from aitpi.message import FolderMessage
from aitpi.message import Message

class FolderWatch():
    watchers = []
    def __init__(self):
        raise "Static class"

    # Will add a folder to be watched, and will send a message at any change with msgId
    @staticmethod
    def watchFolder(folder, msgId):
        Printer.print("Watching: '%s'" % folder)
        try:
            w = Watcher(folder, msgId)
            FolderWatch.watchers.append(w)
            w.run()
        except:
            Printer.print("Invalid folder '%s'" % folder, level=Printer.ERROR)

    @staticmethod
    def stop():
        for w in FolderWatch.watchers:
            w.stop()

class Watcher(FileSystemEventHandler):
    def __init__(self, folder, msgId):
        self.observer = Observer()
        self.folder = folder
        self.msgId = msgId

    def run(self):
        self.observer.schedule(self, self.folder, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.join()

    def on_any_event(self, event):
        msg = Message(self.folder)
        msg.msgId = self.msgId
        if event.is_directory:
            return None
        elif (event.event_type == 'deleted' or event.event_type == 'created' or event.event_type == 'modified'):
            PostalService.sendMessage(msg)