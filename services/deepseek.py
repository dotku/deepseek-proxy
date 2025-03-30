from typing import Dict, Any, AsyncGenerator
import httpx
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

async def forward_request(data: Dict[str, Any], uri: str) -> AsyncGenerator[bytes, None]:
    """
    Forward request to DeepSeek API and stream the response.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_url = f"{DEEPSEEK_API_URL.rstrip('/')}/{uri}"
    
    async with httpx.AsyncClient() as client:
        async with client.stream('POST', full_url, json=data, headers=headers) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                yield chunk
