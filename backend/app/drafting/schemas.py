from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class CommentSchema(BaseModel):
    author: str
    text: str
    timestamp: datetime

class DraftCreate(BaseModel):
    client_id: str
    client_name: str
    matter: str = Field(..., min_length=2)
    draft_type: str = Field(..., pattern="^(Notice reply|Reconciliation note|Audit note|Submission)$")
    content: str
    prepared_by: str
    reviewer: str
    state: str = Field("Requested", pattern="^(Requested|In progress|Draft ready|Returned|Approved)$")
    due_by: str

class DraftUpdate(BaseModel):
    content: Optional[str] = None
    state: Optional[str] = None
    new_comment: Optional[str] = None
    comment_author: Optional[str] = None

class DraftResponse(BaseModel):
    id: str
    client_id: str
    client_name: str
    matter: str
    draft_type: str
    content: str
    prepared_by: str
    reviewer: str
    state: str
    due_by: str
    comments: List[CommentSchema] = []
    version: float = 1.0

    class Config:
        from_attributes = True
