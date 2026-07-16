from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DocumentCreate(BaseModel):
    client_id: str
    client_name: str
    requested_item: str = Field(..., min_length=2)
    related_task: str = Field(..., min_length=2)
    impact: str = Field(..., min_length=2)
    status: str = Field("Awaiting client", pattern="^(Awaiting client|Partial received|Received|Escalate)$")

class DocumentUpdate(BaseModel):
    status: Optional[str] = None
    last_response: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    client_id: str
    client_name: str
    requested_item: str
    related_task: str
    requested_on: str
    reminder_count: int
    last_response: str
    impact: str
    status: str
    file_path: Optional[str] = None

    class Config:
        from_attributes = True
