<<<<<<< HEAD
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
=======
from fastapi import APIRouter, Depends
>>>>>>> 0a0a7ba446ff064dcf1d889e022b915c703ba8d3
from fastapi.responses import JSONResponse
from pathlib import Path

from app.file_watcher import FileWatcherManager
<<<<<<< HEAD
from app.ws_manager import WebSocketManager, WebSocketHandler
from app.utils import get_file_meta
=======
from app.utils import get_ctx_file_meta
>>>>>>> 0a0a7ba446ff064dcf1d889e022b915c703ba8d3

router = APIRouter()
watcher_manager = FileWatcherManager()

<<<<<<< HEAD
file_path = '/home/teodoro/DBs/test_DB_6/context.py'


=======
>>>>>>> 0a0a7ba446ff064dcf1d889e022b915c703ba8d3
# TODO fetch the proposal path here
proposal_path = Path('/home/teodoro/DBs/test_DB_6/')

def get_watcher_manager():
  return watcher_manager

@router.get("/health")
async def health_check():
    return JSONResponse(content={"response":"OK"})

@router.get("/{proposal}/{file_type}/current")
<<<<<<< HEAD
async def get_file(proposal: str):

    file_path = proposal_path / 'context.py'
    content, last_modified, checksum = get_file_meta(file_path)

    if content is None:
        return{"error" : "File not found"}

    return{
        "content": content,
        "last_modified": last_modified,
        "checksum": checksum
    }

@router.get("/{proposal}/{file_name}/watcher/start")
async def start_watcher(proposal: str,
                        file_name: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):
  async def on_change(a,b,c):
    print("triggered")

  watcher_manager.start_watcher(
=======
async def get_ctx(proposal: str):

    ctx_file_path = proposal_path / 'context.py'
    ctx_content, ctx_last_modified, ctx_checksum = get_ctx_file_meta(ctx_file_path)

    if ctx_content is None:
        return{"error" : "File not found"}

    return{
        "content": ctx_content,
        "last_modified": ctx_last_modified,
        "checksum": ctx_checksum
    }

@router.get("/{proposal}/{file_type}/watcher/start")
async def start_watcher(proposal: str,
                        file_type: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):
  file_path = proposal_path / 'context.py'
  def on_change(a,b,c):
    print("triggered")

  watcher_manager.start_watcher(
    proposal=proposal,
    file_type=file_type,
>>>>>>> 0a0a7ba446ff064dcf1d889e022b915c703ba8d3
    file_path=file_path,
    on_change=on_change
  )

  return JSONResponse(content={"message": "Watcher started",
<<<<<<< HEAD
                               "file_path":file_path})

@router.get("/{proposal}/{file_name}/watcher/stop")
async def start_watcher(proposal: str,
                        file_name: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

  watcher_manager.stop_watcher(file_path=file_path)

  return JSONResponse(content={"message": "Watcher stopped",
                               "file_path":file_path})

@router.get("/{proposal}/{file_name}/watcher/status")
async def start_watcher(proposal: str,
                        file_name: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

  status = watcher_manager.watcher_status(file_path)
  return JSONResponse(content={"status": status,
                               "file_path":file_path})

ws_manager = WebSocketManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  """Websocket route for file watching updates

  Event types:
  "ping" -> Heartbeat message - Server responds "pong"
  ""

  Args:
      websocket (WebSocket): _description_
  """
  print('connecting')
  await ws_manager.connect(websocket)
  handler = WebSocketHandler(websocket, ws_manager, watcher_manager)

  try:
    while True:
      data = await websocket.receive_json()
      event = data.get("event")
      if not event:
        await websocket.send_text("Malformed JSON")
      else:
        await handler.handle_event(event, data)

  except WebSocketDisconnect:
    await ws_manager.disconnect(websocket)
=======
                               "proposal":proposal,
                               "file_type":file_type})

@router.get("/{proposal}/{file_type}/watcher/stop")
async def start_watcher(proposal: str,
                        file_type: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

  watcher_manager.stop_watcher(
    proposal=proposal,
    file_type=file_type)

  return JSONResponse(content={"message": "Watcher stopped",
                               "proposal":proposal,
                               "file_type":file_type})

@router.get("/{proposal}/{file_type}/watcher/status")
async def start_watcher(proposal: str,
                        file_type: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

  status = watcher_manager.watcher_status(proposal, file_type)
  return JSONResponse(content={"status": status,
                               "proposal":proposal,
                               "file_type":file_type})
>>>>>>> 0a0a7ba446ff064dcf1d889e022b915c703ba8d3

