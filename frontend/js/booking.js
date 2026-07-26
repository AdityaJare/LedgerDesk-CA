/* ===== Demo Booking Modal Feature Module ===== */
const BookingModule = {
  init() {
    this.createModal();
    this.bindButtons();
  },

  createModal() {
    if (document.getElementById("demo-booking-modal")) return;

    const overlay = document.createElement("div");
    overlay.id = "demo-booking-modal";
    overlay.style.cssText = `
      display:none; position:fixed; inset:0; z-index:9999; 
      background:rgba(0,0,0,0.5); backdrop-filter:blur(4px);
      align-items:center; justify-content:center;
    `;

    overlay.innerHTML = `
      <div id="demo-booking-card" style="
        background:var(--surface,#fff); border:1px solid var(--border,#e0e0e0);
        border-radius:14px; padding:36px; width:90%; max-width:480px;
        box-shadow:0 16px 64px rgba(0,0,0,0.18); position:relative;
        font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
      ">
        <button id="demo-modal-close" style="
          position:absolute; top:14px; right:14px; background:none; border:none;
          font-size:22px; cursor:pointer; color:var(--text-muted,#888); line-height:1;
        ">&times;</button>

        <h3 style="margin:0 0 6px 0; font-size:20px; font-weight:700; color:var(--text,#111);">
          Book a Workflow Demo
        </h3>
        <p style="margin:0 0 24px 0; font-size:13px; color:var(--text-secondary,#666); line-height:1.5;">
          See how LedgerDesk structures your firm's statutory workflow — from deadline to signed-off evidence.
        </p>

        <form id="demo-booking-form" style="display:flex; flex-direction:column; gap:14px;">
          <div>
            <label style="font-size:12px; font-weight:600; color:var(--text-secondary,#666); display:block; margin-bottom:4px;">Full Name *</label>
            <input type="text" id="booking-name" required placeholder="e.g. Rajesh Sharma" style="
              width:100%; padding:10px 12px; border:1px solid var(--border,#ddd); border-radius:8px;
              font-size:14px; background:var(--bg,#f7f7f5); color:var(--text,#111); outline:none; box-sizing:border-box;
            ">
          </div>
          <div>
            <label style="font-size:12px; font-weight:600; color:var(--text-secondary,#666); display:block; margin-bottom:4px;">Email Address *</label>
            <input type="email" id="booking-email" required placeholder="e.g. rajesh@sharmaca.com" style="
              width:100%; padding:10px 12px; border:1px solid var(--border,#ddd); border-radius:8px;
              font-size:14px; background:var(--bg,#f7f7f5); color:var(--text,#111); outline:none; box-sizing:border-box;
            ">
          </div>
          <div>
            <label style="font-size:12px; font-weight:600; color:var(--text-secondary,#666); display:block; margin-bottom:4px;">Firm Name *</label>
            <input type="text" id="booking-firm" required placeholder="e.g. Sharma & Associates CAs" style="
              width:100%; padding:10px 12px; border:1px solid var(--border,#ddd); border-radius:8px;
              font-size:14px; background:var(--bg,#f7f7f5); color:var(--text,#111); outline:none; box-sizing:border-box;
            ">
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div>
              <label style="font-size:12px; font-weight:600; color:var(--text-secondary,#666); display:block; margin-bottom:4px;">Phone</label>
              <input type="tel" id="booking-phone" placeholder="+91 98123 45678" style="
                width:100%; padding:10px 12px; border:1px solid var(--border,#ddd); border-radius:8px;
                font-size:14px; background:var(--bg,#f7f7f5); color:var(--text,#111); outline:none; box-sizing:border-box;
              ">
            </div>
            <div>
              <label style="font-size:12px; font-weight:600; color:var(--text-secondary,#666); display:block; margin-bottom:4px;">Team Size</label>
              <select id="booking-teamsize" style="
                width:100%; padding:10px 12px; border:1px solid var(--border,#ddd); border-radius:8px;
                font-size:14px; background:var(--bg,#f7f7f5); color:var(--text,#111); outline:none; box-sizing:border-box;
              ">
                <option value="1-5">1–5 (Solo / Small)</option>
                <option value="5-15">5–15 (Mid-size)</option>
                <option value="15-30" selected>15–30 (Large firm)</option>
                <option value="30+">30+ (Multi-branch)</option>
              </select>
            </div>
          </div>
          <button type="submit" id="booking-submit-btn" style="
            padding:12px; border:none; border-radius:8px; font-size:15px; font-weight:600;
            background:var(--teal,#0d8a72); color:#fff; cursor:pointer; margin-top:6px;
            transition: background 0.2s;
          ">Submit Demo Request</button>
        </form>

        <div id="booking-success-msg" style="display:none; text-align:center; padding:20px 0;">
          <div style="font-size:32px; margin-bottom:12px;">✅</div>
          <h4 style="margin:0 0 8px 0; font-size:18px; color:var(--text,#111);">Demo Request Received!</h4>
          <p style="font-size:13px; color:var(--text-secondary,#666);">Our team will reach out within 24 hours to schedule your personalized walkthrough.</p>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    // Close handlers
    document.getElementById("demo-modal-close").addEventListener("click", () => this.closeModal());
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) this.closeModal();
    });

    // Form submission
    document.getElementById("demo-booking-form").addEventListener("submit", (e) => {
      e.preventDefault();
      this.submitBooking();
    });
  },

  bindButtons() {
    // Bind all "Book a workflow demo" links/buttons
    document.querySelectorAll('a[href="#cta"], a[href="#"], .btn--primary').forEach(btn => {
      const text = btn.textContent.trim().toLowerCase();
      if (text.includes("book a workflow demo") || text.includes("discuss pricing")) {
        btn.addEventListener("click", (e) => {
          e.preventDefault();
          this.openModal();
        });
      }
    });
  },

  openModal() {
    const modal = document.getElementById("demo-booking-modal");
    if (modal) {
      modal.style.display = "flex";
      document.getElementById("demo-booking-form").style.display = "flex";
      document.getElementById("booking-success-msg").style.display = "none";
    }
  },

  closeModal() {
    const modal = document.getElementById("demo-booking-modal");
    if (modal) modal.style.display = "none";
  },

  async submitBooking() {
    const payload = {
      full_name: document.getElementById("booking-name").value,
      email: document.getElementById("booking-email").value,
      firm_name: document.getElementById("booking-firm").value,
      phone: document.getElementById("booking-phone").value || "",
      team_size: document.getElementById("booking-teamsize").value
    };

    const btn = document.getElementById("booking-submit-btn");
    btn.textContent = "Submitting...";
    btn.disabled = true;

    try {
      await api.post("/api/bookings", payload);
      document.getElementById("demo-booking-form").style.display = "none";
      document.getElementById("booking-success-msg").style.display = "block";
    } catch (err) {
      alert("Submission failed: " + err.message);
      btn.textContent = "Submit Demo Request";
      btn.disabled = false;
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  BookingModule.init();
});
