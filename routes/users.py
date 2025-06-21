from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import get_password_hash, fake_users_db

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: str

@router.post("/users/", status_code=201)
def create_user(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    hashed_password = get_password_hash(user.password)
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "disabled": False,
    }
    return {"msg": "Usuario creado exitosamente"}
