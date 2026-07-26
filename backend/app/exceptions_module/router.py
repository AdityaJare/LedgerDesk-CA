from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
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

@router.post("/import-csv", status_code=status.HTTP_201_CREATED)
async def import_reconciliation_csv(
    client_id: str,
    client_name: str,
    file: UploadFile = File(...),
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    import csv
    import io
    
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8")
    except UnicodeDecodeError:
        decoded = contents.decode("latin-1")
        
    reader = csv.DictReader(io.StringIO(decoded))
    created_items = []
    
    for row in reader:
        # Standard GSTR-2B vs Books reconciliation fields
        exc_type = row.get("type") or row.get("Exception Type") or "GSTR-2A vs Books mismatch"
        affected = int(row.get("affected_entries") or row.get("Affected Entries") or 1)
        value_impact = row.get("value_impact") or row.get("Value Impact") or "₹0"
        next_act = row.get("next_action") or row.get("Next Action") or "Verify purchase register with client invoices"
        
        new_doc = {
            "client_id": client_id,
            "client_name": client_name,
            "type": exc_type,
            "affected_entries": affected,
            "value_impact": value_impact,
            "age": "1 day",
            "assigned_to": current_user["name"],
            "next_action": next_act,
            "state": "Open"
        }
        res = await db.exceptions.insert_one(new_doc)
        new_doc["_id"] = res.inserted_id
        created_items.append(serialize_exception(new_doc))
        
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="bulk_import_exceptions",
        resource_type="exception",
        resource_id=client_id,
        details=f"Bulk imported {len(created_items)} reconciliation exceptions for {client_name} from {file.filename}"
    )
    
    return {
        "status": "success",
        "imported_count": len(created_items),
        "exceptions": created_items
    }

