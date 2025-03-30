from typing import Dict, Any

# Default system message for chat
DEFAULT_SYSTEM_MESSAGE: Dict[str, str] = {
    "role": "system",
    "content": "你是一个友好的AI助手，用轻松愉快的语气和用户交流。"
}

# Token limits for different models
DEFAULT_TOKEN_LIMITS: Dict[str, int] = {
    "default": 512,
    "deepseek-chat": 4096,
    "deepseek-coder": 8192
}
