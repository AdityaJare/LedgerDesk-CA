# 🏛️ LedgerDesk CA — System Architecture & Data Schema Map

> **Memory Reference File**: Use this document to inspect API contracts, MongoDB collection structures, security mechanisms, and Gemini AI agent pipelines without parsing source code files.

---

## 1. Backend Architecture (FastAPI + Async Motor MongoDB)

### FastAPI Application Entry Point: [`backend/app/main.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/main.py)
- **Database Lifecycle**: `@asynccontextmanager lifespan` initializes Motor client on startup and cleans up on shutdown.
- **Dashboard Optimization**: `GET /api/dashboard/summary` uses `asyncio.gather` for 7 concurrent MongoDB count queries.
- **Static Asset Serving**: Mounts `/css` and `/js` from `../frontend`.

### API Router Registry & Endpoints

| Domain | Router File | Primary Endpoints | Description |
| :--- | :--- | :--- | :--- |
| **Authentication** | [`auth/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/auth/router.py) | `POST /api/auth/login`, `POST /api/auth/register`, `GET /api/auth/me` | JWT + bcrypt auth. |
| **Clients** | [`clients/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/clients/router.py) | `GET /api/clients`, `POST /api/clients` | Client firm directory (GSTIN, PAN). |
| **Deadlines** | [`deadlines/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/deadlines/router.py) | `GET /api/deadlines`, `POST /api/deadlines/check-escalations` | Statutory calendar + auto-overdue engine. |
| **Exceptions** | [`exceptions_module/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/exceptions_module/router.py) | `GET /api/exceptions`, `POST /api/exceptions/import-csv` | Reconciliation breaks + CSV bulk import. |
| **Documents** | [`documents/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/documents/router.py) | `GET /api/documents`, `GET /api/documents/{id}/share-link` | Document chasing + WhatsApp template. |
| **Drafting** | [`drafting/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/drafting/router.py) | `GET /api/drafts`, `GET /api/drafts/{id}/export` | Notice reply workspace + letterhead exporter. |
| **Reviews** | [`reviews/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/reviews/router.py) | `GET /api/reviews`, `PUT /api/reviews/{id}` | 4-stage approval workflow. |
| **Audit Trail** | [`audit_trail/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/audit_trail/router.py) | `GET /api/audit-trail` | Immutable activity log. |
| **AI Co-Pilot** | [`ai_agents/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/ai_agents/router.py) | `POST /api/ai/notice-reply`, `POST /api/ai/reconciliation`, etc. | Async multi-model Gemini AI adapter. |
| **Bookings** | [`bookings/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/bookings/router.py) | `POST /api/bookings` | Demo request lead capture. |

---

## 2. Frontend Architecture (Modular JS Feature Files)

### Directory: [`frontend/js/`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/)

| Module File | Global Object | Backend Endpoint | Feature |
| :--- | :--- | :--- | :--- |
| [`api.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/api.js) | `api` | — | JWT token client, auto-detects `file://` fallback to `http://localhost:8000`. |
| [`dashboard.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/dashboard.js) | `DashboardModule` | `GET /api/dashboard/summary` | Live practice metric counters. |
| [`deadlines.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/deadlines.js) | `DeadlinesModule` | `GET /api/deadlines`, `POST /api/deadlines/check-escalations` | Statutory calendar with GST/TDS/Audit filter + auto-escalation. |
| [`exceptions.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/exceptions.js) | `ExceptionsModule` | `GET /api/exceptions`, `POST /api/exceptions/import-csv` | Reconciliation board + CSV bulk importer. |
| [`documents.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/documents.js) | `DocumentsModule` | `GET /api/documents`, `GET /api/documents/{id}/share-link` | Document chasing + WhatsApp share link. |
| [`drafting.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/drafting.js) | `DraftingModule` | `GET /api/drafts`, `POST /api/ai/notice-reply`, `GET /api/drafts/{id}/export` | Drafting workspace + AI co-pilot + PDF export. |
| [`reviews.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/reviews.js) | `ReviewsModule` | `GET /api/reviews`, `PUT /api/reviews/{id}` | 4-stage review pipeline with approve/return. |
| [`audit.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/audit.js) | `AuditModule` | `GET /api/audit-trail` | Immutable activity log viewer. |
| [`booking.js`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/js/booking.js) | `BookingModule` | `POST /api/bookings` | Demo booking modal with form → API submission. |

### Landing Page: [`ledgerdesk-ca-practice-platform.html`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/ledgerdesk-ca-practice-platform.html)
- Includes `<script src="frontend/js/api.js">` and `<script src="frontend/js/booking.js">`.
- All 4 CTA buttons wired to `BookingModule.openModal()`.
- Smooth scroll JS guarded against bare `#` selectors.

### Dashboard App: [`frontend/index.html`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/frontend/index.html)
- Includes all 9 JS feature modules.
- Served by FastAPI at `http://localhost:8000/`.

---

## 3. Gemini AI Co-Pilot Service Pipeline

Located at [`backend/app/ai_agents/gemini_service.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/ai_agents/gemini_service.py):
- **Model Fallback Chain**: `gemini-2.0-flash` → `gemini-1.5-flash` → `gemini-1.5-pro`.
- **Async Execution**: `asyncio.to_thread` wrapping sync SDK calls.
- **Production Grounding**: Includes statutory section citations (CGST Act 2017, Income Tax Act 1961, CBIC Circulars, Supreme Court rulings).
