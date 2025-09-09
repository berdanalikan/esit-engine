#!/bin/bash

# Start the FastAPI application with gunicorn
exec gunicorn app:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT --timeout 120 --keep-alive 2
