# 🚀 How to Run LedgerDesk CA — Setup, Execution & Error Troubleshooting

This guide provides step-by-step instructions to set up, launch, test, and troubleshoot the **LedgerDesk CA** Practice Operating System.

---

## 📋 1. Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 installed.
- **MongoDB**: Either an active **MongoDB Atlas Cloud Connection** or a local MongoDB server running on `mongodb://localhost:27017`.

---

## 🔑 2. Environment Configuration

Ensure `c:\Users\adity\Downloads\LedgerDesk CA\backend\.env` contains valid parameters:

```env
MONGODB_URL="mongodb+srv://adityajare180_db_user:fYnxImJc7foPHPq1@ledgerdeskca.ianbxzc.mongodb.net/ledgerdesk_ca?retryWrites=true&w=majority"
DB_NAME="ledgerdesk_ca"
JWT_SECRET="supersecretjwtkeyforledgerdeskca2026practiceos"
JWT_ALGORITHM="HS256"
GEMINI_API_KEY="" # Add your Google Gemini API Key here (Optional: system runs in production fallback if empty)
UPLOAD_DIR="./uploads"
PORT=8000
```

---

## ⚡ 3. Step-by-Step Launch Execution

### Step 1: Open Terminal & Navigate to Backend
```powershell
cd "c:\Users\adity\Downloads\LedgerDesk CA\backend"
```

### Step 2: Install Required Python Packages
```powershell
pip install -r requirements.txt
```

### Step 3: Seed Initial CA Practice Data (One-Time Execution)
```powershell
python -m app.seed
```
*Creates sample CA firm users (`partner@ledgerdesk.in`), active clients, statutory deadlines, GSTR-2B mismatches, document chasing items, notice drafts, and audit logs.*

### Step 4: Run Automated Pytest Integration Suite (Optional Verification)
```powershell
pytest tests/
```

### Step 5: Launch FastAPI Development Server
```powershell
python -m uvicorn app.main:app --reload --port 8000
```

---

## 🌐 4. Accessing the Practice Application

Once the server is running:

| Resource | URL | Description |
| :--- | :--- | :--- |
| **Main Practice Dashboard** | `http://localhost:8000/` | Full-stack CA OS workspace (served via FastAPI). |
| **Interactive API Documentation** | `http://localhost:8000/docs` | Swagger UI for testing all 10 domain routers. |
| **ReDoc API Reference** | `http://localhost:8000/redoc` | OpenAPI documentation. |
| **API Health Check** | `http://localhost:8000/api/health` | Service status JSON check. |

---

## 🛠️ 5. Troubleshooting & Common Error Resolutions

### Error 1: `ServerSelectionTimeoutError` / MongoDB Connection Failed
- **Symptom**: Server crashes on startup or API requests hang.
- **Root Cause**: Invalid `MONGODB_URL` or MongoDB Atlas Network Access IP block.
- **Solution**:
  1. Go to MongoDB Atlas → Network Access → Add IP Address `0.0.0.0/0` (Allow access from anywhere).
  2. Alternatively, switch to local MongoDB in `backend/.env`:
     ```env
     MONGODB_URL="mongodb://localhost:27017"
     ```

---

### Error 2: `pydantic.ValidationError` on Startup
- **Symptom**: `ValidationError: 1 validation error for Settings MONGODB_URL Field required`.
- **Root Cause**: `backend/.env` file is missing or lacks `MONGODB_URL` or `JWT_SECRET`.
- **Solution**: Create `backend/.env` using the template provided in Section 2 above.

---

### Error 3: `net::ERR_CONNECTION_REFUSED` at `http://localhost:8000`
- **Symptom**: Browser shows connection refused error.
- **Root Cause**: The FastAPI Uvicorn backend server is not currently running.
- **Solution**: Open Command Prompt / PowerShell, navigate to `backend/`, and execute:
  ```powershell
  python -m uvicorn app.main:app --reload --port 8000
  ```

---

### Error 4: `GEMINI_API_KEY` Empty / Google AI SDK Warning
- **Symptom**: Terminal log says `GEMINI_API_KEY is not set. AI agents will run in fallback production mode.`
- **Root Cause**: No Gemini API Key in `.env`.
- **Solution**: This is **not a fatal error**. LedgerDesk CA includes built-in statutory fallback draft templates (CGST Sec 16(2), Income Tax Act 1961, Bharti Airtel Supreme Court ruling). To use live Google AI, enter your key in `backend/.env`:
  ```env
  GEMINI_API_KEY="AIzaSy..."
  ```

---

### Error 5: Terminal Sandbox `opening NUL for ACL write: Access is denied`
- **Symptom**: Error when attempting to start server from IDE terminal wrappers.
- **Root Cause**: Windows OS security boundary restriction on device `NUL` redirection inside restricted sandboxes.
- **Solution**: Open a standard, native Windows PowerShell or Command Prompt window outside the IDE and run `python -m uvicorn app.main:app --reload --port 8000`.

---

## 🖱️ 6. One-Click Batch Launch (`run.bat`)

You can also start the project instantly by double-clicking `run.bat` located in the root directory!
