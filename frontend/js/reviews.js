/* ===== Review Pipeline Feature Module ===== */
const ReviewsModule = {
  async init() {
    await this.loadReviews();
  },

  async loadReviews() {
    try {
      const list = await api.get("/api/reviews");
      this.renderReviews(list);
    } catch (err) {
      console.error("Failed to load reviews:", err);
    }
  },

  async updateReviewStatus(reviewId, newStatus) {
    try {
      await api.put(`/api/reviews/${reviewId}`, { status: newStatus });
      alert(`Review status updated to: ${newStatus}`);
      await this.loadReviews();
    } catch (err) {
      alert("Failed to update review: " + err.message);
    }
  },

  async addReviewComment(reviewId) {
    const comment = prompt("Enter review comment:");
    if (!comment) return;
    try {
      await api.put(`/api/reviews/${reviewId}`, { new_comment: comment });
      alert("Comment added successfully.");
      await this.loadReviews();
    } catch (err) {
      alert("Failed to add comment: " + err.message);
    }
  },

  renderReviews(list) {
    const container = document.getElementById("reviews-list-container");
    if (!container) return;

    if (!list || list.length === 0) {
      container.innerHTML = `<div class="empty-state">No items pending review.</div>`;
      return;
    }

    container.innerHTML = list.map(item => {
      let statusChip = `<span class="chip chip--review">${item.status}</span>`;
      if (item.status === "Approved") statusChip = `<span class="chip chip--done">Approved ✓</span>`;
      else if (item.status === "Returned") statusChip = `<span class="chip chip--overdue">Returned</span>`;
      else if (item.status === "Exported") statusChip = `<span class="chip chip--done">Exported ✓</span>`;

      let riskColor = "var(--text-muted)";
      if (item.risk_flag === "High") riskColor = "var(--error)";
      else if (item.risk_flag === "Medium") riskColor = "var(--warning)";

      const actionButtons = [];
      if (item.status === "Awaiting manager") {
        actionButtons.push(`<button class="btn btn--primary btn--sm" onclick="ReviewsModule.updateReviewStatus('${item.id}','Awaiting partner')">Approve → Partner</button>`);
        actionButtons.push(`<button class="btn btn--secondary btn--sm" onclick="ReviewsModule.updateReviewStatus('${item.id}','Returned')">Return with Comments</button>`);
      } else if (item.status === "Awaiting partner") {
        actionButtons.push(`<button class="btn btn--primary btn--sm" onclick="ReviewsModule.updateReviewStatus('${item.id}','Approved')">Partner Approve ✓</button>`);
        actionButtons.push(`<button class="btn btn--secondary btn--sm" onclick="ReviewsModule.updateReviewStatus('${item.id}','Returned')">Return with Comments</button>`);
      }
      actionButtons.push(`<button class="btn btn--ghost btn--sm" onclick="ReviewsModule.addReviewComment('${item.id}')">Add Comment</button>`);

      return `
        <div class="review-card" style="background:var(--surface); border:1px solid var(--border); padding:16px; border-radius:8px; margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div>
              <h4 style="margin:0; font-size:15px; font-weight:600;">${item.item_name}</h4>
              <div style="font-size:12px; color:var(--text-muted);">${item.client_name} — ${item.work_item_type} — ${item.version || ''}</div>
            </div>
            ${statusChip}
          </div>
          <div style="font-size:13px; color:var(--text-secondary); margin-bottom:8px;">
            <strong>Submitted By:</strong> ${item.submitted_by} |
            <strong>Reviewer:</strong> ${item.reviewer} |
            <strong>Risk:</strong> <span style="color:${riskColor}; font-weight:600;">${item.risk_flag}</span>
          </div>
          <div style="display:flex; gap:8px; flex-wrap:wrap;">${actionButtons.join("")}</div>
        </div>
      `;
    }).join("");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  ReviewsModule.init();
});
