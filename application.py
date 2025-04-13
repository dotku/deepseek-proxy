from typing import Union, Dict, Any
import json
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from config.settings import CORS_SETTINGS
from services.deepseek import forward_request, forward_request_sync
from utils.token_manager import apply_token_limits

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

application = FastAPI()

# CORS 設置
application.add_middleware(
    CORSMiddleware,
    **CORS_SETTINGS
)

@application.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@application.post("/{path:path}", response_model=None)
async def proxy_request(request: Request, path: str):
    """
    Proxy requests to DeepSeek API with token limit management.
    """
    # 記錄請求路徑和方法
    logger.info(f"Received {request.method} request for path: {path}")
    
    try:
        # 讀取和記錄原始請求內容
        body = await request.body()
        logger.info(f"Request body: {body.decode()}")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid JSON in request body",
                    "detail": str(e),
                    "received": body.decode()
                }
            )
    
        try:
            data = apply_token_limits(data)
            # 檢查是否需要流式輸出
            stream_mode = data.get("stream", True)  # 默認為 True 保持向後兼容
            
            if stream_mode:
                return StreamingResponse(
                    forward_request(data, path), media_type="text/event-stream"
                )
            else:
                # 非流式輸出
                response = await forward_request_sync(data, path)
                return JSONResponse(content=response)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error: {str(e)}"}
        )
