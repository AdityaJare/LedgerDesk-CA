# 🎯 LedgerDesk CA — Next Steps & Actionable Roadmap

> **Memory Reference File**: Consult this list to identify priority tasks for future development.

---

## ✅ Completed Production Features

- [x] **Printable Legal Notice Reply Exporter**: `GET /api/drafts/{id}/export`
- [x] **Non-Blocking Async Gemini AI Adapter**: Multi-model fallback chain wrapped in `asyncio.to_thread`
- [x] **Parallelized Dashboard Aggregator**: `asyncio.gather` on `GET /api/dashboard/summary`
- [x] **Statutory Deadline Auto-Escalation Engine**: `POST /api/deadlines/check-escalations`
- [x] **Client Document Share Link & WhatsApp Template**: `GET /api/documents/{id}/share-link`
- [x] **Reconciliation CSV Ingestion Engine**: `POST /api/exceptions/import-csv`
- [x] **Modular Frontend Feature JS Files**: 8 dedicated modules in `frontend/js/`
- [x] **Demo Booking Modal**: Interactive form in `booking.js` → `POST /api/bookings`
- [x] **Fixed querySelector('#') JavaScript crash** in landing page smooth scroll
- [x] **Wired all CTA buttons** (4 "Book a workflow demo" + 1 "Discuss pricing") to booking modal
- [x] **Frontend index.html Integration**: Included all 9 modular feature scripts in `frontend/index.html`
- [x] **Pytest Automated Test Suite**: Created `backend/tests/test_api.py` for FastAPI endpoints

---

## 📌 Upcoming Enhancements

- [ ] **Multi-Tenant Practice Isolation**: Enforce `firm_id` JWT claim filtering across all queries.
- [ ] **Direct WhatsApp Business API Integration**: Connect share-link output to Twilio Cloud API.
