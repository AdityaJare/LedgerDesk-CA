from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ReviewCommentSchema(BaseModel):
    author: str
    text: str
    timestamp: datetime

class ReviewCreate(BaseModel):
    work_item_id: str
    work_item_type: str = Field(..., pattern="^(GST reconciliation summary|Notice reply draft|Audit workpaper pack|TDS reconciliation summary)$")
    client_id: str
    client_name: str
    item_name: str
    submitted_by: str
    reviewer: str = Field("Partner Desk")
    status: str = Field("Awaiting review", pattern="^(Awaiting manager|Awaiting partner|Returned|Approved|Exported)$")
    risk_flag: str = Field("Medium", pattern="^(Low|Medium|High)$")

class ReviewUpdate(BaseModel):
    status: Optional[str] = None
    new_comment: Optional[str] = None
    comment_author: Optional[str] = None
    export_state: Optional[str] = None
    version: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    work_item_id: str
    work_item_type: str
    client_id: str
    client_name: str
    item_name: str
    submitted_by: str
    reviewer: str
    status: str
    comments: List[ReviewCommentSchema] = []
    risk_flag: str
    timestamp: datetime
    export_state: str = "Not exported"
    version: str = "v1.0"

    class Config:
        from_attributes = True
