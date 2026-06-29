from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel
from pathlib import Path
from typing import List
import asyncio
import os

from .file_explorer import DirectoryEntry, FileExplorerService
from .project import Project, project_service
from .websocket.routes import router as websocket_router
from .websocket.manager import websocket_manager
from .sc_backend.routes import router as sc_backend_router, init_sc_service
from .init.routes import router as init_router
from .runtime.routes import router as runtime_router
from .runtime.service import runtime_service
from .ableton.routes import router as ableton_router
from .ableton.service import ableton_service
from .websocket.osc_clock_server import osc_server
from ..logger import get_main_logger
from ..__about__ import __version__

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # --- startup ---
    from .websocket.runtime_state import runtime_state
    await runtime_state.start()

    init_sc_service(websocket_manager)
    loop = asyncio.get_event_loop()
    runtime_service.init(websocket_manager, loop)
    osc_server.init(loop)
    osc_server.register_builtin_handlers()
    osc_server.start()

    from .sc_backend.routes import sc_service as _sc_service
    if _sc_service is not None:
        audio_device_index = _sc_service.get_audio_device_setting()
        asyncio.create_task(_sc_service.start_backend(audio_device_index))

    runtime_service.start()

    if ableton_service.is_startup_enabled():
        import time
        time.sleep(2)  # give the runtime a moment to finish importing
        ableton_service.start()

    yield

    # --- shutdown ---
    await runtime_state.stop()
    osc_server.stop()


app = FastAPI(title="Renardo WebServer Fresh", version=__version__, lifespan=lifespan)

# Static files configuration
def get_static_folder() -> Path:
    """Find the static folder for serving frontend files."""
    logger = get_main_logger()

    # Check for RENARDO_STATIC_FOLDER env var (set by Electron)
    env_static = os.environ.get("RENARDO_STATIC_FOLDER")
    logger.info(f"RENARDO_STATIC_FOLDER env: {env_static}")
    if env_static:
        env_path = Path(env_static)
        if env_path.exists() and (env_path / "index.html").exists():
            logger.info(f"Using static folder from env: {env_path}")
            return env_path
        else:
            logger.warning(f"Static folder from env does not exist or missing index.html: {env_path}")

    # Try to find webclient/dist relative to this file
    current_file = Path(__file__).resolve()
    logger.info(f"Current file: {current_file}")

    # Go up to find project root (where pyproject.toml is)
    for parent in current_file.parents:
        dist_path = parent / "webclient" / "dist"
        if dist_path.exists() and (dist_path / "index.html").exists():
            logger.info(f"Found static folder at: {dist_path}")
            return dist_path
        # Also check for static folder in webserver (packaged app)
        static_path = parent / "webserver" / "static"
        if static_path.exists() and (static_path / "index.html").exists():
            logger.info(f"Found static folder at: {static_path}")
            return static_path

    logger.warning("No static folder found")
    return None

STATIC_FOLDER = get_static_folder()

# Include WebSocket routes
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])

# Include SC Backend routes
app.include_router(sc_backend_router)

# Include Init routes
app.include_router(init_router)

# Include Runtime routes
app.include_router(runtime_router)

# Include Ableton routes
app.include_router(ableton_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:54321",
        "http://127.0.0.1:54321",
        "ws://localhost:54321",
        "ws://127.0.0.1:54321",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExecuteCodeRequest(BaseModel):
    code: str


class ExecuteCodeResponse(BaseModel):
    success: bool
    message: str
    output: str | None = None


@app.post("/execute", response_model=ExecuteCodeResponse)
async def execute_code(request: ExecuteCodeRequest):
    """Execute Python code by sending it to the Renardo runtime subprocess."""
    await websocket_manager.send_console_message(
        "info", "runtime", f">>> {request.code}"
    )

    sent = runtime_service.execute_code(request.code)

    if sent:
        return ExecuteCodeResponse(
            success=True,
            message="Code sent to runtime",
            output=None,
        )
    else:
        msg = "Runtime subprocess is not running — start it from the Runtime panel"
        await websocket_manager.send_console_message("error", "runtime", msg)
        return ExecuteCodeResponse(
            success=False,
            message=msg,
            output=None,
        )


@app.get("/")
async def root():
    """Serve index.html for SPA or return API message"""
    if STATIC_FOLDER and (STATIC_FOLDER / "index.html").exists():
        return FileResponse(STATIC_FOLDER / "index.html")
    return {"message": "Renardo WebServer Fresh is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}




@app.get("/api/clock/state")
async def clock_get_state():
    """Get current clock state from runtime (if loaded)"""
    from .websocket.runtime_state import runtime_state
    return await runtime_state.get_state()


# Music Examples endpoints
@app.get("/api/music-examples/files")
async def get_music_example_files():
    """Get list of music example files"""
    try:
        from ..tutorial import get_music_examples_path

        music_examples_path = get_music_examples_path()
        files = []

        if music_examples_path.exists():
            for file_path in music_examples_path.glob("*.py"):
                files.append(
                    {
                        "name": file_path.name,
                        "path": str(file_path),
                        "url": f"/api/music-examples/files/{file_path.name}",
                    }
                )
            files.sort(key=lambda x: x["name"])

        return {"success": True, "files": files}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading music example files: {str(e)}"
        )


@app.get("/api/music-examples/files/{filename}")
async def get_music_example_file(filename: str):
    """Get content of a specific music example file"""
    try:
        from ..tutorial import get_music_examples_path

        # Security: ensure we're staying within music_examples directory
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        music_examples_path = get_music_examples_path()
        file_path = music_examples_path / filename

        # Security: ensure file exists and is within music_examples directory
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Music example file not found")

        # Additional security check
        try:
            file_path.resolve().relative_to(music_examples_path.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Access denied")

        # Read and return file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return PlainTextResponse(content=content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading music example file: {str(e)}"
        )


# Tutorial endpoints
@app.get("/api/tutorial/files")
async def get_tutorial_files(lang: str | None = None):
    """Get list of tutorial files, optionally filtered by language"""
    try:
        from ..tutorial import get_tutorial_path, get_available_languages

        if lang:
            # Return files for specific language
            tutorial_path = get_tutorial_path(lang)
            files = []

            if tutorial_path.exists():
                for file_path in tutorial_path.glob("*.py"):
                    files.append(
                        {
                            "name": file_path.name,
                            "path": str(file_path),
                            "url": f"/api/tutorial/files/{lang}/{file_path.name}",
                        }
                    )
                files.sort(key=lambda x: x["name"])

            return {"success": True, "languages": {lang: files}}
        else:
            # Return all languages and their files
            languages = {}
            available_langs = get_available_languages()

            for language in available_langs:
                tutorial_path = get_tutorial_path(language)
                files = []

                if tutorial_path.exists():
                    for file_path in tutorial_path.glob("*.py"):
                        files.append(
                            {
                                "name": file_path.name,
                                "path": str(file_path),
                                "url": f"/api/tutorial/files/{language}/{file_path.name}",
                            }
                        )
                    files.sort(key=lambda x: x["name"])

                languages[language] = files

            return {"success": True, "languages": languages}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading tutorial files: {str(e)}"
        )


@app.get("/api/tutorial/files/{lang}/{filename}")
async def get_tutorial_file(lang: str, filename: str):
    """Get content of a specific tutorial file"""
    try:
        from ..tutorial import get_tutorial_path

        # Security: ensure we're staying within tutorial directory
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        tutorial_path = get_tutorial_path(lang)
        file_path = tutorial_path / filename

        # Security: ensure file exists and is within tutorial directory
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Tutorial file not found")

        # Additional security check
        try:
            file_path.resolve().relative_to(tutorial_path.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Access denied")

        # Read and return file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return PlainTextResponse(content=content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading tutorial file: {str(e)}"
        )


# File Explorer endpoints
@app.get("/api/file-explorer/list", response_model=List[DirectoryEntry])
async def list_directory(path: str = "/"):
    """List contents of a directory"""
    try:
        file_explorer = FileExplorerService()
        entries = file_explorer.list_directory(path)
        return entries
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing directory: {str(e)}"
        )


@app.get("/api/file-explorer/home")
async def get_home_directory():
    """Get user's home directory path"""
    try:
        file_explorer = FileExplorerService()
        home_path = file_explorer.get_home_directory()
        return {"path": home_path}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting home directory: {str(e)}"
        )


@app.get("/api/file-explorer/parent")
async def get_parent_directory(path: str):
    """Get parent directory of a path"""
    try:
        file_explorer = FileExplorerService()
        parent_path = file_explorer.get_parent_directory(path)
        return {"path": parent_path}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting parent directory: {str(e)}"
        )


@app.get("/api/file-explorer/read")
async def read_file(path: str):
    """Read content of a file"""
    try:
        file_path = Path(path).resolve()

        # Security: ensure file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Security: ensure it's a file, not a directory
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")

        # Read and return file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {"content": content, "path": str(file_path)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading file: {str(e)}"
        )


# User Directory endpoints
@app.get("/api/user-directory")
async def get_user_directory():
    """Get current user directory path"""
    try:
        from ..settings_manager import settings
        user_dir = settings.get_renardo_user_dir()
        return {"success": True, "path": str(user_dir)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting user directory: {str(e)}"
        )


@app.get("/api/user-directory/list")
async def list_user_directory(subpath: str = ""):
    """List contents of user directory or subdirectory"""
    try:
        from ..settings_manager import settings
        user_dir = settings.get_renardo_user_dir()

        # Construct full path
        if subpath:
            full_path = (user_dir / subpath).resolve()
        else:
            full_path = user_dir.resolve()

        # Security: ensure path is within user directory
        try:
            full_path.relative_to(user_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Access denied")

        # Check if path exists
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        # List directory contents
        file_explorer = FileExplorerService()
        entries = file_explorer.list_directory(str(full_path))

        return {"success": True, "entries": entries, "current_path": str(full_path)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing user directory: {str(e)}"
        )


class SetUserDirectoryRequest(BaseModel):
    path: str


@app.post("/api/user-directory/set")
async def set_user_directory(request: SetUserDirectoryRequest):
    """Set new user directory path"""
    try:
        from ..settings_manager import settings
        new_path = Path(request.path)

        # Validate path
        if not new_path.is_absolute():
            raise HTTPException(status_code=400, detail="Path must be absolute")

        # Set the new user directory
        success = settings.set_user_dir_path(new_path)

        if success:
            return {"success": True, "path": str(new_path)}
        else:
            raise HTTPException(status_code=500, detail="Failed to set user directory")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error setting user directory: {str(e)}"
        )


# Project endpoints
class OpenProjectRequest(BaseModel):
    root_path: str


class SaveFileRequest(BaseModel):
    file_path: str
    content: str


@app.post("/api/project/open")
async def open_project(request: OpenProjectRequest):
    """Open a project directory"""
    try:
        project = project_service.open_project(request.root_path)
        return {"success": True, "project": {"root_path": str(project.root_path)}}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error opening project: {str(e)}")


@app.get("/api/project/current")
async def get_current_project():
    """Get current project information"""
    try:
        if project_service.current_project:
            return {
                "success": True,
                "project": {
                    "root_path": str(project_service.current_project.root_path)
                },
            }
        else:
            return {"success": False, "project": None}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting current project: {str(e)}"
        )


@app.post("/api/project/save-file")
async def save_file(request: SaveFileRequest):
    """Save a file to the current project"""
    try:
        if not project_service.current_project:
            raise HTTPException(status_code=400, detail="No project is open")

        project_service.write_file(request.file_path, request.content)
        return {"success": True, "message": f"File saved: {request.file_path}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


# Frontend state persistence
@app.get("/api/frontend-state")
async def get_frontend_state():
    """Return persisted frontend state from user_dir/frontend_state.json"""
    import json
    from ..settings_manager import settings
    state_file = settings.get_renardo_user_dir() / "frontend_state.json"
    if not state_file.exists():
        return {}
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading frontend state: {e}")


class SaveFrontendStateRequest(BaseModel):
    state: dict


@app.post("/api/frontend-state")
async def save_frontend_state(request: SaveFrontendStateRequest):
    """Persist frontend state to user_dir/frontend_state.json"""
    import json
    from ..settings_manager import settings
    user_dir = settings.get_renardo_user_dir()
    try:
        user_dir.mkdir(parents=True, exist_ok=True)
        with open(user_dir / "frontend_state.json", "w", encoding="utf-8") as f:
            json.dump(request.state, f, indent=2, ensure_ascii=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving frontend state: {e}")


# Frontend logging endpoint
class FrontendLogRequest(BaseModel):
    level: str
    message: str


@app.post("/api/frontend_logs")
async def frontend_logs(request: FrontendLogRequest):
    """Receive logs from frontend"""
    logger = get_main_logger()

    level = request.level.upper()
    message = f"[FRONTEND] {request.message}"

    if level == "DEBUG":
        logger.debug(message)
    elif level == "INFO":
        logger.info(message)
    elif level == "WARN":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.info(message)

    return {"success": True}


# SPA catch-all route - must be at the end
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve static files or index.html for SPA routing"""
    if not STATIC_FOLDER:
        raise HTTPException(status_code=404, detail="Static files not configured")

    # Try to serve the exact file
    file_path = STATIC_FOLDER / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)

    # For SPA routing, return index.html for non-file paths
    index_path = STATIC_FOLDER / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    raise HTTPException(status_code=404, detail="File not found")
