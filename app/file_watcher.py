import os
import hashlib
import logging
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from typing import Callable, Dict

class FileWatcher(FileSystemEventHandler):
  """
  Watches an specific file
  """
  def __init__(self, file_path: str, on_file_change: Callable, loop: asyncio.AbstractEventLoop):
    """Initialize the watcher

    Args:
        file_path (str): file path
        on_file_change (Callable): callback onChange
    """

    self.file_path = file_path
    self.on_file_change = on_file_change
    self.last_modified = os.path.getmtime(file_path)
    self.checksum = self.calculate_checksum()
    self.loop = loop

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
        self.loop.create_task(self.on_file_change(self.file_path, self.last_modified, self.checksum))

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
    self.watchers: Dict[str, Observer] ={}
    self.loop = asyncio.get_event_loop()

  def start_watcher(self, file_path: str, on_change: Callable):
    """Starts watcher for a given file and proposal

    Args:
        file_path (str): File path
        on_change (Callable): Callback for changes
    """
    if file_path not in self.watchers:
      self.watchers[file_path] = {}

    file_watcher = FileWatcher(file_path=file_path, on_file_change=on_change, loop=self.loop)

    print("Watcher added to the list")

    observer = Observer()
    observer.schedule(file_watcher, os.path.dirname(file_path), recursive=False)
    self.watchers[file_path] = observer
    self.watchers[file_path].start()

    print(self.watchers)

  def stop_watcher(self, file_path: str):
    """Stops watching a file type for a given proposal

    Args:
        proposal (str): Proposal number
        file_type (str): e.g. log or context
    """
    if  file_path not in self.watchers:
        print("pp isnt being watched")
        return

    if file_path in self.watchers:
        self.watchers[file_path].stop()
        del self.watchers[file_path]


  def watcher_status(self, file_path: str):
    """Shows the watcher status. False = off, True = on
    """
    if file_path not in self.watchers:
        print("pp isnt being watched")
        return False

    return self.watchers[file_path].is_alive()
