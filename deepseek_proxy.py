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

# Default token limits for different models
DEFAULT_TOKEN_LIMITS = {
    "deepseek-chat": 4096,  # Adjust these values based on actual model limits
    "deepseek-coder": 8192,
    "default": 512
}

# Default system message for friendly Chinese responses
DEFAULT_SYSTEM_MESSAGE = {
    "role": "system",
    "content": """你是一个友善、活泼、专业的AI助手。在回应用户时：
1. 使用亲切自然的口吻，适当使用表情符号
2. 保持积极正面的态度
3. 回答要简洁明了
4. 适当使用"～"等符号增加语气的轻松感
5. 每次对话都要像第一次见面一样热情，但不要过度热情
6. 使用"我"而不是"AI助手"来指代自己"""
}

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

def apply_token_limits(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply token limits to the request data."""
    if not isinstance(data, dict):
        return data

    # Only process chat completion requests
    if "messages" not in data:
        return data
        
    # Add default system message if no system message exists
    if not any(msg.get("role") == "system" for msg in data["messages"]):
        data["messages"].insert(0, DEFAULT_SYSTEM_MESSAGE)

    # Get the model name or use default
    model_name = data.get("model", "default").lower()
    
    # If max_tokens is not specified, add it with default limit
    if "max_tokens" not in data:
        default_limit = DEFAULT_TOKEN_LIMITS.get(model_name, DEFAULT_TOKEN_LIMITS["default"])
        
        # Calculate approximate input tokens (rough estimation)
        input_tokens = sum(len(msg.get("content", "")) // 4 for msg in data["messages"])
        
        # Set max_tokens to default limit minus input tokens
        data["max_tokens"] = max(1, min(default_limit - input_tokens, default_limit))
        print(f"Setting max_tokens to {data['max_tokens']} for model {model_name}")
    
    return data

async def forward_to_deepseek_streaming(data: Dict[str, Any], uri: str):
    """Forward request to DeepSeek API with streaming support."""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # Apply token limits to the request data
    data = apply_token_limits(data)

    # print the data, but hide the api key
    # print("Request data:", {**data, "api_key": "..."})

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
