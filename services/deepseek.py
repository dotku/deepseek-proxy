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
    
    timeout_settings = httpx.Timeout(
        connect=10.0,  # connection timeout
        read=300.0,    # read timeout - longer for streaming responses
        write=10.0,    # write timeout
        pool=10.0      # pool timeout
    )
    
    try:
        async with httpx.AsyncClient(timeout=timeout_settings) as client:
            async with client.stream('POST', full_url, json=data, headers=headers) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
    except httpx.TimeoutException as e:
        raise RuntimeError(f"Timeout while connecting to DeepSeek API: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP error from DeepSeek API: {e.response.status_code} - {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error forwarding request to DeepSeek API: {str(e)}")

async def forward_request_sync(data: Dict[str, Any], uri: str) -> Dict[str, Any]:
    """
    Forward request to DeepSeek API and return the complete response.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_url = f"{DEEPSEEK_API_URL.rstrip('/')}/{uri}"
    
    timeout_settings = httpx.Timeout(
        connect=10.0,
        read=60.0,     # 非流式請求可以使用較短的超時
        write=10.0,
        pool=10.0
    )
    
    try:
        async with httpx.AsyncClient(timeout=timeout_settings) as client:
            response = await client.post(full_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException as e:
        raise RuntimeError(f"Timeout while connecting to DeepSeek API: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP error from DeepSeek API: {e.response.status_code} - {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error forwarding request to DeepSeek API: {str(e)}")
