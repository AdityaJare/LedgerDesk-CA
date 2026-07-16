from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_database
from app.auth.dependencies import get_current_user
from app.drafting.schemas import DraftCreate, DraftUpdate, DraftResponse
from app.audit_trail.service import log_audit_event
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/api/drafts", tags=["Drafting"])

def serialize_draft(doc) -> dict:
    if not doc:
        return None
    res = doc.copy()
    res["id"] = str(res["_id"])
    del res["_id"]
    return res

@router.get("", response_model=List[DraftResponse])
async def list_drafts(db = Depends(get_database), current_user = Depends(get_current_user)):
    cursor = db.drafts.find({}).sort("due_by", 1)
    drafts = []
    async for doc in cursor:
        drafts.append(serialize_draft(doc))
    return drafts

@router.post("", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(payload: DraftCreate, db = Depends(get_database), current_user = Depends(get_current_user)):
    new_draft = {
        "client_id": payload.client_id,
        "client_name": payload.client_name,
        "matter": payload.matter,
        "draft_type": payload.draft_type,
        "content": payload.content,
        "prepared_by": payload.prepared_by,
        "reviewer": payload.reviewer,
        "state": payload.state,
        "due_by": payload.due_by,
        "comments": [],
        "version": 1.0,
        "created_at": datetime.utcnow()
    }
    
    result = await db.drafts.insert_one(new_draft)
    new_draft["_id"] = result.inserted_id
    serialized = serialize_draft(new_draft)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="create_draft",
        resource_type="draft",
        resource_id=serialized["id"],
        details=f"Created reply draft for {payload.matter} (Client: {payload.client_name})"
    )
    
    return serialized

@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: str, db = Depends(get_database), current_user = Depends(get_current_user)):
    try:
        doc = await db.drafts.find_one({"_id": ObjectId(draft_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid draft ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Draft not found")
    return serialize_draft(doc)

@router.put("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    payload: DraftUpdate,
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    try:
        oid = ObjectId(draft_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid draft ID")
        
    doc = await db.drafts.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    update_data = {}
    
    # Increment version if content changes
    if payload.content is not None and payload.content != doc["content"]:
        update_data["content"] = payload.content
        update_data["version"] = round(doc.get("version", 1.0) + 0.1, 1)
        
    if payload.state is not None:
        update_data["state"] = payload.state
        
    if payload.new_comment:
        author = payload.comment_author or current_user["name"]
        new_c = {
            "author": author,
            "text": payload.new_comment,
            "timestamp": datetime.utcnow()
        }
        await db.drafts.update_one({"_id": oid}, {"$push": {"comments": new_c}})
        
    if update_data:
        await db.drafts.update_one({"_id": oid}, {"$set": update_data})
        
    updated = await db.drafts.find_one({"_id": oid})
    serialized = serialize_draft(updated)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="update_draft",
        resource_type="draft",
        resource_id=draft_id,
        details=f"Updated draft fields: {list(update_data.keys())} or added comment"
    )
    
    return serialized
