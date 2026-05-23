from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import os
import secrets

from src.web.routes import router, NotAuthenticatedException

app = FastAPI(title="Auto-Fanpage AI Dashboard")

# Generate a random secret key for sessions if not provided
session_secret = os.getenv("SESSION_SECRET", secrets.token_hex(32))
app.add_middleware(SessionMiddleware, secret_key=session_secret)

@app.exception_handler(NotAuthenticatedException)
async def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    return RedirectResponse(url='/login')

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routes
app.include_router(router)
