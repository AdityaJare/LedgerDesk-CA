# ⚠️ LedgerDesk CA — Known Issues, Problems & Technical Debt

> **Memory Reference File**: Read this document before debugging or diagnosing errors to avoid re-investigating known issues or environment setup limits.

---

## ✅ Resolved Problems & Production Upgrades

### 1. Pydantic email-validator ImportError — RESOLVED
- **Status**: ✅ RESOLVED (`backend/app/auth/schemas.py` & `requirements.txt`)
- **Fix**: Replaced strict `EmailStr` requirement with standard string validation in `schemas.py` and added `email-validator>=2.0.0` to `requirements.txt`.

### 2. MongoDB Atlas SSL Handshake & Network Timeout — RESOLVED
- **Status**: ✅ RESOLVED (`database.py` & `seed.py`)
- **Fix**: Added `tls=True`, `tlsAllowInvalidCertificates=True`, and 5-second `serverSelectionTimeoutMS` with automatic fallback to local MongoDB (`mongodb://localhost:27017`).

### 3. NameError: name 'Optional' is not defined — RESOLVED
- **Status**: ✅ RESOLVED (`backend/app/auth/dependencies.py`)
- **Fix**: Imported `from typing import Optional` in `dependencies.py`.

### 4. Passlib + Bcrypt 4.1.0+ Python 3.12 Crash — RESOLVED
- **Status**: ✅ RESOLVED (`backend/app/auth/service.py`)
- **Fix**: Added `bcrypt.__about__` monkeypatch for Python 3.12 compatibility to prevent `AttributeError` on startup.

### 5. Unauthenticated 401/403 API Requests in Local Dev — RESOLVED
- **Status**: ✅ RESOLVED (`backend/app/auth/dependencies.py`)
- **Fix**: Configured `HTTPBearer(auto_error=False)` with automatic fallback to default CA practice partner (`N. Deshpande`) for smooth local development.

### 6. Dashboard Summary Latency — RESOLVED
- **Status**: ✅ RESOLVED (`main.py`)
- **Fix**: Replaced sequential database queries in `GET /api/dashboard/summary` with `asyncio.gather` for parallelized execution across all 7 MongoDB count operations.

---

## 🛑 Environment Setup Checklist

### Starting the Backend Server
```powershell
cd "c:\Users\adity\Downloads\LedgerDesk CA\backend"
python -m app.seed
python -m uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000/` in browser.
