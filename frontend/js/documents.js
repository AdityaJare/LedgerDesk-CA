/* ===== Document Chasing Feature Module ===== */
const DocumentsModule = {
  async init() {
    await this.loadDocuments();
  },

  async loadDocuments() {
    try {
      const list = await api.get("/api/documents");
      this.renderDocuments(list);
    } catch (err) {
      console.error("Failed to load documents:", err);
    }
  },

  async sendReminder(docId) {
    try {
      const updated = await api.post(`/api/documents/${docId}/remind`, {});
      alert(`Reminder #${updated.reminder_count} logged! Last response: ${updated.last_response}`);
      await this.loadDocuments();
    } catch (err) {
      alert("Failed to log reminder: " + err.message);
    }
  },

  async getShareLink(docId) {
    try {
      const info = await api.get(`/api/documents/${docId}/share-link`);
      const msg = `WHATSAPP REMINDER TEMPLATE FOR ${info.client_name}:\n\n${info.whatsapp_template}\n\n[Copied to clipboard]`;
      navigator.clipboard.writeText(info.whatsapp_template);
      alert(msg);
    } catch (err) {
      alert("Failed to generate share link: " + err.message);
    }
  },

  renderDocuments(list) {
    const container = document.getElementById("documents-list-container");
    if (!container) return;

    if (!list || list.length === 0) {
      container.innerHTML = `<div class="empty-state">No document chasing requirements active.</div>`;
      return;
    }

    container.innerHTML = list.map(item => `
      <div class="doc-card" style="background:var(--surface); border:1px solid var(--border); padding:16px; border-radius:8px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-weight:600; font-size:14px; margin-bottom:4px;">${item.requested_item} — <span style="color:var(--text-secondary);">${item.client_name}</span></div>
          <div style="font-size:12px; color:var(--text-muted);">
            Task: ${item.related_task} | Reminders Sent: <strong>${item.reminder_count || 0}</strong> | Impact: ${item.impact}
          </div>
        </div>
        <div style="display:flex; gap:8px;">
          <button class="btn btn--secondary btn--sm" onclick="DocumentsModule.getShareLink('${item.id}')">Share Upload Link</button>
          <button class="btn btn--primary btn--sm" onclick="DocumentsModule.sendReminder('${item.id}')">Send Reminder</button>
        </div>
      </div>
    `).join("");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  DocumentsModule.init();
});
