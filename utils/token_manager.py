from typing import Dict, Any
from config.constants import DEFAULT_SYSTEM_MESSAGE, DEFAULT_TOKEN_LIMITS

def apply_token_limits(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply token limits and system message to the request data.
    """
    if not isinstance(data, dict) or "messages" not in data:
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
