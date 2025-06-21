"""
main.py

Entry point for the FastAPI application. This file initializes the FastAPI app and includes all route modules for the API.
"""

from fastapi import FastAPI
from routes import route, token, users

app = FastAPI()
"""The FastAPI application instance for the API."""

app.include_router(route.router)
app.include_router(token.router)
app.include_router(users.router)
