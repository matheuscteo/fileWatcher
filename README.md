## API file handler for DAMNIT

![image](https://github.com/user-attachments/assets/3f13484e-e799-43c3-972e-267f82b5a3b6)


The purpose of the file handler
 in the MVP context is:

 - Get file content and metadata
 - Watch the file for changes
 - Notify the user when changes are applied (e.g. via an external editor)

Thinking about this, I recalled an old use-case that requires the same functionality: the log file output. Hence, why not work in a watching engine that's modular and less context-file specific? There's no extra effort on that.

So I considered making a "FileWatcher" engine for our server. The structure looks like this:

We have a `FileWatcher` class that receives a file path and a callback. The callback will be triggered when the file has changed it's content. The callback, being arbitrary, can contain for instance a websocket broadcast capability for context files or a error checker for log watching and so on...
 
A FileWatcherManager class, supposed to be instantiated in a singleton , will orchestrate the watchers by generating, starting, stopping and accessing the status of watchdog `Observers`. I assumed that the singleton approach would be nice so we can keep track of all files being watched. E.g. we want to sure that there are not more than one observer per file. It also stops watchers automatically when a timeout is reached without client activity. 


### Use Case example workflow

**-> The user of proposal 1111 opened the context file editor in the client**

#### Phase 1 - Get content

-> The client sends a request to fetch the file data via the `/file_content?proposal=<PROPOSAL>&file_name=<FILENAME>` route
-> The server looks at the proposal "1111" folder for a "context.py", reads it and send it's content/metadata to the client.
-> Client handles first render of the file

#### Phase 2 - Watching

-> The client pulls periodically with `/has_new_checksum?proposal=<PROPOSAL>&file_name=<FILENAME>&checksum=<CHECKSUM>`
-> The server runs a watchdog observer if not existing for that file.
-> If the chacksum doesn't match the client's, answer `true`
-> Client GETs the whole file again and renders it

#### Phase 3 - Killing

-> User stops pulling
-> Server sees that there is no activity and stops the watcher.

