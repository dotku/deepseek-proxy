import os
from typing import Dict, Any
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env.local file with override
print("Loading environment from .env.local...")
load_dotenv(override=True)  # First load any .env file
load_dotenv('.env.local', override=True)  # Then override with .env.local

# Print loaded environment variables for debugging
print(f"DEEPSEEK_API_URL: {os.getenv('DEEPSEEK_API_URL')}")
print(f"DEEPSEEK_API_KEY: {os.getenv('DEEPSEEK_API_KEY', '')[:8]}...")  # Only print first 8 chars of key for security

app = FastAPI(title="DeepSeek Proxy")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load DEEPSEEK_API_KEY from the environment variables
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable not set")

if not DEEPSEEK_API_URL:
    raise ValueError("DEEPSEEK_API_URL environment variable not set")

async def forward_to_deepseek_streaming(data: Dict[str, Any], uri: str):
    """Forward request to DeepSeek API with streaming support."""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # Construct the full URL by appending the URI path
    full_url = f"{DEEPSEEK_API_URL.rstrip('/')}/{uri}"
    
    # Debug prints
    print("Request data:", data)
    print("Headers:", headers)
    print("URL:", full_url)
    print("URI:", uri)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            full_url,
            json=data,
            headers=headers,
            timeout=60.0
        )
        response.raise_for_status()
        return response

@app.get("/ping")
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "pong"}

@app.api_route("/{uri:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, uri: str):
    """Generic proxy endpoint that forwards requests to DeepSeek API."""
    try:
        # Get request body if any
        data = {}
        if request.method in ["POST", "PUT", "PATCH"]:
            data = await request.json()

        # Forward request to DeepSeek
        deepseek_response = await forward_to_deepseek_streaming(data, uri)

        # Stream the response back
        async def generate():
            async for chunk in deepseek_response.aiter_bytes():
                if chunk:
                    yield chunk

        return StreamingResponse(
            generate(),
            status_code=deepseek_response.status_code,
            headers={
                "Content-Type": deepseek_response.headers.get("Content-Type", "application/json")
            }
        )

    except httpx.HTTPError as e:
        return JSONResponse(
            status_code=e.response.status_code if hasattr(e, 'response') else 500,
            content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
