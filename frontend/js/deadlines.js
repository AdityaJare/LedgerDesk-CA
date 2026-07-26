/* ===== Statutory Deadlines Feature Module ===== */
const DeadlinesModule = {
  currentFilter: "all",

  async init() {
    this.bindEvents();
    await this.loadDeadlines();
  },

  bindEvents() {
    const filterBtns = document.querySelectorAll("[data-deadline-filter]");
    filterBtns.forEach(btn => {
      btn.addEventListener("click", (e) => {
        filterBtns.forEach(b => b.classList.remove("active"));
        e.target.classList.add("active");
        this.currentFilter = e.target.getAttribute("data-deadline-filter");
        this.loadDeadlines();
      });
    });

    const escalateBtn = document.getElementById("btn-check-escalations");
    if (escalateBtn) {
      escalateBtn.addEventListener("click", () => this.runEscalationEngine());
    }
  },

  async loadDeadlines() {
    try {
      const path = this.currentFilter === "all" 
        ? "/api/deadlines" 
        : `/api/deadlines?filter_type=${encodeURIComponent(this.currentFilter)}`;
      const list = await api.get(path);
      this.renderTable(list);
    } catch (err) {
      console.error("Failed to load deadlines:", err);
    }
  },

  async runEscalationEngine() {
    try {
      const res = await api.post("/api/deadlines/check-escalations", {});
      alert(`Statutory Escalation Engine: Auto-escalated ${res.escalated_count} overdue deadlines.`);
      await this.loadDeadlines();
    } catch (err) {
      alert("Failed to run escalation engine: " + err.message);
    }
  },

  renderTable(deadlines) {
    const tbody = document.getElementById("deadlines-tbody");
    if (!tbody) return;

    if (!deadlines || deadlines.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:#888;">No statutory compliance items found.</td></tr>`;
      return;
    }

    tbody.innerHTML = deadlines.map(item => {
      const daysLeft = item.days_left;
      let statusChip = `<span class="chip chip--due">Pending</span>`;
      if (item.status === "overdue" || daysLeft < 0) {
        statusChip = `<span class="chip chip--overdue">Overdue (${Math.abs(daysLeft)}d)</span>`;
      } else if (item.status === "filed") {
        statusChip = `<span class="chip chip--done">Filed ✓</span>`;
      } else if (item.status === "in_prep") {
        statusChip = `<span class="chip chip--review">In Prep</span>`;
      }

      return `
        <tr>
          <td><strong>${item.client_name}</strong></td>
          <td>${item.obligation}</td>
          <td>${item.period || 'FY 2025-26'}</td>
          <td>${item.due_date ? item.due_date.slice(0, 10) : ''}</td>
          <td>${item.owner || 'Unassigned'}</td>
          <td>${statusChip}</td>
        </tr>
      `;
    }).join("");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  DeadlinesModule.init();
});
