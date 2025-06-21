"""
auth.py

Handles authentication logic for the API, including password hashing, JWT token creation and validation, and user retrieval from the database.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    """Represents a JWT token returned to the client after authentication."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Holds the username data extracted from a JWT token payload."""

    username: Optional[str] = None


class User(BaseModel):
    """Represents a user in the system."""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """Extends User with hashed password for database storage."""

    hashed_password: str


def verify_password(plain_password, hashed_password):
    """
    Verify a plain password against its hashed version.
    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to check against.
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hash a plain password for secure storage.
    Args:
        password (str): The password to hash.
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def get_user_from_db(username: str):
    """
    Retrieve a user from the database by username.
    Args:
        username (str): The username to search for.
    Returns:
        UserInDB | None: The user object if found, else None.
    """
    from config.database import users_collection

    user_dict = users_collection.find_one({"username": username})
    if user_dict:
        return UserInDB(**user_dict)
    return None


def get_user(db, username: str):
    """
    Deprecated: Retrieve a user from a provided dictionary-based database.
    Args:
        db (dict): The database dictionary.
        username (str): The username to search for.
    Returns:
        UserInDB | None: The user object if found, else None.
    """
    # Deprecated: Solo para compatibilidad
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(username: str, password: str):
    """
    Authenticate a user by username and password.
    Args:
        username (str): The user's username.
        password (str): The user's password.
    Returns:
        UserInDB | None: The authenticated user or None if authentication fails.
    """
    user = get_user_from_db(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with expiration.
    Args:
        data (dict): Data to encode in the token.
        expires_delta (timedelta, optional): Token expiration delta. Defaults to 15 minutes if not provided.
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user based on the JWT token provided in the request.
    Args:
        token (str): The JWT token extracted from the request.
    Returns:
        UserInDB: The user associated with the token.
    Raises:
        HTTPException: If authentication fails or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc
    user = get_user_from_db(token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Ensure the current user is active (not disabled).
    Args:
        current_user (User): The current authenticated user.
    Returns:
        User: The current active user.
    Raises:
        HTTPException: If the user is inactive.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user
