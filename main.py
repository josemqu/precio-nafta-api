from fastapi import FastAPI
from routes import route, token, users

app = FastAPI()

app.include_router(route.router)
app.include_router(token.router)
app.include_router(users.router)
