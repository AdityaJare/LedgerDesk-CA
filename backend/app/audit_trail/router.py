from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_database
from app.auth.dependencies import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/api/audit-trail", tags=["Audit Trail"])

@router.get("")
async def get_audit_trail(
    db = Depends(get_database),
    current_user = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    resource_type: Optional[str] = None
):
    if current_user["role"] not in ["partner", "manager"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    query = {}
    if action:
        query["action"] = action
    if resource_type:
        query["resource_type"] = resource_type
        
    cursor = db.audit_logs.find(query).sort("timestamp", -1).limit(limit)
    logs = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        logs.append(doc)
    return logs
