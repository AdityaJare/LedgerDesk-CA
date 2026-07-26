/* ===== Dashboard Feature Module ===== */
const DashboardModule = {
  async init() {
    try {
      await this.loadSummary();
    } catch (err) {
      console.warn("Dashboard summary API load warning:", err.message);
    }
  },

  async loadSummary() {
    try {
      const summary = await api.get("/api/dashboard/summary");
      this.renderSummary(summary);
    } catch (err) {
      console.error("Failed to load dashboard metrics:", err);
    }
  },

  renderSummary(data) {
    if (!data) return;

    const elemOverdue = document.getElementById("metric-overdue-count");
    const elemExceptions = document.getElementById("metric-exceptions-count");
    const elemDocs = document.getElementById("metric-docs-count");
    const elemDrafts = document.getElementById("metric-drafts-count");
    const elemReviews = document.getElementById("metric-reviews-count");

    if (elemOverdue) elemOverdue.textContent = data.overdue_deadlines || 0;
    if (elemExceptions) elemExceptions.textContent = data.open_exceptions || 0;
    if (elemDocs) elemDocs.textContent = data.awaiting_documents || 0;
    if (elemDrafts) elemDrafts.textContent = data.drafts_in_progress || 0;
    if (elemReviews) elemReviews.textContent = data.pending_reviews || 0;
  }
};

document.addEventListener("DOMContentLoaded", () => {
  DashboardModule.init();
});
