# DeepSeek Proxy

A proxy for DeepSeek API with token management and friendly Chinese responses.

## Features

- Token limit management
- Friendly Chinese responses
- CORS support
- Health check endpoints
- Docker support

## Usage

### Local Development

```bash
python3 deepseek_proxy.py
```

### Docker

1. Build the image:

```bash
docker build -t deepseek-proxy .
```

2. Run the container:

```bash
docker run -d \
  -p 8080:8080 \
  -e DEEPSEEK_API_KEY=your_api_key \
  -e DEEPSEEK_API_URL=your_api_url \
  --name deepseek-proxy \
  deepseek-proxy
```

The proxy will be available at `http://localhost:8080`.

## Environment Variables

- `DEEPSEEK_API_KEY`: your DeepSeek API key
- `DEEPSEEK_API_URL`: your DeepSeek API url

## Health Check

- `/ping` or `/health`: Returns service status
- Response: `{"status": "ok", "message": "pong"}`

## License

MIT
