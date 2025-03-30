import os
import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env.local file with override
print("Loading environment from .env.local...")
load_dotenv(override=True)  # First load any .env file
load_dotenv('.env.local', override=True)  # Then override with .env.local

# Print loaded environment variables for debugging
print(f"DEEPSEEK_API_URL: {os.getenv('DEEPSEEK_API_URL')}")
print(f"DEEPSEEK_API_KEY: {os.getenv('DEEPSEEK_API_KEY', '')[:8]}...")  # Only print first 8 chars of key for security

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
    # print all post data
    print(data)
    print(headers)
    print(full_url) 
    print(uri)

    # Using 'stream=True' to enable response streaming
    response = requests.post(full_url, json=data, headers=headers, stream=True)
    
    # Check if response is successful
    response.raise_for_status()
    return response

# Define the proxy endpoint with streaming
@app.route('/<path:uri>', methods=['POST', 'GET', 'PUT', 'DELETE', 'PATCH'])
def proxy(uri):
    try:
        # Get the request body from the client
        data = request.json if request.is_json else {}

        # Forward the request to DeepSeek and get the streaming response
        deepseek_response = forward_to_deepseek_streaming(data, uri)

        # If response is not streaming or is JSON, return it directly
        if not deepseek_response.headers.get('Transfer-Encoding') == 'chunked':
            return jsonify(deepseek_response.json()), deepseek_response.status_code

        # For streaming responses, stream the content
        def generate():
            try:
                for chunk in deepseek_response.iter_lines(decode_unicode=True):
                    if chunk:
                        yield chunk + '\n'
            except Exception as e:
                yield str({"error": str(e)})

        # Create a streaming response using Flask's Response class
        content_type = deepseek_response.headers.get('Content-Type', 'application/json')
        return Response(generate(), content_type=content_type, status=deepseek_response.status_code)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), getattr(e.response, 'status_code', 500)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run the Flask app
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
