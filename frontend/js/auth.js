/* ===== Auth Page Logic ===== */
document.addEventListener("DOMContentLoaded", () => {
  // Redirect if already authenticated
  if (api.isAuthenticated()) {
    window.location.href = "/dashboard";
    return;
  }

  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const errEl = document.getElementById("auth-error");
      errEl.classList.remove("visible");

      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      try {
        const data = await api.post("/api/auth/login", { email, password });
        api.setToken(data.access_token);
        api.setUser(data.user);
        window.location.href = "/dashboard";
      } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.add("visible");
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const errEl = document.getElementById("auth-error");
      errEl.classList.remove("visible");

      const name = document.getElementById("name").value;
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;
      const firm_name = document.getElementById("firm_name").value;
      const role = document.getElementById("role").value;

      try {
        const data = await api.post("/api/auth/register", { name, email, password, firm_name, role });
        api.setToken(data.access_token);
        api.setUser(data.user);
        window.location.href = "/dashboard";
      } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.add("visible");
      }
    });
  }
});
