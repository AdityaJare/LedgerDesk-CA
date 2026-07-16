/* ===== LedgerDesk CA — Dashboard Application Controller ===== */

let currentModule = "overview";
const toastContainer = document.getElementById("toast-container");

// --- Toast ---
function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast toast--${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// --- Chip helper ---
function statusChip(status) {
  const map = {
    "pending": "chip--due", "in_prep": "chip--progress", "awaiting_docs": "chip--waiting",
    "in_review": "chip--review", "filed": "chip--done", "overdue": "chip--overdue",
    "Open": "chip--open", "In progress": "chip--progress", "Pending review": "chip--review",
    "Escalated": "chip--overdue", "Resolved": "chip--done",
    "Awaiting client": "chip--due", "Partial received": "chip--progress", "Received": "chip--done", "Escalate": "chip--overdue",
    "Requested": "chip--draft", "Draft ready": "chip--review", "Returned": "chip--overdue", "Approved": "chip--done",
    "Awaiting manager": "chip--due", "Awaiting partner": "chip--review", "Exported": "chip--done",
    "Not exported": "chip--draft",
  };
  return `<span class="chip ${map[status] || 'chip--draft'}">${status}</span>`;
}

// --- Init ---
document.addEventListener("DOMContentLoaded", async () => {
  if (!api.isAuthenticated()) { window.location.href = "/login"; return; }

  const user = api.getUser();
  document.getElementById("user-name").textContent = user.name;
  document.getElementById("user-role").textContent = user.role;
  document.getElementById("user-avatar").textContent = user.name.charAt(0).toUpperCase();

  // Date
  const now = new Date();
  document.getElementById("topbar-date").textContent = now.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

  // Navigation
  document.querySelectorAll(".dash-nav-item[data-module]").forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      switchModule(item.dataset.module);
    });
  });

  // Sidebar toggle (mobile)
  document.getElementById("sidebar-toggle")?.addEventListener("click", () => {
    document.getElementById("dash-sidebar").classList.toggle("open");
  });

  // Theme
  document.getElementById("theme-btn")?.addEventListener("click", toggleTheme);

  // Logout
  document.getElementById("logout-btn")?.addEventListener("click", api.logout);

  // Load overview
  switchModule("overview");
});

async function switchModule(mod) {
  currentModule = mod;
  document.querySelectorAll(".dash-nav-item").forEach(i => i.classList.remove("active"));
  document.querySelector(`.dash-nav-item[data-module="${mod}"]`)?.classList.add("active");
  // Close sidebar on mobile
  document.getElementById("dash-sidebar")?.classList.remove("open");

  const canvas = document.getElementById("content-canvas");
  canvas.innerHTML = '<div class="loading">Loading...</div>';

  try {
    switch (mod) {
      case "overview": await renderOverview(canvas); break;
      case "deadlines": await renderDeadlines(canvas); break;
      case "exceptions": await renderExceptions(canvas); break;
      case "documents": await renderDocuments(canvas); break;
      case "drafting": await renderDrafting(canvas); break;
      case "reviews": await renderReviews(canvas); break;
      case "clients": await renderClients(canvas); break;
      case "ai-agents": await renderAIAgents(canvas); break;
      default: canvas.innerHTML = '<div class="empty-state">Module not found</div>';
    }
  } catch (err) {
    canvas.innerHTML = `<div class="empty-state" style="color:var(--error)">Error: ${err.message}</div>`;
  }
}

// ==================== MODULE RENDERERS ====================

// --- Overview ---
async function renderOverview(el) {
  const summary = await api.get("/api/dashboard/summary");
  el.innerHTML = `
    <h1 class="dash-content__title">Dashboard</h1>
    <div class="summary-grid">
      <div class="summary-card summary-card--danger"><div class="summary-card__value">${summary.overdue_deadlines}</div><div class="summary-card__label">Overdue</div></div>
      <div class="summary-card summary-card--warning"><div class="summary-card__value">${summary.pending_deadlines}</div><div class="summary-card__label">Pending Deadlines</div></div>
      <div class="summary-card summary-card--danger"><div class="summary-card__value">${summary.open_exceptions}</div><div class="summary-card__label">Open Exceptions</div></div>
      <div class="summary-card summary-card--warning"><div class="summary-card__value">${summary.awaiting_documents}</div><div class="summary-card__label">Awaiting Docs</div></div>
      <div class="summary-card summary-card--info"><div class="summary-card__value">${summary.drafts_in_progress}</div><div class="summary-card__label">Drafts Active</div></div>
      <div class="summary-card summary-card--info"><div class="summary-card__value">${summary.pending_reviews}</div><div class="summary-card__label">Pending Reviews</div></div>
      <div class="summary-card"><div class="summary-card__value">${summary.total_clients}</div><div class="summary-card__label">Active Clients</div></div>
    </div>
    <div id="overview-deadlines"></div>
    <div id="overview-exceptions"></div>
  `;
  // Quick panels
  await renderDeadlinePanel(document.getElementById("overview-deadlines"), "today");
  await renderExceptionPanel(document.getElementById("overview-exceptions"));
}

// --- Deadlines ---
async function renderDeadlines(el) {
  el.innerHTML = `
    <h1 class="dash-content__title">Statutory Deadlines</h1>
    <div class="data-panel">
      <div class="data-panel__header">
        <span class="data-panel__title">Due Dates</span>
        <div class="data-panel__actions">
          <button class="data-panel__filter active" data-tf="all">All</button>
          <button class="data-panel__filter" data-tf="today">Today</button>
          <button class="data-panel__filter" data-tf="next3">Next 3 days</button>
          <button class="data-panel__filter" data-tf="overdue">Overdue</button>
        </div>
      </div>
      <div class="data-panel__body" id="deadlines-body"><div class="loading">Loading...</div></div>
    </div>
  `;
  el.querySelectorAll(".data-panel__filter").forEach(btn => {
    btn.addEventListener("click", async () => {
      el.querySelectorAll(".data-panel__filter").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      await renderDeadlinePanel(document.getElementById("deadlines-body"), btn.dataset.tf);
    });
  });
  await renderDeadlinePanel(document.getElementById("deadlines-body"), "all");
}

async function renderDeadlinePanel(el, timeframe) {
  const deadlines = await api.get(`/api/deadlines?timeframe=${timeframe || ""}`);
  if (!deadlines.length) { el.innerHTML = '<div class="empty-state">No deadlines matching this filter</div>'; return; }
  el.innerHTML = `
    <table class="d-table"><thead><tr>
      <th>Client</th><th>Obligation</th><th>Period</th><th>Due</th><th>Owner</th><th>Status</th><th>Days</th>
    </tr></thead><tbody>
      ${deadlines.map(d => `
        <tr class="${d.days_left < 0 ? 'row-overdue' : d.days_left <= 2 ? 'row-urgent' : ''}">
          <td>${d.client_name}</td><td>${d.obligation}</td><td>${d.period}</td>
          <td>${new Date(d.due_date).toLocaleDateString("en-IN",{day:"numeric",month:"short"})}</td>
          <td>${d.owner}</td><td>${statusChip(d.status)}</td>
          <td>${d.days_left < 0 ? `<span style="color:var(--error);font-weight:600">${d.days_left}d</span>` : `${d.days_left}d`}</td>
        </tr>
      `).join("")}
    </tbody></table>
  `;
}

// --- Exceptions ---
async function renderExceptions(el) {
  el.innerHTML = `
    <h1 class="dash-content__title">Exception Triage</h1>
    <div class="data-panel">
      <div class="data-panel__header"><span class="data-panel__title">Mismatches & Breaks</span></div>
      <div class="data-panel__body" id="exceptions-body"><div class="loading">Loading...</div></div>
    </div>
  `;
  await renderExceptionPanel(document.getElementById("exceptions-body"));
}

async function renderExceptionPanel(el) {
  const exceptions = await api.get("/api/exceptions");
  if (!exceptions.length) { el.innerHTML = '<div class="empty-state">No open exceptions</div>'; return; }
  el.innerHTML = `
    <table class="d-table"><thead><tr>
      <th>Client</th><th>Type</th><th>Entries</th><th>Value</th><th>Age</th><th>Assigned</th><th>State</th>
    </tr></thead><tbody>
      ${exceptions.map(e => `
        <tr>
          <td>${e.client_name}</td><td>${e.type}</td><td>${e.affected_entries}</td>
          <td>${e.value_impact}</td><td>${e.age}</td><td>${e.assigned_to}</td>
          <td>${statusChip(e.state)}</td>
        </tr>
      `).join("")}
    </tbody></table>
  `;
}

// --- Documents ---
async function renderDocuments(el) {
  const docs = await api.get("/api/documents");
  el.innerHTML = `
    <h1 class="dash-content__title">Document Tracking</h1>
    <div class="data-panel">
      <div class="data-panel__header"><span class="data-panel__title">Client Document Requests</span></div>
      <div class="data-panel__body">
        ${!docs.length ? '<div class="empty-state">No document requests</div>' : `
        <table class="d-table"><thead><tr>
          <th>Client</th><th>Item</th><th>Task</th><th>Reminders</th><th>Last Response</th><th>Impact</th><th>Status</th><th>Action</th>
        </tr></thead><tbody>
          ${docs.map(d => `
            <tr>
              <td>${d.client_name}</td><td>${d.requested_item}</td><td>${d.related_task}</td>
              <td>${d.reminder_count}</td><td>${d.last_response}</td><td>${d.impact}</td>
              <td>${statusChip(d.status)}</td>
              <td>${d.status !== "Received" ? `<button class="d-table__action" onclick="sendReminder('${d.id}')">Remind</button>` : "—"}</td>
            </tr>
          `).join("")}
        </tbody></table>`}
      </div>
    </div>
  `;
}
async function sendReminder(docId) {
  try {
    await api.post(`/api/documents/${docId}/remind`);
    showToast("Reminder sent successfully");
    switchModule("documents");
  } catch (err) { showToast(err.message, "error"); }
}

// --- Drafting ---
async function renderDrafting(el) {
  const drafts = await api.get("/api/drafts");
  el.innerHTML = `
    <h1 class="dash-content__title">Drafting Queue</h1>
    ${!drafts.length ? '<div class="empty-state">No drafts</div>' : drafts.map(d => `
      <div class="data-panel">
        <div class="data-panel__header">
          <span class="data-panel__title">${d.matter} — ${d.client_name}</span>
          <div class="data-panel__actions">
            <span class="chip chip--draft">v${d.version}</span>
            ${statusChip(d.state)}
          </div>
        </div>
        <div class="data-panel__body">
          <div class="draft-view">
            <div class="draft-view__main">
              <div class="draft-view__label">Draft Content</div>
              <div class="draft-view__content">${d.content}</div>
            </div>
            <div class="draft-view__sidebar">
              <div class="draft-view__label">Prepared by</div>
              <div class="draft-view__meta">${d.prepared_by}</div>
              <div class="draft-view__label">Reviewer</div>
              <div class="draft-view__meta">${d.reviewer}</div>
              <div class="draft-view__label">Due by</div>
              <div class="draft-view__meta">${d.due_by}</div>
              ${d.comments.length ? `
                <div class="draft-view__label">Comments</div>
                ${d.comments.map(c => `<div class="draft-view__meta"><strong>${c.author}:</strong> ${c.text}</div>`).join("")}
              ` : ""}
            </div>
          </div>
        </div>
      </div>
    `).join("")}
  `;
}

// --- Reviews ---
async function renderReviews(el) {
  const reviews = await api.get("/api/reviews");
  el.innerHTML = `
    <h1 class="dash-content__title">Review & Sign-off</h1>
    <div class="data-panel">
      <div class="data-panel__header"><span class="data-panel__title">Sign-off Timeline</span></div>
      <div class="data-panel__body">
        <div class="timeline">
          ${reviews.map(r => {
            const dt = new Date(r.timestamp);
            const timeStr = dt.toLocaleDateString("en-IN", {day:"numeric",month:"short"}) + ", " + dt.toLocaleTimeString("en-IN", {hour:"2-digit",minute:"2-digit"});
            const typeClass = r.status === "Approved" ? "approved" : r.status === "Returned" ? "returned" : "submitted";
            return `
              <div class="timeline-entry timeline-entry--${typeClass}">
                <div class="timeline-entry__time">${timeStr}</div>
                <div class="timeline-entry__dot"></div>
                <div class="timeline-entry__content">
                  <strong>${r.reviewer}</strong> ${r.status === "Approved" ? "approved" : r.status === "Returned" ? "returned" : "reviewing"}
                  <strong>${r.item_name}</strong> for ${r.client_name} · ${r.version}
                  ${r.export_state === "Exported" ? '<span class="chip chip--done" style="margin-left:4px">Exported</span>' : ""}
                  ${r.status !== "Approved" && r.status !== "Returned" ? `
                    <div style="margin-top:4px">
                      <button class="d-table__action" onclick="approveReview('${r.id}')">Approve</button>
                      <button class="d-table__action" style="color:var(--warning)" onclick="returnReview('${r.id}')">Return</button>
                    </div>
                  ` : ""}
                </div>
              </div>
            `;
          }).join("")}
        </div>
      </div>
    </div>
  `;
}
async function approveReview(id) {
  try {
    await api.put(`/api/reviews/${id}`, { status: "Approved", export_state: "Exported" });
    showToast("Review approved and exported");
    switchModule("reviews");
  } catch (err) { showToast(err.message, "error"); }
}
async function returnReview(id) {
  const comment = prompt("Enter return comment:");
  if (!comment) return;
  try {
    await api.put(`/api/reviews/${id}`, { status: "Returned", new_comment: comment });
    showToast("Review returned with comments");
    switchModule("reviews");
  } catch (err) { showToast(err.message, "error"); }
}

// --- Clients ---
async function renderClients(el) {
  const clients = await api.get("/api/clients");
  el.innerHTML = `
    <h1 class="dash-content__title">Client Directory</h1>
    <div style="margin-bottom:var(--sp-4)">
      <button class="btn btn--primary" onclick="showAddClientModal()">+ Add Client</button>
    </div>
    <div class="data-panel">
      <div class="data-panel__header"><span class="data-panel__title">Active Clients (${clients.length})</span></div>
      <div class="data-panel__body">
        <table class="d-table"><thead><tr>
          <th>Name</th><th>GSTIN</th><th>PAN</th><th>Contact</th><th>Status</th>
        </tr></thead><tbody>
          ${clients.map(c => `
            <tr><td>${c.name}</td><td>${c.gstin || "—"}</td><td>${c.pan || "—"}</td><td>${c.contact || "—"}</td><td>${statusChip(c.status)}</td></tr>
          `).join("")}
        </tbody></table>
      </div>
    </div>
  `;
}
function showAddClientModal() {
  const overlay = document.getElementById("modal-overlay");
  const modal = document.getElementById("modal-content");
  modal.innerHTML = `
    <h2>Add New Client</h2>
    <p>Enter client details to register them in the workspace.</p>
    <form id="add-client-form">
      <div class="form-group"><label>Company Name</label><input id="c-name" required placeholder="e.g. Mangal Metals Pvt Ltd"></div>
      <div class="form-group"><label>GSTIN</label><input id="c-gstin" placeholder="27AAACM1234F1Z5"></div>
      <div class="form-group"><label>PAN</label><input id="c-pan" placeholder="AAACM1234F"></div>
      <div class="form-group"><label>Contact</label><input id="c-contact" placeholder="+91 98765 43210"></div>
      <button type="submit" class="btn btn--primary btn--lg" style="width:100%;justify-content:center">Save Client</button>
    </form>
  `;
  overlay.classList.add("visible");
  document.getElementById("add-client-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await api.post("/api/clients", {
        name: document.getElementById("c-name").value,
        gstin: document.getElementById("c-gstin").value || "",
        pan: document.getElementById("c-pan").value || "",
        contact: document.getElementById("c-contact").value || "",
        status: "active"
      });
      overlay.classList.remove("visible");
      showToast("Client added successfully");
      switchModule("clients");
    } catch (err) { showToast(err.message, "error"); }
  });
}

// --- AI Agents ---
async function renderAIAgents(el) {
  el.innerHTML = `
    <h1 class="dash-content__title">AI Agents</h1>
    <div class="ai-panel">
      <div class="ai-panel__badge">Draft only</div>
      <h3>Notice Reply Agent</h3>
      <p>Drafts GST/IT notice replies with section citations. Output requires reviewer sign-off.</p>
      <div class="form-group"><label>Client Name</label><input id="ai-nr-client" placeholder="e.g. Orbit Buildcon"></div>
      <div class="form-group"><label>Notice Subject</label><input id="ai-nr-subject" placeholder="e.g. ITC mismatch GSTR-3B vs 2A"></div>
      <textarea id="ai-nr-body" placeholder="Paste notice details here..."></textarea>
      <button class="btn btn--primary" onclick="runNoticeAgent()">Generate Draft</button>
      <div id="ai-nr-result" class="ai-panel__result"></div>
      <div id="ai-nr-disclaimer" class="ai-panel__disclaimer">⚠ This is an AI-generated draft. Reviewer approval is required before submission.</div>
    </div>
    <div class="ai-panel">
      <div class="ai-panel__badge">Draft only</div>
      <h3>Reconciliation Agent</h3>
      <p>Analyzes GSTR-2A vs books, 26AS vs TDS ledger, and bank vs cash book mismatches.</p>
      <div class="form-group"><label>Client Name</label><input id="ai-rc-client" placeholder="Client name"></div>
      <div class="form-group"><label>Exception Type</label><input id="ai-rc-type" placeholder="e.g. GSTR-2A mismatch"></div>
      <div class="form-group"><label>Entries Count</label><input id="ai-rc-entries" type="number" placeholder="14"></div>
      <div class="form-group"><label>Value Impact</label><input id="ai-rc-value" placeholder="₹2.8L"></div>
      <button class="btn btn--primary" onclick="runReconAgent()">Analyze</button>
      <div id="ai-rc-result" class="ai-panel__result"></div>
      <div id="ai-rc-disclaimer" class="ai-panel__disclaimer">⚠ AI analysis is for triage support only. No auto-adjustments will be made.</div>
    </div>
    <div class="ai-panel">
      <div class="ai-panel__badge">Draft only</div>
      <h3>Law Research Agent</h3>
      <p>Returns cited legal sections, circulars, and case law relevant to a query.</p>
      <textarea id="ai-lr-query" placeholder="e.g. Applicability of Section 16(4) CGST for ITC claimed after due date"></textarea>
      <button class="btn btn--primary" onclick="runLawAgent()">Research</button>
      <div id="ai-lr-result" class="ai-panel__result"></div>
      <div id="ai-lr-disclaimer" class="ai-panel__disclaimer">⚠ Citations only — not legal advice. Reviewer verification needed.</div>
    </div>
    <div class="ai-panel">
      <div class="ai-panel__badge">Draft only</div>
      <h3>Client Follow-up Agent</h3>
      <p>Generates polite follow-up messages for pending documents based on deadline proximity.</p>
      <div class="form-group"><label>Client Name</label><input id="ai-fu-client" placeholder="Client name"></div>
      <div class="form-group"><label>Requested Item</label><input id="ai-fu-item" placeholder="e.g. Purchase register Jun-26"></div>
      <div class="form-group"><label>Deadline Impact</label><input id="ai-fu-impact" placeholder="e.g. GSTR-3B filing at risk"></div>
      <button class="btn btn--primary" onclick="runFollowupAgent()">Generate Message</button>
      <div id="ai-fu-result" class="ai-panel__result"></div>
      <div id="ai-fu-disclaimer" class="ai-panel__disclaimer">⚠ Approval required before sending to client.</div>
    </div>
  `;
}
async function runNoticeAgent() {
  const result = document.getElementById("ai-nr-result");
  const disc = document.getElementById("ai-nr-disclaimer");
  result.textContent = "Generating..."; result.classList.add("visible");
  try {
    const data = await api.post("/api/ai/notice-reply", {
      client_name: document.getElementById("ai-nr-client").value,
      notice_subject: document.getElementById("ai-nr-subject").value,
      notice_body: document.getElementById("ai-nr-body").value,
    });
    result.textContent = data.draft; disc.classList.add("visible");
  } catch (err) { result.textContent = "Error: " + err.message; }
}
async function runReconAgent() {
  const result = document.getElementById("ai-rc-result");
  const disc = document.getElementById("ai-rc-disclaimer");
  result.textContent = "Analyzing..."; result.classList.add("visible");
  try {
    const data = await api.post("/api/ai/reconciliation", {
      client_name: document.getElementById("ai-rc-client").value,
      exception_type: document.getElementById("ai-rc-type").value,
      entries_count: parseInt(document.getElementById("ai-rc-entries").value) || 1,
      value_impact: document.getElementById("ai-rc-value").value,
    });
    result.textContent = data.analysis; disc.classList.add("visible");
  } catch (err) { result.textContent = "Error: " + err.message; }
}
async function runLawAgent() {
  const result = document.getElementById("ai-lr-result");
  const disc = document.getElementById("ai-lr-disclaimer");
  result.textContent = "Researching..."; result.classList.add("visible");
  try {
    const data = await api.post("/api/ai/law-research", {
      query: document.getElementById("ai-lr-query").value,
    });
    result.textContent = data.research; disc.classList.add("visible");
  } catch (err) { result.textContent = "Error: " + err.message; }
}
async function runFollowupAgent() {
  const result = document.getElementById("ai-fu-result");
  const disc = document.getElementById("ai-fu-disclaimer");
  result.textContent = "Generating..."; result.classList.add("visible");
  try {
    const data = await api.post("/api/ai/followup", {
      client_name: document.getElementById("ai-fu-client").value,
      requested_item: document.getElementById("ai-fu-item").value,
      deadline_impact: document.getElementById("ai-fu-impact").value,
    });
    result.textContent = data.message_draft; disc.classList.add("visible");
  } catch (err) { result.textContent = "Error: " + err.message; }
}

// --- Close modal ---
function closeModal() {
  document.getElementById("modal-overlay")?.classList.remove("visible");
}
