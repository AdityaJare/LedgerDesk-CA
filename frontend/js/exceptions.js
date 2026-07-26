/* ===== Exceptions & Reconciliation Module ===== */
const ExceptionsModule = {
  async init() {
    this.bindEvents();
    await this.loadExceptions();
  },

  bindEvents() {
    const csvInput = document.getElementById("exceptions-csv-input");
    if (csvInput) {
      csvInput.addEventListener("change", (e) => this.handleCsvImport(e));
    }
  },

  async loadExceptions() {
    try {
      const list = await api.get("/api/exceptions");
      this.renderExceptions(list);
    } catch (err) {
      console.error("Failed to load exceptions:", err);
    }
  },

  async handleCsvImport(e) {
    const file = e.target.files[0];
    if (!file) return;

    const clientId = prompt("Enter Client ID for this reconciliation upload:", "66a1b2c3d4e5f67890123456");
    if (!clientId) return;

    const clientName = prompt("Enter Client Firm Name:", "Mangal Metals Pvt Ltd") || "Imported Client";

    const formData = new FormData();
    formData.append("file", file);

    try {
      const path = `/api/exceptions/import-csv?client_id=${encodeURIComponent(clientId)}&client_name=${encodeURIComponent(clientName)}`;
      const res = await api.upload(path, formData);
      alert(`Successfully imported ${res.imported_count} reconciliation exception items!`);
      await this.loadExceptions();
    } catch (err) {
      alert("CSV Import failed: " + err.message);
    }
  },

  renderExceptions(list) {
    const container = document.getElementById("exceptions-list-container");
    if (!container) return;

    if (!list || list.length === 0) {
      container.innerHTML = `<div class="empty-state">No reconciliation breaks or mismatches open.</div>`;
      return;
    }

    container.innerHTML = list.map(item => `
      <div class="exception-card" style="background:var(--surface); border:1px solid var(--border); padding:16px; border-radius:8px; margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <h4 style="margin:0; font-size:15px; font-weight:600;">${item.client_name} — <span style="color:var(--teal);">${item.type}</span></h4>
          <span class="chip chip--mismatch">${item.state}</span>
        </div>
        <div style="font-size:13px; color:var(--text-secondary); margin-bottom:8px;">
          <strong>Affected Entries:</strong> ${item.affected_entries} | 
          <strong>Value Impact:</strong> <span style="color:var(--error); font-weight:600;">${item.value_impact}</span> | 
          <strong>Age:</strong> ${item.age}
        </div>
        <div style="font-size:12px; color:var(--text-muted);">
          <strong>Assigned:</strong> ${item.assigned_to || 'Unassigned'} | 
          <strong>Next Action:</strong> ${item.next_action || 'Pending verification'}
        </div>
      </div>
    `).join("");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  ExceptionsModule.init();
});
