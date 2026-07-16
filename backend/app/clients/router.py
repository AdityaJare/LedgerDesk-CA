from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_database
from app.auth.dependencies import get_current_user
from app.clients.schemas import ClientCreate, ClientUpdate, ClientResponse
from app.audit_trail.service import log_audit_event
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/clients", tags=["Clients"])

def serialize_client(doc) -> dict:
    if not doc:
        return None
    res = doc.copy()
    res["id"] = str(res["_id"])
    del res["_id"]
    return res

@router.get("", response_model=List[ClientResponse])
async def list_clients(db = Depends(get_database), current_user = Depends(get_current_user)):
    cursor = db.clients.find({"status": "active"}).sort("name", 1)
    clients = []
    async for doc in cursor:
        clients.append(serialize_client(doc))
    return clients

@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreate, db = Depends(get_database), current_user = Depends(get_current_user)):
    # Check for existing client by name
    existing = await db.clients.find_one({"name": payload.name, "status": "active"})
    if existing:
        raise HTTPException(status_code=400, detail="Client with this name already exists")
        
    new_client = {
        "name": payload.name,
        "gstin": payload.gstin or "",
        "pan": payload.pan or "",
        "contact": payload.contact or "",
        "status": payload.status,
        "created_by": current_user["id"],
        "created_at": datetime.utcnow()
    }
    
    result = await db.clients.insert_one(new_client)
    new_client["_id"] = result.inserted_id
    serialized = serialize_client(new_client)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="create_client",
        resource_type="client",
        resource_id=serialized["id"],
        details=f"Created client {payload.name}"
    )
    
    return serialized

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, db = Depends(get_database), current_user = Depends(get_current_user)):
    try:
        doc = await db.clients.find_one({"_id": ObjectId(client_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid client ID")
        
    if not doc:
        raise HTTPException(status_code=404, detail="Client not found")
    return serialize_client(doc)

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, payload: ClientUpdate, db = Depends(get_database), current_user = Depends(get_current_user)):
    try:
        oid = ObjectId(client_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid client ID")
        
    existing = await db.clients.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Client not found")
        
    update_data = {}
    if payload.name is not None:
        update_data["name"] = payload.name
    if payload.gstin is not None:
        update_data["gstin"] = payload.gstin
    if payload.pan is not None:
        update_data["pan"] = payload.pan
    if payload.contact is not None:
        update_data["contact"] = payload.contact
    if payload.status is not None:
        update_data["status"] = payload.status
        
    if update_data:
        await db.clients.update_one({"_id": oid}, {"$set": update_data})
        # refresh document
        existing = await db.clients.find_one({"_id": oid})
        
    serialized = serialize_client(existing)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="update_client",
        resource_type="client",
        resource_id=serialized["id"],
        details=f"Updated client fields: {list(update_data.keys())}"
    )
    
    return serialized

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: str, db = Depends(get_database), current_user = Depends(get_current_user)):
    try:
        oid = ObjectId(client_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid client ID")
        
    existing = await db.clients.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Client not found")
        
    # soft delete: set status to inactive
    await db.clients.update_one({"_id": oid}, {"$set": {"status": "inactive"}})
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="delete_client",
        resource_type="client",
        resource_id=client_id,
        details=f"Soft deleted client {existing['name']}"
    )
    return None
