from pydantic import BaseModel, Field
from typing import Optional

class ExceptionCreate(BaseModel):
    client_id: str
    client_name: str
    type: str = Field(..., pattern="^(GSTR-2A mismatch|TDS variance|Bank reconciliation break|Vendor mismatch|Ledger break|Challan issue)$")
    affected_entries: int = Field(..., ge=1)
    value_impact: str
    age: str
    assigned_to: str
    next_action: str
    state: str = Field("Open", pattern="^(Open|In progress|Pending review|Escalated|Resolved)$")

class ExceptionUpdate(BaseModel):
    assigned_to: Optional[str] = None
    next_action: Optional[str] = None
    state: Optional[str] = None

class ExceptionResponse(BaseModel):
    id: str
    client_id: str
    client_name: str
    type: str
    affected_entries: int
    value_impact: str
    age: str
    assigned_to: str
    next_action: str
    state: str

    class Config:
        from_attributes = True
