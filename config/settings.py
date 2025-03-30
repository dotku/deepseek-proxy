import os
from dotenv import load_dotenv

# Load environment variables from .env files
load_dotenv(override=True)  # First load any .env file
load_dotenv('.env.local', override=True)  # Then override with .env.local

# API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "dummy_key_for_dev")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")

# Only validate in production
if os.getenv("ENV") == "production":
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "dummy_key_for_dev":
        raise ValueError("DEEPSEEK_API_KEY environment variable not set in production")
    if not DEEPSEEK_API_URL:
        raise ValueError("DEEPSEEK_API_URL environment variable not set in production")

# CORS Settings
CORS_SETTINGS = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
