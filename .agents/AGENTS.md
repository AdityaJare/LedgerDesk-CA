# 🤖 Antigravity AI Agent Rules & Workspace Memory System — LedgerDesk CA

> **System Memory Instruction**: This repository contains a pre-indexed, token-efficient memory store located at `.agent_memory/`. Every AI agent operating in this workspace MUST follow this instruction set to maximize efficiency and minimize credit usage.

---

## ⚡ MANDATORY BOOTSTRAP PROTOCOL

Whenever an AI agent is initialized in this project or receives a new user task:

1. **IMMEDIATE FIRST STEP — Check `.agent_memory/` Index**:
   - Before searching source code or listing project directories, inspect [`.agent_memory/00_QUICK_START.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/00_QUICK_START.md).
   - Refer to [`.agent_memory/architecture.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/architecture.md) for database schemas, API routes, and system components.

2. **Check Current Issues & History**:
   - Check [`.agent_memory/main_problems.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/main_problems.md) for known environment limits or active bugs.
   - Check [`.agent_memory/query_history.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/query_history.md) to see prior agent actions.

3. **Conserve Token Context & API Credits**:
   - Do NOT run wide-scale code searches or inspect full source files if relevant paths/schemas are already documented in `.agent_memory/`.
   - Perform targeted file views and localized edits.

4. **Task Completion Handoff**:
   - Before completing your turn, append a summary of your action to [`.agent_memory/query_history.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/query_history.md).
   - If features were modified, update [`.agent_memory/next_steps.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/next_steps.md) and [`.agent_memory/developing_features.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/developing_features.md).

---

## 🏗️ Project Technical Context at a Glance

- **Domain**: Indian CA Practice Operating System (Statutory compliance, notice replies, audit reviews, document chasing).
- **Backend Stack**: Python 3.12, FastAPI, Async MongoDB (`motor`), PyJWT, Passlib, Uvicorn, Google Gemini API SDK.
- **Frontend Stack**: Vanilla HTML5, CSS3 Custom Properties, ES6 JS (Fetch API).
- **Backend Entry Point**: `backend/app/main.py`
- **Frontend Entry Point**: `frontend/index.html` (served at `http://localhost:8000/`)

---

## 📌 Memory Files Directory Map

```
c:\Users\adity\Downloads\LedgerDesk CA\
 ├── .agent_memory/
 │    ├── 00_QUICK_START.md      <-- Entry point & quick index
 │    ├── architecture.md        <-- API endpoints & DB schemas
 │    ├── query_history.md       <-- Prompt history & change log
 │    ├── main_problems.md       <-- Known bugs & tech debt
 │    ├── next_steps.md          <-- Active tasks & backlog
 │    ├── developing_features.md <-- Technical specs of active features
 │    └── agent_guidelines.md    <-- Token-saving instructions
 └── .agents/
      └── AGENTS.md              <-- Antigravity Workspace System Memory Rule
```
