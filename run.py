"""Launcher file to run the FastAPI app from project root.

Usage:
  python run.py         # starts uvicorn with backend.app:app

Prefer running from backend directory:
  python -m uvicorn backend.app:app --reload --port 8000
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
