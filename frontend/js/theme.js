/* ===== Theme Toggle ===== */
function initTheme() {
  const saved = localStorage.getItem("ld_theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("ld_theme", next);
}

initTheme();
