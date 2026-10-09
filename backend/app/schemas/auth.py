from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)

class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: str

class GoogleAuthRequest(BaseModel):
    token: str = Field(..., description="Google ID Token (credential)")

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    message: str = "Authentication successful"
