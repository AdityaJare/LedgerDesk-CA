from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_database
from app.auth.dependencies import get_current_user
from app.bookings.schemas import BookingCreate, BookingResponse
from app.audit_trail.service import log_audit_event
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

def serialize_booking(doc) -> dict:
    if not doc:
        return None
    res = doc.copy()
    res["id"] = str(res["_id"])
    del res["_id"]
    
    preferred_date_val = res["preferred_date"]
    if isinstance(preferred_date_val, datetime):
        preferred_date_val = preferred_date_val.date()
    elif isinstance(preferred_date_val, str):
        preferred_date_val = datetime.strptime(preferred_date_val[:10], "%Y-%m-%d").date()
    res["preferred_date"] = preferred_date_val
    return res

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(payload: BookingCreate, db = Depends(get_database)):
    new_booking = {
        "name": payload.name,
        "email": payload.email,
        "firm_name": payload.firm_name,
        "firm_size": payload.firm_size,
        "phone": payload.phone,
        "preferred_date": datetime.combine(payload.preferred_date, datetime.min.time()),
        "message": payload.message or "",
        "created_at": datetime.utcnow()
    }
    
    result = await db.demo_bookings.insert_one(new_booking)
    new_booking["_id"] = result.inserted_id
    serialized = serialize_booking(new_booking)
    
    # Audit log
    await log_audit_event(
        db,
        user_id=None,
        action="book_demo",
        resource_type="booking",
        resource_id=serialized["id"],
        details=f"Demo booked by {payload.name} ({payload.email}) for firm {payload.firm_name}"
    )
    
    return serialized

@router.get("", response_model=List[BookingResponse])
async def list_bookings(db = Depends(get_database), current_user = Depends(get_current_user)):
    if current_user["role"] != "partner":
        raise HTTPException(status_code=403, detail="Permission denied")
        
    cursor = db.demo_bookings.find({}).sort("created_at", -1)
    bookings = []
    async for doc in cursor:
        bookings.append(serialize_booking(doc))
    return bookings
