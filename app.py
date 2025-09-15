"""
ASGI entrypoint for deployment platforms expecting `uvicorn app:app`.
This file simply imports the FastAPI `app` from `src/api/app.py`.
"""

from src.api.app import app  # noqa: F401

if __name__ == "__main__":
    # Optional: allow running locally as `python app.py`
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)


