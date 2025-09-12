# Use lightweight Python base
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# System deps for PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install additional packages separately to avoid conflicts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* || true

# Copy requirements first for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create directories for data and feedback
ENV FEEDBACK_DIR=/data
RUN mkdir -p /data /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Expose port
EXPOSE 8080

# Start with python (app.py starts uvicorn)
ENV PORT=8080
CMD ["python", "app.py"]

