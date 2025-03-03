# The **FileWatcher** System for DAMNIT!

### Overview

![image](https://github.com/user-attachments/assets/29eefe8d-35d1-462b-ba5e-4b3a25d3b97c)


DAMNIT will have to watch files for the context editor feature (read-only MVP) and perhaps in the future to update the log info. I'm using **checksums**  to monitor file changes efficiently. Plus, it's designed for **web polling** now. Still it can be plugged into something else like **webhooks** later. I tried to make it as agnostic as I could. 

### The  **FileWatcherManager** 

The **FileWatcherManager** is where all the action happens. It keeps track of which files are being watched and manages both the **Observer** and **FileWatcher** instances:

- **Observer**: Listens for file system events
- **FileWatcher**: Tracks file checksum and data

That's the inferface between the API and the file watcher layer. It has quick access to the current checksum for a given file being watched (when we start polling we should avoid ready the file at every request). We keep the observer to stop the watchdog upon request. I still need to improve the stopping of the observer.

The manager structure looks like this:

```python
{"usr/file1.txt": {"observer": ObserverInstance1, "watcher": FileWatcherInstance1},
 "usr/file2.txt": {"observer": ObserverInstance2,"watcher": FileWatcherInstance2}
...
}
```


### Ideas for the Routes

How I'm thinking of designing now:

1. **Health Check** You know what's for

2. **/{proposal}/{file_name}/current**:
    - **Arguments**: `proposal`, `file_name`.
    - **Purpose**: Get the current **checksum**, **last modified** time, and the **content** of the file. 

3. **/{proposal}/{file_name}/watcher/start**:
    - **Arguments**: `proposal`, `file_name`, and a callback (`on_change`).
    - **Purpose**: Start watching a file. The callback is called whenever the file changes. You can plug in any logic there. 
    
4. **/{proposal}/{file_name}/watcher/stop**:
    - **Arguments**: `proposal`, `file_name`.
    - **Purpose**: Stop watching the file when you’re done. E.g. moved to another proposal
    
5. **/{proposal}/{file_name}/watcher/status**:
    - **Arguments**: `proposal`, `file_name`.
    - **Purpose**: Check if the watcher is running or not. Helpful to know if your file is being monitored.
    
6. **/has_changed/{proposal}/{file_name}/{checksum}**:
    - **Arguments**: `proposal`, `file_name`, `checksum`.
    - **Purpose**: Checks an arbitrary checksum with the one of the file being watched. Perhaps we move this to a POST request and the checksum in the body?

---

### How I'm planning to do polling


1. **Client Fetches Current Content**: First, you grab the file’s content and **checksum**. Hold on to that checksum
    
2. **Start Watching the File**: Then, you start the **file watcher**. The system will now monitor the file for changes.
    
3. **Start polling**: The client repeatedly asks "Has this file changed?" by checking the checksum with the `has_changed` route. The system only replies **True** if something has really changed, which saves you from constant file reads. 
    
4. **Update the Interface**: Once the file changes, the client can get the updated content and refresh the UI.
    
5. **Stop polling and Watcher**: Once the update is done, you stop the polling (and optionally, the watcher)
    

---


