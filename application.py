import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from config.settings import CORS_SETTINGS
from services.deepseek import forward_request
from utils.token_manager import apply_token_limits

application = FastAPI()

# Add CORS middleware
application.add_middleware(CORSMiddleware, **CORS_SETTINGS)


@application.get("/")  # Make sure the HTTP method matches your request
async def root():
    return {"message": "Hello World"}


@application.get("/ping")
@application.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@application.post("/{path:path}")
async def proxy_request(request: Request, path: str):
    """
    Proxy requests to DeepSeek API with token limit management.
    """
    data = await request.json()
    data = apply_token_limits(data)

    return StreamingResponse(
        forward_request(data, path), media_type="text/event-stream"
    )
