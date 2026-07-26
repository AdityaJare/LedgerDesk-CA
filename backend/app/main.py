import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.auth.dependencies import get_current_user

# Import all routers
from app.auth.router import router as auth_router
from app.clients.router import router as clients_router
from app.deadlines.router import router as deadlines_router
from app.exceptions_module.router import router as exceptions_router
from app.documents.router import router as documents_router
from app.drafting.router import router as drafting_router
from app.reviews.router import router as reviews_router
from app.bookings.router import router as bookings_router
from app.audit_trail.router import router as audit_router
from app.ai_agents.router import router as ai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="LedgerDesk CA — Practice Operating System",
    description="Full-stack API for Indian Chartered Accountant practice management: deadlines, reconciliation, drafting, review trails, and AI agents.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routers
app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(deadlines_router)
app.include_router(exceptions_router)
app.include_router(documents_router)
app.include_router(drafting_router)
app.include_router(reviews_router)
app.include_router(bookings_router)
app.include_router(audit_router)
app.include_router(ai_router)

# --- Dashboard summary endpoint ---
@app.get("/api/dashboard/summary", tags=["Dashboard"])
async def dashboard_summary(
    db = Depends(get_database),
    current_user = Depends(get_current_user)
):
    import asyncio
    from datetime import datetime, date
    today = datetime.combine(date.today(), datetime.min.time())

    # Execute all 7 Mongo count queries concurrently
    (
        overdue_count,
        pending_deadlines,
        open_exceptions,
        awaiting_docs,
        drafts_in_progress,
        pending_reviews,
        total_clients
    ) = await asyncio.gather(
        db.deadlines.count_documents({"due_date": {"$lt": today}, "status": {"$nin": ["filed"]}}),
        db.deadlines.count_documents({"status": {"$in": ["pending", "in_prep", "awaiting_docs"]}}),
        db.exceptions.count_documents({"state": {"$in": ["Open", "In progress"]}}),
        db.documents.count_documents({"status": "Awaiting client"}),
        db.drafts.count_documents({"state": {"$in": ["Requested", "In progress", "Draft ready"]}}),
        db.reviews.count_documents({"status": {"$in": ["Awaiting manager", "Awaiting partner"]}}),
        db.clients.count_documents({"status": "active"})
    )

    return {
        "overdue_deadlines": overdue_count,
        "pending_deadlines": pending_deadlines,
        "open_exceptions": open_exceptions,
        "awaiting_documents": awaiting_docs,
        "drafts_in_progress": drafts_in_progress,
        "pending_reviews": pending_reviews,
        "total_clients": total_clients
    }


# --- Serve frontend static files ---
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)

if os.path.isdir(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

@app.get("/", tags=["Frontend"])
async def serve_landing():
    path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(path):
        return FileResponse(path)
    return {"message": "LedgerDesk CA API is running. Visit /docs for Swagger UI."}

@app.get("/login", tags=["Frontend"])
async def serve_login():
    path = os.path.join(FRONTEND_DIR, "login.html")
    if os.path.isfile(path):
        return FileResponse(path)
    return {"message": "Login page not found."}

@app.get("/register", tags=["Frontend"])
async def serve_register():
    path = os.path.join(FRONTEND_DIR, "register.html")
    if os.path.isfile(path):
        return FileResponse(path)
    return {"message": "Register page not found."}

@app.get("/dashboard", tags=["Frontend"])
async def serve_dashboard():
    path = os.path.join(FRONTEND_DIR, "dashboard.html")
    if os.path.isfile(path):
        return FileResponse(path)
    return {"message": "Dashboard page not found."}

# Health check
@app.get("/api/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "LedgerDesk CA", "version": "1.0.0"}
