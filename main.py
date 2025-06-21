"""
main.py

Entry point for the FastAPI application. This file initializes the FastAPI app and includes all route modules for the API.
"""

from fastapi import FastAPI
from routes import route, token, users

app = FastAPI(
    title="Precio Nafta API",
    description="API para consulta de precios de combustibles en estaciones de servicio.",
    version="1.0.0",
    contact={
        "name": "Jose Maria Quintana",
        "email": "mailjmq@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
)
"""The FastAPI application instance for the API."""

# Include all routers with /api/v1 prefix
app.include_router(route.router, prefix="/api/v1")
app.include_router(token.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
