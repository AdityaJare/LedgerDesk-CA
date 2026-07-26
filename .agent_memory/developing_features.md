# 🛠️ LedgerDesk CA — Active & Production Feature Specifications

> **Memory Reference File**: Use this document to check technical specifications, status, and feature contracts for production features.

---

## 🟢 Production Ready & Deployed Features

### 1. Notice Reply Letterhead Exporter
- **Module**: [`backend/app/drafting/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/drafting/router.py)
- **Status**: 🟢 Production Ready (`GET /api/drafts/{draft_id}/export`)
- **Specification**: Renders formatted HTML legal submissions with official CA firm letterhead, case metadata, prepared by / reviewer tags, section citations, partner sign-off blocks, and immutable audit logs.

### 2. Async Multi-Model Gemini Co-Pilot Pipeline
- **Module**: [`backend/app/ai_agents/gemini_service.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/ai_agents/gemini_service.py)
- **Status**: 🟢 Production Ready
- **Specification**: Non-blocking `asyncio.to_thread` execution with automatic model fallback (`gemini-2.0-flash` → `gemini-1.5-flash` → `gemini-1.5-pro`) and grounded statutory draft templates for CGST Act Sec 16(2), CBIC Circular 183/15/2022, and Supreme Court Bharti Airtel ruling.

### 3. Statutory Deadline Escalation Engine
- **Module**: [`backend/app/deadlines/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/deadlines/router.py)
- **Status**: 🟢 Production Ready (`POST /api/deadlines/check-escalations`)
- **Specification**: Evaluates pending filings against current date and automatically escalates status to `overdue` with logged audit events.

### 4. Client Document Share Link & Reminder Template
- **Module**: [`backend/app/documents/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/documents/router.py)
- **Status**: 🟢 Production Ready (`GET /api/documents/{doc_id}/share-link`)
- **Specification**: Generates secure upload URLs and ready-to-copy WhatsApp/Email notification text formatted for client communications.

### 5. Reconciliation CSV Bulk Importer
- **Module**: [`backend/app/exceptions_module/router.py`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/backend/app/exceptions_module/router.py)
- **Status**: 🟢 Production Ready (`POST /api/exceptions/import-csv`)
- **Specification**: Ingests GSTR-2B vs Books reconciliation CSV spreadsheets and populates exception control records automatically.
