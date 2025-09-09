# Use lightweight Python base
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create feedback dir and allow override at runtime
ENV FEEDBACK_DIR=/data
RUN mkdir -p /data

# Expose port
EXPOSE 8080

# Start with python (app.py starts uvicorn)
ENV PORT=8080
CMD ["python", "app.py"]

