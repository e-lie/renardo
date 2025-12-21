from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from pathlib import Path
import os

app = FastAPI(title="Renardo WebServer Fresh", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
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

        result = execute(request.code, verbose=True)

        return ExecuteCodeResponse(
            success=True,
            message="Code executed successfully",
            output=str(result) if result else None,
        )
    except Exception as e:
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
