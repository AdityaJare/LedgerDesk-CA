import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.database import get_database
from app.config import settings
from app.auth.dependencies import get_current_user
from app.documents.schemas import DocumentCreate, DocumentUpdate, DocumentResponse
from app.audit_trail.service import log_audit_event
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/api/documents", tags=["Documents"])

def serialize_document(doc) -> dict:
    if not doc:
        return None
    res = doc.copy()
    res["id"] = str(res["_id"])
    del res["_id"]
    return res

@router.get("", response_model=List[DocumentResponse])
async def list_documents(db = Depends(get_database), current_user = Depends(get_current_user)):
    cursor = db.documents.find({}).sort("requested_on", -1)
    documents = []
    async for doc in cursor:
        documents.append(serialize_document(doc))
    return documents

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document_request(payload: DocumentCreate, db = Depends(get_database), current_user = Depends(get_current_user)):
    new_doc = {
        "client_id": payload.client_id,
        "client_name": payload.client_name,
        "requested_item": payload.requested_item,
        "related_task": payload.related_task,
        "requested_on": datetime.now().strftime("%d %b"),
        "reminder_count": 0,
        "last_response": "No reply",
        "impact": payload.impact,
        "status": payload.status,
        "file_path": ""
    }
    
    result = await db.documents.insert_one(new_doc)
    new_doc["_id"] = result.inserted_id
    serialized = serialize_document(new_doc)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="create_document_request",
        resource_type="document_request",
        resource_id=serialized["id"],
        details=f"Requested {payload.requested_item} from {payload.client_name}"
    )
    
    return serialized

@router.post("/{doc_id}/upload", response_model=DocumentResponse)
async def upload_document(
    doc_id: str,
    file: UploadFile = File(...),
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    try:
        oid = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID")
        
    doc = await db.documents.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Document request not found")
        
    # Generate path
    filename = f"{doc['client_id']}_{doc_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # Update DB
    await db.documents.update_one(
        {"_id": oid},
        {
            "$set": {
                "file_path": file_path,
                "status": "Received",
                "last_response": "Uploaded by client"
            }
        }
    )
    
    updated_doc = await db.documents.find_one({"_id": oid})
    serialized = serialize_document(updated_doc)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="upload_document",
        resource_type="document",
        resource_id=doc_id,
        details=f"Uploaded file {file.filename} for request: {doc['requested_item']}"
    )
    
    return serialized

@router.post("/{doc_id}/remind", response_model=DocumentResponse)
async def send_reminder(
    doc_id: str,
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    try:
        oid = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID")
        
    doc = await db.documents.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Document request not found")
        
    new_reminders = doc.get("reminder_count", 0) + 1
    
    await db.documents.update_one(
        {"_id": oid},
        {
            "$set": {
                "reminder_count": new_reminders,
                "last_response": f"Reminder #{new_reminders} sent by {current_user['name']}"
            }
        }
    )
    
    updated_doc = await db.documents.find_one({"_id": oid})
    serialized = serialize_document(updated_doc)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="send_document_reminder",
        resource_type="document_request",
        resource_id=doc_id,
        details=f"Sent reminder #{new_reminders} to client for {doc['requested_item']}"
    )
    
    return serialized

@router.get("/{doc_id}/share-link")
async def generate_document_share_link(
    doc_id: str,
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    try:
        oid = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID")
        
    doc = await db.documents.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Document request not found")
        
    upload_url = f"http://localhost:8000/api/documents/{doc_id}/upload"
    client_name = doc.get("client_name", "Valued Client")
    requested_item = doc.get("requested_item", "Statutory Document")
    related_task = doc.get("related_task", "Filing Compliance")
    firm_name = current_user.get("firm_name", "CA Office")

    whatsapp_text = (
        f"Dear {client_name},\n\n"
        f"Greetings from {firm_name}.\n\n"
        f"This is a gentle reminder regarding the outstanding document: *{requested_item}* required for *{related_task}*.\n\n"
        f"Kindly upload the file securely via this direct upload link:\n{upload_url}\n\n"
        f"Timely receipt of documents ensures your statutory compliance is filed before the due date to avoid late fees.\n\n"
        f"Thank you,\n{firm_name}"
    )

    return {
        "document_id": doc_id,
        "client_name": client_name,
        "upload_url": upload_url,
        "whatsapp_template": whatsapp_text,
        "email_subject": f"Document Reminder: {requested_item} for {related_task} - {firm_name}",
        "email_body": whatsapp_text.replace("*", "")
    }

