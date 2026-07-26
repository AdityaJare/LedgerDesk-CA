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

@router.get("/{draft_id}/export")
async def export_draft_document(
    draft_id: str,
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
        
    firm_name = current_user.get("firm_name", "Chartered Accountant Practice Firm")
    author_name = doc.get("prepared_by", current_user.get("name", "Chartered Accountant"))
    reviewer_name = doc.get("reviewer", "Partner Sign-off")
    version_num = doc.get("version", 1.0)
    
    formatted_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Official Legal Reply - {doc['client_name']}</title>
    <style>
        body {{ font-family: 'Times New Roman', Times, serif; font-size: 13pt; line-height: 1.6; margin: 45px; color: #111; }}
        .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 25px; }}
        .firm-title {{ font-size: 18pt; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
        .firm-sub {{ font-size: 10pt; font-style: italic; color: #444; }}
        .meta-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 11pt; }}
        .meta-table td {{ padding: 4px 8px; border-bottom: 1px solid #eee; }}
        .content {{ white-space: pre-wrap; margin-top: 20px; font-size: 12pt; text-align: justify; }}
        .footer {{ margin-top: 60px; page-break-inside: avoid; }}
        .sig-block {{ float: right; width: 250px; text-align: center; font-weight: bold; border-top: 1px dashed #444; padding-top: 8px; margin-top: 40px; }}
        .watermark {{ position: fixed; bottom: 10px; right: 10px; font-size: 9pt; color: #888; font-family: sans-serif; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="firm-title">{firm_name}</div>
        <div class="firm-sub">CHARTERED ACCOUNTANTS & STATUTORY AUDITORS</div>
    </div>
    
    <table class="meta-table">
        <tr><td><strong>Client Name:</strong> {doc['client_name']}</td><td><strong>Matter / Ref:</strong> {doc['matter']}</td></tr>
        <tr><td><strong>Draft Type:</strong> {doc['draft_type']}</td><td><strong>Version:</strong> v{version_num}</td></tr>
        <tr><td><strong>Prepared By:</strong> {author_name}</td><td><strong>Reviewer:</strong> {reviewer_name}</td></tr>
        <tr><td><strong>State:</strong> {doc['state']}</td><td><strong>Export Date:</strong> {datetime.utcnow().strftime('%d %B %Y')}</td></tr>
    </table>
    
    <div class="content">{doc['content']}</div>
    
    <div class="footer">
        <div class="sig-block">
            For {firm_name}<br><br><br>
            ({reviewer_name})<br>
            Partner / Authorized Signatory
        </div>
        <div style="clear: both;"></div>
    </div>
    
    <div class="watermark">Generated via LedgerDesk CA OS | Immutable Audit Logged</div>
</body>
</html>"""

    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="export_notice_draft",
        resource_type="draft",
        resource_id=draft_id,
        details=f"Exported printable legal draft v{version_num} for {doc['client_name']}"
    )
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=formatted_html, status_code=200)

