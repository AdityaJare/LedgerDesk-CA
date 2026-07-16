from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ClientCreate(BaseModel):
    name: str = Field(..., min_length=2)
    gstin: Optional[str] = Field(None, pattern="^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$|^$")
    pan: Optional[str] = Field(None, pattern="^[A-Z]{5}[0-9]{4}[A-Z]{1}$|^$")
    contact: Optional[str] = None
    status: str = Field("active", pattern="^(active|inactive)$")

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[str] = None

class ClientResponse(BaseModel):
    id: str
    name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    contact: Optional[str] = None
    status: str
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True
