import os
import hashlib
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from typing import Callable, Dict

class FileWatcher(FileSystemEventHandler):
  """
  Watches an specific file
  """
  def __init__(self, file_path: str, on_file_change: Callable):
    """Initialize the watcher

    Args:
        file_path (str): file path
        on_file_change (Callable): callback onChange
    """

    self.file_path = file_path
    self.on_file_change = on_file_change
    self.last_modified = os.path.getmtime(file_path)
    self.checksum = self.calculate_checksum()

  def calculate_checksum(self):
    with open(self.file_path, 'r') as file:
      content = file.read()
    return hashlib.sha256(content.encode()).hexdigest()

  def on_modified(self, event: FileSystemEvent):
    """Handler for file modifications

    Args:
        event: File system even from watchdog
    """

    if event.src_path == str(self.file_path):
      logging.info(f"Watched file modified")
      current_checksum = self.calculate_checksum()

      if current_checksum != self.checksum:
        self.checksum = current_checksum
        self.last_modified = os.path.getmtime(self.file_path)
        self.on_file_change(self.file_path, self.last_modified, self.checksum)

class FileWatcherManager:
  def __init__(self) -> None:
    """
    Manages the watchers
    watchers should be a Dict like the following:
    {
      "proposal#": {
        "file_type": {"observer": Observer instance}
      }
    }
    """
    self.watchers: Dict[str, Dict[str, Observer]] ={}

  def start_watcher(self, proposal: str, file_type: str, file_path: str, on_change: Callable):
    """Starts watcher for a given file and proposal

    Args:
        proposal (str): Proposal number from request
        file_type (str): e.g. log or context
        file_path (str): File path
        on_change (Callable): Callback for changes
    """
    if proposal not in self.watchers:
      self.watchers[proposal] = {}

    if file_type in self.watchers[proposal]:
      print("Watcher exits")
      return

    file_watcher = FileWatcher(file_path=file_path, on_file_change=on_change)

    print("Watcher added to the list")

    observer = Observer()
    observer.schedule(file_watcher, os.path.dirname(file_path), recursive=False)
    self.watchers[proposal][file_type] = observer
    self.watchers[proposal][file_type].start()

    print(self.watchers)


  def stop_watcher(self, proposal: str, file_type: str):
    """Stops watching a file type for a given proposal

    Args:
        proposal (str): Proposal number
        file_type (str): e.g. log or context
    """
    if proposal not in self.watchers:
        print("pp isnt being watched")
        return

    if file_type in self.watchers[proposal]:
        self.watchers[proposal][file_type].stop()
        del self.watchers[proposal][file_type]


  def watcher_status(self, proposal: str, file_type: str):
    """Shows the watcher status. False = off, True = on
    """
    if proposal not in self.watchers:
        print("pp isnt being watched")
        return False

    if file_type not in self.watchers[proposal]:
        return False

    return self.watchers[proposal][file_type].is_alive()

