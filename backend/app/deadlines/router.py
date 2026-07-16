from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.database import get_database
from app.auth.dependencies import get_current_user
from app.deadlines.schemas import DeadlineCreate, DeadlineUpdate, DeadlineResponse
from app.audit_trail.service import log_audit_event
from bson import ObjectId
from datetime import datetime, date
from typing import List, Optional

router = APIRouter(prefix="/api/deadlines", tags=["Deadlines"])

def serialize_deadline(doc) -> dict:
    if not doc:
        return None
    res = doc.copy()
    res["id"] = str(res["_id"])
    del res["_id"]
    
    # Calculate days_left
    due_date_val = res["due_date"]
    if isinstance(due_date_val, datetime):
        due_date_val = due_date_val.date()
    elif isinstance(due_date_val, str):
        due_date_val = datetime.strptime(due_date_val[:10], "%Y-%m-%d").date()
    
    today = date.today()
    res["days_left"] = (due_date_val - today).days
    res["due_date"] = due_date_val
    return res

@router.get("", response_model=List[DeadlineResponse])
async def list_deadlines(
    db = Depends(get_database),
    current_user = Depends(get_current_user),
    filter_type: Optional[str] = Query(None),
    timeframe: Optional[str] = Query(None)
):
    query = {}
    if filter_type and filter_type.lower() != "all":
        # GST, TDS, Audit, Notices
        query["obligation"] = {"$regex": filter_type, "$options": "i"}
        
    cursor = db.deadlines.find(query).sort("due_date", 1)
    deadlines = []
    today = date.today()
    
    async for doc in cursor:
        item = serialize_deadline(doc)
        
        # timeframe filters
        if timeframe == "today":
            if item["due_date"] != today:
                continue
        elif timeframe == "next3":
            diff = (item["due_date"] - today).days
            if diff < 0 or diff > 3:
                continue
        elif timeframe == "thisweek":
            diff = (item["due_date"] - today).days
            if diff < 0 or diff > 7:
                continue
        elif timeframe == "overdue":
            if item["days_left"] >= 0 or item["status"] == "filed":
                continue
                
        deadlines.append(item)
    return deadlines

@router.post("", response_model=DeadlineResponse, status_code=status.HTTP_201_CREATED)
async def create_deadline(payload: DeadlineCreate, db = Depends(get_database), current_user = Depends(get_current_user)):
    new_deadline = {
        "client_id": payload.client_id,
        "client_name": payload.client_name,
        "obligation": payload.obligation,
        "period": payload.period,
        "due_date": datetime.combine(payload.due_date, datetime.min.time()),
        "owner": payload.owner,
        "status": payload.status,
        "blocker": payload.blocker or ""
    }
    
    result = await db.deadlines.insert_one(new_deadline)
    new_deadline["_id"] = result.inserted_id
    serialized = serialize_deadline(new_deadline)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="create_deadline",
        resource_type="deadline",
        resource_id=serialized["id"],
        details=f"Created deadline: {payload.obligation} for {payload.client_name}"
    )
    
    return serialized

@router.put("/{deadline_id}", response_model=DeadlineResponse)
async def update_deadline(
    deadline_id: str,
    payload: DeadlineUpdate,
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    try:
        oid = ObjectId(deadline_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid deadline ID")
        
    existing = await db.deadlines.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Deadline not found")
        
    update_data = {}
    if payload.status is not None:
        update_data["status"] = payload.status
    if payload.blocker is not None:
        update_data["blocker"] = payload.blocker
    if payload.owner is not None:
        update_data["owner"] = payload.owner
        
    if update_data:
        await db.deadlines.update_one({"_id": oid}, {"$set": update_data})
        existing = await db.deadlines.find_one({"_id": oid})
        
    serialized = serialize_deadline(existing)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="update_deadline",
        resource_type="deadline",
        resource_id=deadline_id,
        details=f"Updated deadline fields: {list(update_data.keys())}"
    )
    
    return serialized
