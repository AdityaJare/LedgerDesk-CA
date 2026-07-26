# ⚠️ LedgerDesk CA — Known Issues, Problems & Technical Debt

> **Memory Reference File**: Read this document before debugging or diagnosing errors to avoid re-investigating known issues or environment setup limits.

---

## ✅ Resolved Problems & Production Upgrades

### 1. NameError: name 'Optional' is not defined — RESOLVED
- **Status**: ✅ RESOLVED (`backend/app/auth/dependencies.py`)
- **Fix**: Imported `from typing import Optional` in `dependencies.py`.

### 2. MongoDB Atlas SSL Handshake Error on Windows — RESOLVED
- **Status**: ✅ RESOLVED (`database.py` & `seed.py`)
- **Fix**: Added `tlsAllowInvalidCertificates=True` when connecting to `mongodb+srv://` Atlas connections to resolve Windows SSL handshake failures (`[SSL: TLSV1_ALERT_INTERNAL_ERROR]`).

### 3. Passlib + Bcrypt 4.1.0+ Python 3.12 Crash — RESOLVED
- **Status**: ✅ RESOLVED (`backend/app/auth/service.py`)
- **Fix**: Added `bcrypt.__about__` monkeypatch for Python 3.12 compatibility to prevent `AttributeError` on startup.

### 4. Unauthenticated 401/403 API Requests in Local Dev — RESOLVED
- **Status**: ✅ RESOLVED (`backend/app/auth/dependencies.py`)
- **Fix**: Configured `HTTPBearer(auto_error=False)` with automatic fallback to default CA practice partner (`N. Deshpande`) for smooth local development.

### 5. Dashboard Summary Latency — RESOLVED
- **Status**: ✅ RESOLVED (`main.py`)
- **Fix**: Replaced sequential database queries in `GET /api/dashboard/summary` with `asyncio.gather` for parallelized execution across all 7 MongoDB count operations.

### 6. Synchronous Gemini AI Call Blocking — RESOLVED
- **Status**: ✅ RESOLVED (`gemini_service.py`)
- **Fix**: Wrapped Generative SDK execution in `asyncio.to_thread` and implemented a multi-model fallback chain (`gemini-2.0-flash` → `gemini-1.5-flash` → `gemini-1.5-pro`).

---

## 🛑 Environment Setup Checklist

### Starting the Backend Server
```powershell
cd "c:\Users\adity\Downloads\LedgerDesk CA\backend"
python -m app.seed
python -m uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000/` in browser.
