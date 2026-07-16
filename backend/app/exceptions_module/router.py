from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.database import get_database
from app.auth.dependencies import get_current_user
from app.exceptions_module.schemas import ExceptionCreate, ExceptionUpdate, ExceptionResponse
from app.audit_trail.service import log_audit_event
from bson import ObjectId
from typing import List, Optional

router = APIRouter(prefix="/api/exceptions", tags=["Exceptions"])

def serialize_exception(doc) -> dict:
    if not doc:
        return None
    res = doc.copy()
    res["id"] = str(res["_id"])
    del res["_id"]
    return res

@router.get("", response_model=List[ExceptionResponse])
async def list_exceptions(
    db = Depends(get_database),
    current_user = Depends(get_current_user),
    filter_type: Optional[str] = Query(None)
):
    query = {}
    if filter_type and filter_type.lower() != "all":
        query["type"] = {"$regex": filter_type, "$options": "i"}
        
    cursor = db.exceptions.find(query).sort("type", 1)
    exceptions = []
    async for doc in cursor:
        exceptions.append(serialize_exception(doc))
    return exceptions

@router.post("", response_model=ExceptionResponse, status_code=status.HTTP_201_CREATED)
async def create_exception(payload: ExceptionCreate, db = Depends(get_database), current_user = Depends(get_current_user)):
    new_exception = {
        "client_id": payload.client_id,
        "client_name": payload.client_name,
        "type": payload.type,
        "affected_entries": payload.affected_entries,
        "value_impact": payload.value_impact,
        "age": payload.age,
        "assigned_to": payload.assigned_to,
        "next_action": payload.next_action,
        "state": payload.state
    }
    
    result = await db.exceptions.insert_one(new_exception)
    new_exception["_id"] = result.inserted_id
    serialized = serialize_exception(new_exception)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="create_exception",
        resource_type="exception",
        resource_id=serialized["id"],
        details=f"Created exceptions of type {payload.type} for {payload.client_name}"
    )
    
    return serialized

@router.put("/{exception_id}", response_model=ExceptionResponse)
async def update_exception(
    exception_id: str,
    payload: ExceptionUpdate,
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    try:
        oid = ObjectId(exception_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid exception ID")
        
    existing = await db.exceptions.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Exception not found")
        
    update_data = {}
    if payload.assigned_to is not None:
        update_data["assigned_to"] = payload.assigned_to
    if payload.next_action is not None:
        update_data["next_action"] = payload.next_action
    if payload.state is not None:
        update_data["state"] = payload.state
        
    if update_data:
        await db.exceptions.update_one({"_id": oid}, {"$set": update_data})
        existing = await db.exceptions.find_one({"_id": oid})
        
    serialized = serialize_exception(existing)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="update_exception",
        resource_type="exception",
        resource_id=exception_id,
        details=f"Updated exception status/assignee fields: {list(update_data.keys())}"
    )
    
    return serialized
