/* ===== Audit Trail Feature Module ===== */
const AuditModule = {
  async init() {
    await this.loadAuditLogs();
  },

  async loadAuditLogs() {
    try {
      const logs = await api.get("/api/audit-trail?limit=50");
      this.renderLogs(logs);
    } catch (err) {
      console.error("Failed to load audit trail:", err);
    }
  },

  renderLogs(logs) {
    const container = document.getElementById("audit-log-container");
    if (!container) return;

    if (!logs || logs.length === 0) {
      container.innerHTML = `<div class="empty-state">No audit entries recorded yet.</div>`;
      return;
    }

    container.innerHTML = logs.map(item => {
      const ts = item.timestamp ? new Date(item.timestamp).toLocaleString("en-IN") : "";
      let actionIcon = "📝";
      if (item.action.includes("create")) actionIcon = "➕";
      else if (item.action.includes("update")) actionIcon = "✏️";
      else if (item.action.includes("approve")) actionIcon = "✅";
      else if (item.action.includes("export")) actionIcon = "📤";
      else if (item.action.includes("reminder")) actionIcon = "🔔";
      else if (item.action.includes("escalat")) actionIcon = "⚠️";
      else if (item.action.includes("ai_")) actionIcon = "🤖";
      else if (item.action.includes("import")) actionIcon = "📥";

      return `
        <div style="display:flex; align-items:flex-start; gap:12px; padding:10px 0; border-bottom:1px solid var(--border-subtle);">
          <span style="font-size:16px; flex-shrink:0;">${actionIcon}</span>
          <div style="flex:1; min-width:0;">
            <div style="font-size:13px; font-weight:500; color:var(--text);">${item.action.replace(/_/g, ' ').toUpperCase()}</div>
            <div style="font-size:12px; color:var(--text-secondary);">${item.details || ''}</div>
          </div>
          <div style="font-size:11px; color:var(--text-muted); white-space:nowrap;">${ts}</div>
        </div>
      `;
    }).join("");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  AuditModule.init();
});
