import os
import hashlib
import logging
import asyncio
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from typing import Callable, Dict

from app.utils import fetch_file_data

# Logging
logger = logging.getLogger("uvicorn")


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
        self.loop = loop
        self.checksum = None

    async def calculate_checksum(self):
        file_data = await fetch_file_data(self.file_path)
        return file_data['checksum']

    async def initialize_checksum(self):
        file_data = await fetch_file_data(self.file_path)
        self.checksum = file_data["checksum"]

    async def on_modified_async(self, event: FileSystemEvent):
        """Handler for file modifications

        Args:
            event: File system even from watchdog
        """

        if event.src_path == str(self.file_path):
            logger.info(f"Watched file modified")
            current_checksum = await self.calculate_checksum()

            if current_checksum != self.checksum:
                self.checksum = current_checksum
                self.last_modified = os.path.getmtime(self.file_path)
                await self.on_file_change(self.file_path, self.last_modified, self.checksum)

    def on_modified(self, event: FileSystemEvent):
        self.loop.create_task(self.on_modified_async(event))


class FileWatcherManager:
    def __init__(self) -> None:
        """
        Manages the watchers
        watchers should be a Dict like the following:
        {
          file_path: {
            count: how many clients are pulling,
            Observer: watcher observer,
            FileWatcher: file watcher instance,
            last_activity: last pulled timestamp,
          }
        }
        """
        self.watchers: Dict[str, Dict[str,int | Observer | FileWatcher | float]] = {}
        self.loop = asyncio.get_event_loop()

    async def start_watcher(self, file_path: str, on_change: Callable):
        """Starts watcher for a given file and proposal

        Args:
            file_path (str): File path
            on_change (Callable): Callback for changes
        """
        if file_path not in self.watchers:
            self.watchers[file_path] = {}
        else:
            self.watchers[file_path]["count"] += 1
            self.watchers[file_path]["last_activity"] = time.time()
            logger.info(f"Client added to an watched file path: {file_path}")
            logger.info(f"{self.watchers}")
            return
        
        file_watcher = FileWatcher(
            file_path=file_path, on_file_change=on_change, loop=self.loop)

        logger.info(f"""New watcher added to the list \n
                     file {file_path} is being watched now""")
        
        await file_watcher.initialize_checksum()
        observer = Observer()
        observer.schedule(file_watcher, os.path.dirname(
            file_path), recursive=False)
    
        self.watchers[file_path]["observer"] = observer
        self.watchers[file_path]["watcher"] = file_watcher
        self.watchers[file_path]["count"] = 1   
        self.watchers[file_path]["observer"].start()

    def stop_watcher(self, file_path: str):
        """Stops watching a file type for a given path
        """
        if file_path not in self.watchers:
            logging.warning("File isn't being watched, nothing to do.")
            return

        if file_path in self.watchers:
            self.watchers[file_path]["observer"].stop()
            self.watchers[file_path]["observer"].join()
            del self.watchers[file_path]

    def watcher_status(self, file_path: str):
        """Shows the watcher status. False = off, True = on
        """
        if file_path not in self.watchers:
            logging.warning("File isn't being watched, nothing to do.")
            return False

        return self.watchers[file_path]["observer"].is_alive()

    def has_changed(self, file_path: str, checksum: str):
        """Compares checksum in a file being watched
        Args:
          file_path (str): file path
          checksum: checksum for comparison 
        """
        if file_path not in self.watchers:
            logging.warning("File isn't being watched, nothing to do.")
            return None
        if self.watchers[file_path]['watcher'].checksum is None:
            logging.warning("Checksum can not be found")
            return None

        return self.watchers[file_path]['watcher'].checksum != checksum
