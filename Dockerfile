FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rename .env.local to .env for production
RUN if [ -f .env.local ]; then cp .env.local .env; fi

ENV PORT=8080
EXPOSE 8080

# Use uvicorn to run the FastAPI application
CMD ["uvicorn", "deepseek_proxy:app", "--host", "0.0.0.0", "--port", "8080"]
