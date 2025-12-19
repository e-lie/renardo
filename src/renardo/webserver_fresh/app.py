from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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