/* ===== API Client for LedgerDesk CA ===== */
const API_BASE = (window.location.protocol === 'file:' || !window.location.port || window.location.origin === 'null') 
  ? "http://localhost:8000" 
  : window.location.origin;

const api = {
  getToken() {
    return localStorage.getItem("ld_token");
  },
  setToken(token) {
    localStorage.setItem("ld_token", token);
  },
  setUser(user) {
    localStorage.setItem("ld_user", JSON.stringify(user));
  },
  getUser() {
    const u = localStorage.getItem("ld_user");
    return u ? JSON.parse(u) : null;
  },
  logout() {
    localStorage.removeItem("ld_token");
    localStorage.removeItem("ld_user");
    window.location.href = "/login";
  },
  isAuthenticated() {
    return !!this.getToken();
  },

  async request(method, path, body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = this.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, opts);

    if (res.status === 401) {
      this.logout();
      throw new Error("Session expired. Please log in again.");
    }

    if (res.status === 204) return null;

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Request failed");
    }
    return data;
  },

  async upload(path, formData) {
    const headers = {};
    const token = this.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers,
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");
    return data;
  },

  get(path) { return this.request("GET", path); },
  post(path, body) { return this.request("POST", path, body); },
  put(path, body) { return this.request("PUT", path, body); },
  del(path) { return this.request("DELETE", path); },
};
