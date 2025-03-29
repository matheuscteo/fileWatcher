from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Request
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


@router.get("/file_current")
async def get_file(proposal: str,
                   file_name: str):
    data = await fetch_file_data(file_path, with_content=True)
    return JSONResponse(data)


@router.get("/watcher_status")
async def start_watcher(proposal: str,
                        file_name: str,
                        manager: FileWatcherManager = Depends(get_watcher_manager)):

    status = watcher_manager.watcher_status(file_path)
    return JSONResponse(content={"status": status})


@router.get("/has_new_checksum")
async def has_new_checksum(proposal: str,
                        file_name: str,
                        checksum: str,
                        request: Request,
                        watcher_manager: FileWatcherManager = Depends(get_watcher_manager),
                        ):
    
    client_ip = request.client.host
    has_new_checksum = await watcher_manager.has_new_checksum(file_path, checksum, client_ip)
    return JSONResponse(content={"has_changed": has_new_checksum,
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
