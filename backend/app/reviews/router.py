from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_database
from app.auth.dependencies import get_current_user
from app.reviews.schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from app.audit_trail.service import log_audit_event
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

def serialize_review(doc) -> dict:
    if not doc:
        return None
    res = doc.copy()
    res["id"] = str(res["_id"])
    del res["_id"]
    return res

@router.get("", response_model=List[ReviewResponse])
async def list_reviews(db = Depends(get_database), current_user = Depends(get_current_user)):
    cursor = db.reviews.find({}).sort("timestamp", -1)
    reviews = []
    async for doc in cursor:
        reviews.append(serialize_review(doc))
    return reviews

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review_request(payload: ReviewCreate, db = Depends(get_database), current_user = Depends(get_current_user)):
    new_review = {
        "work_item_id": payload.work_item_id,
        "work_item_type": payload.work_item_type,
        "client_id": payload.client_id,
        "client_name": payload.client_name,
        "item_name": payload.item_name,
        "submitted_by": payload.submitted_by,
        "reviewer": payload.reviewer,
        "status": payload.status,
        "risk_flag": payload.risk_flag,
        "comments": [],
        "timestamp": datetime.utcnow(),
        "export_state": "Not exported",
        "version": "v1.0"
    }
    
    result = await db.reviews.insert_one(new_review)
    new_review["_id"] = result.inserted_id
    serialized = serialize_review(new_review)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="submit_for_review",
        resource_type="review",
        resource_id=serialized["id"],
        details=f"Submitted {payload.work_item_type} for client {payload.client_name} for review"
    )
    
    return serialized

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str, db = Depends(get_database), current_user = Depends(get_current_user)):
    try:
        doc = await db.reviews.find_one({"_id": ObjectId(review_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid review ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Review not found")
    return serialize_review(doc)

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review_status(
    review_id: str,
    payload: ReviewUpdate,
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    try:
        oid = ObjectId(review_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid review ID")
        
    doc = await db.reviews.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Review not found")
        
    update_data = {}
    if payload.status is not None:
        update_data["status"] = payload.status
    if payload.export_state is not None:
        update_data["export_state"] = payload.export_state
    if payload.version is not None:
        update_data["version"] = payload.version
        
    if payload.new_comment:
        author = payload.comment_author or current_user["name"]
        new_c = {
            "author": author,
            "text": payload.new_comment,
            "timestamp": datetime.utcnow()
        }
        await db.reviews.update_one({"_id": oid}, {"$push": {"comments": new_c}})
        
    if update_data:
        await db.reviews.update_one({"_id": oid}, {"$set": update_data})
        
    updated = await db.reviews.find_one({"_id": oid})
    serialized = serialize_review(updated)
    
    action_type = "review_update"
    if payload.status == "Approved":
        action_type = "approve_review"
    elif payload.status == "Returned":
        action_type = "return_review"
    elif payload.export_state == "Exported":
        action_type = "export_evidence"
        
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action=action_type,
        resource_type="review",
        resource_id=review_id,
        details=f"Review status: {payload.status or doc['status']}, export state: {payload.export_state or doc['export_state']}"
    )
    
    return serialized
