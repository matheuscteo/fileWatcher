from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pathlib import Path

from app.file_watcher import FileWatcherManager
from app.utils import get_ctx_file_meta

router = APIRouter()
watcher_manager = FileWatcherManager()

# TODO fetch the proposal path here
proposal_path = Path('/home/teodoro/DBs/test_DB_6/')

def get_watcher_manager():
  return watcher_manager

@router.get("/health")
async def health_check():
    return JSONResponse(content={"response":"OK"})

@router.get("/{proposal}/{file_type}/current")
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
    file_path=file_path,
    on_change=on_change
  )

  return JSONResponse(content={"message": "Watcher started",
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

