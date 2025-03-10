from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pathlib import Path
import json

from app.file_watcher import FileWatcherManager
from app.ws_manager import WebSocketManager, WebSocketHandler
from app.utils import fetch_file_data

router = APIRouter()
watcher_manager = FileWatcherManager()

# TODO fetch the proposal path here, rn hard codded
proposal_path = Path('/Users/teodoro/')
file_path = str(proposal_path / 'context.py')


def get_watcher_manager():
    return watcher_manager


@router.get("/health")
async def health_check():
    return JSONResponse(content={"response": "OK"})


@router.get("/{proposal}/{file_name}/current")
async def get_file(proposal: str):
    data = await fetch_file_data(file_path, with_content=True)
    return JSONResponse(data)


@router.post("/{proposal}/{file_name}/watcher/start")
async def start_watcher(proposal: str,
                        file_name: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

    async def on_change(a, b, c):
        """Anything else we need can go here"""
        print("triggered", a, b, c)

    await watcher_manager.start_watcher(
        file_path=file_path,
        on_change=on_change
    )

    return JSONResponse(content={"message": "Watcher started",
                                 "file_path": file_path})


@router.post("/{proposal}/{file_name}/watcher/stop")
async def stop_watcher(proposal: str,
                        file_name: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

    watcher_manager.stop_watcher(file_path=file_path)

    return JSONResponse(content={"message": "Watcher stopped",
                                 "file_path": file_path})


@router.get("/{proposal}/{file_name}/watcher/status")
async def start_watcher(proposal: str,
                        file_name: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

    status = watcher_manager.watcher_status(file_path)
    return JSONResponse(content={"status": status,
                                 "file_path": file_path})


@router.get("/has_changed/{proposal}/{file_name}/{checksum}")
async def start_watcher(proposal: str,
                        file_name: str,
                        checksum: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

    has_changed = watcher_manager.has_changed(file_path, checksum)
    return JSONResponse(content={"has_changed": has_changed,
                                 "file_path": file_path})

#ws_manager = WebSocketManager()

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     """Websocket route for file watching updates

#     Event types:
#     "ping" -> Heartbeat message - Server responds "pong"
#     ""

#     Args:
#         websocket (WebSocket): _description_
#     """
#     print('connecting')
#     await ws_manager.connect(websocket)
#     handler = WebSocketHandler(websocket, ws_manager, watcher_manager)

#     try:
#         while True:
#             data = await websocket.receive_json()
#             event = data.get("event")
#             if not event:
#                 await websocket.send_text("Malformed JSON")
#             else:
#                 await handler.handle_event(event, data)

#     except WebSocketDisconnect:
#         await ws_manager.disconnect(websocket)
