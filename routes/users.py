from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from auth import get_password_hash
from models.user import User, UserCreate
from config.database import users_collection

router = APIRouter()

@router.post("/users", status_code=201)
def create_user(user: UserCreate):
    try:
        # Verificar si el usuario ya existe
        if users_collection.find_one({"username": user.username}):
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        hashed_password = get_password_hash(user.password)
        user_dict = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_password,
            "disabled": False,
        }
        users_collection.insert_one(user_dict)
        return {"msg": "Usuario creado exitosamente"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
