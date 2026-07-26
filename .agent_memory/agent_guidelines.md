# 📖 LedgerDesk CA — AI Agent Operating Guidelines & Token Efficiency Protocol

> **Mandatory Protocol for AI Agents**: Read and follow these rules strictly upon entering this codebase.

---

## 💡 Core Objective
Prevent unnecessary token consumption, long file re-reads, duplicate code searches, and API credit burn when working on the LedgerDesk CA codebase.

---

## 📋 Standard Agent Execution Protocol

### Step 1: Session Initialization (Fast Context Boot)
Upon starting any task on this project:
1. Open and read [`.agent_memory/00_QUICK_START.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/00_QUICK_START.md).
2. Check [`.agent_memory/query_history.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/query_history.md) to understand past context and user intent.
3. Review [`.agent_memory/main_problems.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/main_problems.md) if debugging or troubleshooting.

> **DO NOT** scan the entire codebase or read multiple backend files unless specifically required by the user prompt.

---

### Step 2: Task Execution & Modification
- Use `view_file` with precise `StartLine` and `EndLine` parameters when reading source files. Do not retrieve 800+ lines at once if only modifying a router function.
- Prefer targeted `replace_file_content` over overwriting whole files.
- Always preserve existing API contracts and database schemas documented in [`architecture.md`](file:///c:/Users/adity/Downloads/LedgerDesk%20CA/.agent_memory/architecture.md).

---

### Step 3: Session Handoff & Memory Update (Before Completing Task)
Before ending your turn or delivering the final output to the user:
1. **Append to `query_history.md`**: Log the prompt, summary of changes, created files, and task status.
2. **Update `next_steps.md`**: Mark completed checklist items and add newly discovered follow-up tasks.
3. **Update `main_problems.md`** (if new bugs or limits were identified).
4. **Update `developing_features.md`** (if feature state changed).

---

## ⚡ Credit & Token Preservation Rules
1. **Never perform repetitive full-directory searches** when an exact path is already documented in `.agent_memory/architecture.md`.
2. **Never guess API endpoints or database schemas**—verify with `.agent_memory/architecture.md` first.
3. **Keep line-level code edits tight and localized**.
4. **Always leave the `.agent_memory/` directory updated** so the next agent can resume work instantly without credit loss.
