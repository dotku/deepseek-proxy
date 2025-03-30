FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rename .env.local to .env for production
RUN if [ -f .env.local ]; then cp .env.local .env; fi

ENV PORT=8080
EXPOSE 8080

CMD ["python", "deepseek_proxy.py"]
