"""
user.py

Defines Pydantic models for user-related data structures used in authentication and user management.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    """
    Represents a user in the system.

    Attributes:
        username (str): The user's unique username.
        email (Optional[EmailStr]): The user's email address.
        full_name (Optional[str]): The user's full name.
        hashed_password (str): The user's hashed password.
        disabled (bool): Indicates if the user account is disabled.
    """
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    hashed_password: str
    disabled: bool = False

class UserCreate(BaseModel):
    """
    Model for creating a new user (input data).

    Attributes:
        username (str): The new user's username.
        email (Optional[EmailStr]): The new user's email address.
        full_name (Optional[str]): The new user's full name.
        password (str): The new user's plain password.
    """
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: str
