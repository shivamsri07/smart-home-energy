# backend/app/modules/auth/schemas.py
from datetime import datetime
from pydantic import BaseModel, EmailStr
import uuid


# --- Token Schemas ---

class Token(BaseModel):
    """
    Schema for the access token response.
    This is what the user receives upon successful login.
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema for the data encoded within the JWT.
    Contains the identifier for the user.
    """
    email: EmailStr | None = None


# --- User Schemas ---

class UserBase(BaseModel):
    """
    Base schema for a User, containing common fields.
    """
    email: EmailStr

class UserPublic(UserBase):
    """
    Public schema for a User, containing common fields.
    """
    id: uuid.UUID
    created_at: datetime

class UserCreate(UserBase):
    """
    Schema for user creation.
    Inherits email from UserBase and adds the password.
    Used for the /register endpoint.
    """
    password: str

class UserLogin(BaseModel):
    """
    Schema for user login.
    """
    email: EmailStr
    password: str

class UserInDB(UserBase):
    """
    Schema for representing a user as it is in the database.
    Includes fields that should be present for an existing user.
    """
    id: uuid.UUID
    password_hash: str

    class Config:
        """Pydantic configuration to allow ORM mode."""
        from_attributes = True