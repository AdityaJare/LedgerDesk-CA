from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.database import get_database
from app.auth.dependencies import get_current_user
from app.ai_agents.gemini_service import generate_response
from app.audit_trail.service import log_audit_event

router = APIRouter(prefix="/api/ai", tags=["AI Agents"])

# Request models
class NoticeReplyRequest(BaseModel):
    client_name: str
    notice_subject: str
    notice_body: str

class ReconciliationRequest(BaseModel):
    client_name: str
    exception_type: str
    entries_count: int
    value_impact: str

class LawResearchRequest(BaseModel):
    query: str

class AuditReviewRequest(BaseModel):
    workpaper_title: str
    content: str

class FollowUpRequest(BaseModel):
    client_name: str
    requested_item: str
    deadline_impact: str

# Endpoints
@router.post("/notice-reply")
async def draft_notice_reply(payload: NoticeReplyRequest, db = Depends(get_database), current_user = Depends(get_current_user)):
    system_instruction = (
        "You are the LedgerDesk Notice Reply Agent, a constrained AI assistant for Indian Chartered Accountants. "
        "Your task is to draft a professional, grounded legal reply to a tax notice (GST or Income Tax). "
        "Enforce strict professional tone, format it appropriately (with To, Subject, Reference, body paragraphs), "
        "and reference specific sections of the relevant Acts (e.g. CGST Act 2017 or Income Tax Act 1961). "
        "State clearly that this is a draft and requires human reviewer validation. Do not invent facts."
    )
    prompt = (
        f"Draft a response for client: {payload.client_name}\n"
        f"Subject of notice: {payload.notice_subject}\n"
        f"Details: {payload.notice_body}\n"
    )
    
    draft = await generate_response(prompt, system_instruction)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="ai_notice_reply",
        resource_type="ai_agent",
        resource_id="notice_reply_agent",
        details=f"Generated notice reply draft for {payload.client_name}"
    )
    
    return {"draft": draft, "draft_only": True, "source_linked": True}

@router.post("/reconciliation")
async def analyze_reconciliation(payload: ReconciliationRequest, db = Depends(get_database), current_user = Depends(get_current_user)):
    system_instruction = (
        "You are the LedgerDesk Reconciliation Agent. "
        "Analyze the provided mismatch parameters and produce a structured list of recommended triage steps. "
        "Do not make automatic adjustments. Outline where the team should verify data "
        "(e.g., GSTR-2A matching vs books, checking Form 26AS matching, or challan mapping)."
    )
    prompt = (
        f"Client: {payload.client_name}\n"
        f"Exception Type: {payload.exception_type}\n"
        f"Affected Entries Count: {payload.entries_count}\n"
        f"Value Impact: {payload.value_impact}\n"
    )
    
    analysis = await generate_response(prompt, system_instruction)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="ai_reconciliation",
        resource_type="ai_agent",
        resource_id="reconciliation_agent",
        details=f"Generated reconciliation steps for {payload.client_name}"
    )
    
    return {"analysis": analysis, "draft_only": True}

@router.post("/law-research")
async def perform_law_research(payload: LawResearchRequest, db = Depends(get_database), current_user = Depends(get_current_user)):
    system_instruction = (
        "You are the LedgerDesk Law Research Agent. "
        "Find and citation-link relevant sections, notifications, circulars, or case laws in Indian Tax law for the query. "
        "Provide direct citations. Add a disclaimer: 'This output contains citations for research support only and does not constitute formal legal advice.'"
    )
    prompt = f"Perform research for query: {payload.query}"
    
    research = await generate_response(prompt, system_instruction)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="ai_law_research",
        resource_type="ai_agent",
        resource_id="law_research_agent",
        details=f"Performed legal research for: {payload.query[:30]}"
    )
    
    return {"research": research, "draft_only": True}

@router.post("/audit-review")
async def perform_audit_review(payload: AuditReviewRequest, db = Depends(get_database), current_user = Depends(get_current_user)):
    system_instruction = (
        "You are the LedgerDesk Audit Review Agent. "
        "Scan the provided working paper text or schedule and report gaps, missing links, "
        "inconsistencies, or incomplete schedules as a checklist. "
        "Do not edit or delete any numbers or text. Return findings as a checklist only."
    )
    prompt = (
        f"Workpaper Title: {payload.workpaper_title}\n"
        f"Content to review:\n{payload.content}"
    )
    
    review_findings = await generate_response(prompt, system_instruction)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="ai_audit_review",
        resource_type="ai_agent",
        resource_id="audit_review_agent",
        details=f"Performed audit review on workpaper: {payload.workpaper_title}"
    )
    
    return {"review_findings": review_findings, "draft_only": True}

@router.post("/followup")
async def generate_client_followup(payload: FollowUpRequest, db = Depends(get_database), current_user = Depends(get_current_user)):
    system_instruction = (
        "You are the LedgerDesk Client Follow-up Agent. "
        "Draft a polite but firm professional message to be sent to a client requesting pending documents. "
        "Indicate the specific outstanding items, state how it impacts their filing deadline, "
        "and request an update. The draft should be ready to copy-paste into email or message fields."
    )
    prompt = (
        f"Client Name: {payload.client_name}\n"
        f"Pending requested item: {payload.requested_item}\n"
        f"Deadline impact: {payload.deadline_impact}\n"
    )
    
    message_draft = await generate_response(prompt, system_instruction)
    
    await log_audit_event(
        db,
        user_id=current_user["id"],
        action="ai_client_followup",
        resource_type="ai_agent",
        resource_id="followup_agent",
        details=f"Generated follow-up draft for {payload.client_name}"
    )
    
    return {"message_draft": message_draft, "draft_only": True}
