import os
import requests
from flask import Flask, request, Response
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load DEEPSEEK_API_KEY from the environment variables
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable not set")

if not DEEPSEEK_API_URL:
    raise ValueError("DEEPSEEK_API_URL environment variable not set")

# Function to forward the request to DeepSeek with streaming
def forward_to_deepseek_streaming(data, uri):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # Construct the full URL by appending the URI path
    full_url = f"{DEEPSEEK_API_URL.rstrip('/')}/{uri}"

    # Using 'stream=True' to enable response streaming
    response = requests.post(full_url, json=data, headers=headers, stream=True)
    return response

# Define the proxy endpoint with streaming
@app.route('/<path:uri>', methods=['POST', 'GET', 'PUT', 'DELETE', 'PATCH'])
def proxy(uri):
    try:
        # Get the request body from the client
        data = request.json if request.is_json else {}

        # Forward the request to DeepSeek and get the streaming response
        deepseek_response = forward_to_deepseek_streaming(data, uri)

        # Stream the response back to the client
        def generate():
            for chunk in deepseek_response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk

        # Create a streaming response using Flask's Response class
        return Response(generate(), content_type=deepseek_response.headers['Content-Type'])

    except Exception as e:
        # Return an error message if something goes wrong
        return {"error": str(e)}, 500

# For Vercel, we need to expose the app
app.debug = True
