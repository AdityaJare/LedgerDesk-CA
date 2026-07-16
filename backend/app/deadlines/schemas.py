from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

class DeadlineCreate(BaseModel):
    client_id: str
    client_name: str
    obligation: str = Field(..., min_length=2)
    period: str = Field(..., min_length=2)
    due_date: date
    owner: str = Field("Priya S")
    status: str = Field("pending", pattern="^(pending|in_prep|awaiting_docs|in_review|filed|overdue)$")
    blocker: Optional[str] = None

class DeadlineUpdate(BaseModel):
    status: Optional[str] = None
    blocker: Optional[str] = None
    owner: Optional[str] = None

class DeadlineResponse(BaseModel):
    id: str
    client_id: str
    client_name: str
    obligation: str
    period: str
    due_date: date
    owner: str
    status: str
    blocker: Optional[str] = None
    days_left: int

    class Config:
        from_attributes = True
