from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from pathlib import Path
from typing import List
import os

from .file_explorer import DirectoryEntry, FileExplorerService
from .project import Project, project_service
from .websocket.routes import router as websocket_router
from .websocket.manager import websocket_manager
from ..logger import get_main_logger

app = FastAPI(title="Renardo WebServer Fresh", version="1.0.0")

# Include WebSocket routes
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "ws://localhost:3001",
        "ws://127.0.0.1:3001",
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
    """Execute Python code in the Renardo runtime"""
    try:
        from ..runtime import execute

        # Send execution start message
        await websocket_manager.send_console_message(
            "info",
            "runtime",
            f"Executing code: {request.code[:100]}{'...' if len(request.code) > 100 else ''}",
        )

        result = execute(request.code, verbose=True)

        # Send execution result
        if result:
            await websocket_manager.send_console_message(
                "info", "runtime", f"Execution result: {str(result)}"
            )

        return ExecuteCodeResponse(
            success=True,
            message="Code executed successfully",
            output=str(result) if result else None,
        )
    except Exception as e:
        # Send error message
        await websocket_manager.send_console_message(
            "error", "runtime", f"Execution error: {str(e)}"
        )

        return ExecuteCodeResponse(
            success=False,
            message=f"Error executing code: {str(e)}",
            output=None,
        )


@app.get("/")
async def root():
    return {"message": "Renardo WebServer Fresh is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


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
