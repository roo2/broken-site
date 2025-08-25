import logging
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .schemas import DiagnoseRequest, DiagnosticReport, UserFriendlyReport
from pydantic import BaseModel
from .offline import run_offline_diagnosis
from .agent import run_agent_streaming
from .user_friendly import convert_to_user_friendly
from .config import settings
import json

# Configure logging
import os
log_level = os.getenv("LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.ERROR),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, log_level, logging.ERROR))

app = FastAPI(title="BrokenSite", version="0.1.0")

# Mount static files for the frontend
frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")

@app.get("/")
async def root():
    """Serve the frontend index.html"""
    # Try multiple possible paths for the frontend
    possible_paths = [
        Path(__file__).parent.parent.parent / "frontend" / "dist" / "index.html",
        Path(__file__).parent.parent.parent / "frontend" / "dist" / "index.html",
        Path.cwd() / "frontend" / "dist" / "index.html",
        Path.cwd() / "dist" / "index.html"
    ]
    
    logger.info(f"Looking for frontend in possible paths:")
    for path in possible_paths:
        logger.info(f"  - {path} (exists: {path.exists()})")
    
    for frontend_path in possible_paths:
        if frontend_path.exists():
            logger.info(f"Serving frontend from: {frontend_path}")
            return FileResponse(str(frontend_path))
    
    # If no frontend found, check what directories exist
    logger.warning("Frontend not found in any expected location")
    logger.info(f"Current working directory: {Path.cwd()}")
    logger.info(f"Current directory contents: {list(Path.cwd().iterdir())}")
    
    # Check if frontend directory exists
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    if frontend_dir.exists():
        logger.info(f"Frontend directory exists, contents: {list(frontend_dir.iterdir())}")
        dist_dir = frontend_dir / "dist"
        if dist_dir.exists():
            logger.info(f"Dist directory exists, contents: {list(dist_dir.iterdir())}")
    
    return {"message": "Frontend not built. Please run 'npm run build' in the frontend directory."}

@app.get("/healthz")
def health():
    return {"ok": True}

@app.get("/favicon.svg")
async def favicon():
    """Serve the favicon"""
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
    favicon_path = frontend_path / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    else:
        # Return a simple SVG if the file doesn't exist
        return {"message": "Icon not found"}

@app.get("/api/test")
def test_api():
    return {"message": "API is working!", "status": "ok"}








@app.post("/api/diagnose/stream")
def diagnose_streaming(req: DiagnoseRequest, mode: str = "openai"):
    """Stream diagnosis updates in real-time using Server-Sent Events.
    Provides live updates as the AI agent thinks and uses tools.
    """
    logger.info(f"Starting streaming diagnosis for target: {req.target} with mode: {mode}")
    
    if mode != "openai":
        # For offline mode, return a simple stream with the result
        def offline_stream():
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting offline diagnosis...'})}\n\n"
            
            try:
                result = run_offline_diagnosis(req.target)
                yield f"data: {json.dumps({'type': 'status', 'message': 'Offline diagnosis completed'})}\n\n"
                yield f"data: {json.dumps({'type': 'result', 'data': result.dict()})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            offline_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
    
    # For OpenAI mode, use the streaming agent
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is required for streaming diagnosis")
    
    def streaming_response():
        try:
            for update in run_agent_streaming(req.target):
                yield f"data: {json.dumps(update)}\n\n"
        except Exception as e:
            logger.error(f"Error in streaming diagnosis: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        streaming_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )
