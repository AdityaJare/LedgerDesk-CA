# 🚀 LedgerDesk CA — Agent Quick Start & Index

> **Token-Efficiency Warning**: AI agents MUST read this quick start index first before performing deep directory searches or file views. Conserve context window credits by leveraging pre-indexed summaries.

---

## 📌 Executive Summary
**LedgerDesk CA** is an **exception-driven Practice Operating System** designed specifically for Indian Chartered Accountant (CA) firms handling multi-client statutory compliance, audits, notice replies, and client document chasing.

- **Workspace Path**: `c:\Users\adity\Downloads\LedgerDesk CA`
- **Primary Tech Stack**: Python 3.12 (FastAPI, Uvicorn, Motor/MongoDB, PyJWT) + Vanilla HTML5/CSS3/ES6 JS + Google Gemini AI.
- **Run Guide**: [`HOW_TO_RUN.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/HOW_TO_RUN.md) & 1-click launcher [`run.bat`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/run.bat).
- **Production Status**: 🟢 Fully production-ready with async multi-model Gemini fallbacks, official letterhead notice exporters, automated deadline escalations, and CSV reconciliation importers.

---

## ⚡ Quick Navigation Index

| Memory File | Purpose | When to Inspect |
| :--- | :--- | :--- |
| [`HOW_TO_RUN.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/HOW_TO_RUN.md) | Comprehensive setup, run commands, batch scripts & troubleshooting guide. | When starting or debugging local server execution. |
| [`architecture.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/architecture.md) | Full architectural map, DB schemas, API endpoints, and AI pipeline details. | Before modifying backend routers, database queries, or UI flows. |
| [`query_history.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/query_history.md) | Chronological log of agent prompts, past tasks, and structural decisions. | When reviewing previous changes or user requests. |
| [`main_problems.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/main_problems.md) | Known issues, bugs, resolved bottlenecks, and operational limits. | Before debugging or diagnosing runtime errors. |
| [`next_steps.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/next_steps.md) | Active task backlog, immediate upcoming features, and roadmap priorities. | When deciding what to work on next. |
| [`developing_features.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/developing_features.md) | Technical specs and progress for production features. | When continuing work on active feature modules. |
| [`agent_guidelines.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/agent_guidelines.md) | Protocol for AI agents to update memory and conserve token consumption. | Whenever starting a session or finishing a task. |

---

## 💻 Essential Commands

### 1. One-Click Batch Launch (Windows)
Double-click [`run.bat`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/run.bat) in the project root.

### 2. Manual Commands
```powershell
# Navigate to backend directory
cd "c:\Users\adity\Downloads\LedgerDesk CA\backend"

# Install dependencies
pip install -r requirements.txt

# Seed initial database
python -m app.seed

# Launch FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```
- **Main App**: `http://localhost:8000/`
- **Swagger Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`
