import os
import hashlib
import logging
import asyncio
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from typing import Callable, Dict, Optional

from app.utils import fetch_file_data

# Logging
logger = logging.getLogger("uvicorn")


class FileWatcher(FileSystemEventHandler):
    """
    Watches an specific file
    """

    def __init__(self, file_path: str, loop: asyncio.AbstractEventLoop, on_file_change: Optional[Callable] = None):
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
            current_checksum = await self.calculate_checksum()

            if current_checksum != self.checksum:
                self.checksum = current_checksum
                self.last_modified = os.path.getmtime(self.file_path)
                if self.on_file_change is not None:
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
            clients: list of clients
          }
        }
        """
        self.watchers: Dict[str, Dict[str,int | Observer | FileWatcher | float | list]] = {}
        self.loop = asyncio.get_event_loop()
        self.timeout=10
        self.loop.create_task(self.cleanup_inactive_watchers())

    async def register_client(self, file_path: str, client_ip: str, on_change: Optional[Callable] = None):
        """Starts watcher for a given file and proposal if watcher doesn't
        exist. If it does, adds the client to the client list.
        Every time this function is called, last_activity is updated

        Args:
            file_path (str): File path
            client_ip (str): Client IP 
            on_change (Callable): Callback for changes
        """
        if file_path not in self.watchers:
            self.watchers[file_path] = {}
        elif client_ip not in self.watchers[file_path]["clients"]:
            self.watchers[file_path]["count"] += 1
            self.watchers[file_path]["last_activity"] = time.time()
            self.watchers[file_path]["clients"].append(client_ip)
            logger.info(f"Client added to an watched file path: {file_path}")
            return
        else:
            logger.info(f"Client {client_ip} already watching file path: {file_path}")
            self.watchers[file_path]["last_activity"] = time.time()
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
        self.watchers[file_path]["clients"]= [client_ip]
        self.watchers[file_path]["observer"].start()
        self.watchers[file_path]["last_activity"] = time.time()
        
        logger.info(f"Watcher's list updated: {self.watchers}")
        
    async def cleanup_inactive_watchers(self):
        """Periodically checks for inactive watchers and stops them."""
        logger.info("Started clean up checks for FileWatcherManager")
        while True:
            await asyncio.sleep(10)
            current_time = time.time()
            
            inactive_files = [
                file_path for file_path, data in self.watchers.items()
                if (current_time - data["last_activity"]) > self.timeout
            ]
            
            if inactive_files:
                logger.info(f"Stopping watcher for {inactive_files} due to inactivity.")
            
            await asyncio.gather(*(self.stop_watcher(file) for file in inactive_files))

    async def stop_watcher(self, file_path: str):
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
            return False

        return self.watchers[file_path]["observer"].is_alive()
    
    async def has_new_checksum(self, file_path: str, checksum: str, client_ip: str):
        """Compares checksum in a file being watched
        Args:
          file_path (str): file path
          checksum: checksum for comparison 
        """
        await self.register_client(file_path, client_ip)
        
        if self.watchers[file_path]['watcher'].checksum is None:
            logger.warning("Checksum can not be found")
            return None
        
        logger.info(self.watchers[file_path]['watcher'].checksum != checksum)

        return self.watchers[file_path]['watcher'].checksum != checksum