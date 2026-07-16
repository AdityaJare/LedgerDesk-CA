from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional

class BookingCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    firm_name: str = Field(..., min_length=2)
    firm_size: str = Field("1-5", pattern="^(1-5|6-15|16-50|50\\+)$")
    phone: str = Field(..., min_length=10)
    preferred_date: date
    message: Optional[str] = None

class BookingResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    firm_name: str
    firm_size: str
    phone: str
    preferred_date: date
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
