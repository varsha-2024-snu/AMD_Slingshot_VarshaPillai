# python:3.11-slim keeps image under 200MB — faster Cloud Run cold starts
FROM python:3.11-slim

WORKDIR /app

# Install dependencies before copying source — maximises Docker layer cache hits
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Cloud Run injects PORT env var; default to 8080
EXPOSE 8080

# Use uvicorn with 2 workers — sufficient for demo load, stays within 512Mi memory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
