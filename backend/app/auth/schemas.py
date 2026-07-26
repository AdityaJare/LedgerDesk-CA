from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    firm_name: str = Field(..., min_length=2)
    role: str = Field("executive", pattern="^(partner|manager|executive|clerk)$")

class UserLogin(BaseModel):
    email: str = Field(..., min_length=3)
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    firm_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
