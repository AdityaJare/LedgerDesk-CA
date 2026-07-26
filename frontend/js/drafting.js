/* ===== Drafting Workspace Feature Module ===== */
const DraftingModule = {
  async init() {
    this.bindEvents();
    await this.loadDrafts();
  },

  bindEvents() {
    const aiBtn = document.getElementById("btn-ai-notice-reply");
    if (aiBtn) {
      aiBtn.addEventListener("click", () => this.generateAINoticeReply());
    }
  },

  async loadDrafts() {
    try {
      const list = await api.get("/api/drafts");
      this.renderDrafts(list);
    } catch (err) {
      console.error("Failed to load drafts:", err);
    }
  },

  async generateAINoticeReply() {
    const clientName = prompt("Client Name:", "Orbit Buildcon");
    if (!clientName) return;
    const subject = prompt("Notice Subject:", "GST SCN on ITC mismatch for Q1 2026");
    if (!subject) return;
    const body = prompt("Notice Details / Allegations:", "Alleged ITC mismatch of ₹3.2L between GSTR-3B and GSTR-2A for Jul-Sep 2025.");
    if (!body) return;

    try {
      const res = await api.post("/api/ai/notice-reply", {
        client_name: clientName,
        notice_subject: subject,
        notice_body: body
      });
      const outputEl = document.getElementById("ai-draft-output");
      if (outputEl) {
        outputEl.style.display = "block";
        outputEl.innerHTML = `
          <div style="background:var(--surface); border:1px solid var(--teal); border-radius:8px; padding:20px; margin-top:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
              <h4 style="margin:0; color:var(--teal);">AI-Generated Notice Reply Draft</h4>
              <span class="chip chip--review">Draft Only — Human Sign-off Required</span>
            </div>
            <pre style="white-space:pre-wrap; font-family:var(--font); font-size:13px; line-height:1.7; color:var(--text);">${res.draft}</pre>
          </div>
        `;
      } else {
        alert("AI Notice Reply Draft Generated:\n\n" + res.draft);
      }
    } catch (err) {
      alert("AI generation failed: " + err.message);
    }
  },

  async exportDraft(draftId) {
    try {
      const url = `${API_BASE}/api/drafts/${draftId}/export`;
      window.open(url, "_blank");
    } catch (err) {
      alert("Export failed: " + err.message);
    }
  },

  renderDrafts(list) {
    const container = document.getElementById("drafts-list-container");
    if (!container) return;

    if (!list || list.length === 0) {
      container.innerHTML = `<div class="empty-state">No notice reply drafts in workspace.</div>`;
      return;
    }

    container.innerHTML = list.map(item => {
      let stateChip = `<span class="chip chip--draft">${item.state}</span>`;
      if (item.state === "Approved") stateChip = `<span class="chip chip--done">Approved ✓</span>`;
      else if (item.state === "Draft ready") stateChip = `<span class="chip chip--review">Draft Ready</span>`;
      else if (item.state === "Returned") stateChip = `<span class="chip chip--overdue">Returned</span>`;

      const commentsHtml = (item.comments && item.comments.length > 0)
        ? item.comments.map(c => `<div style="font-size:11px; color:var(--text-muted); padding:4px 0; border-top:1px solid var(--border-subtle);"><strong>${c.author}:</strong> ${c.text}</div>`).join("")
        : `<div style="font-size:11px; color:var(--text-muted);">No comments yet.</div>`;

      return `
        <div class="draft-card" style="background:var(--surface); border:1px solid var(--border); padding:16px; border-radius:8px; margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div>
              <h4 style="margin:0; font-size:15px; font-weight:600;">${item.matter}</h4>
              <div style="font-size:12px; color:var(--text-muted);">${item.client_name} — ${item.draft_type} — v${item.version}</div>
            </div>
            ${stateChip}
          </div>
          <div style="font-size:13px; color:var(--text-secondary); margin-bottom:8px;">
            <strong>Prepared By:</strong> ${item.prepared_by} | <strong>Reviewer:</strong> ${item.reviewer} | <strong>Due:</strong> ${item.due_by || 'N/A'}
          </div>
          <div style="margin-bottom:8px;">${commentsHtml}</div>
          <div style="display:flex; gap:8px;">
            <button class="btn btn--primary btn--sm" onclick="DraftingModule.exportDraft('${item.id}')">Export Letterhead PDF</button>
          </div>
        </div>
      `;
    }).join("");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  DraftingModule.init();
});
